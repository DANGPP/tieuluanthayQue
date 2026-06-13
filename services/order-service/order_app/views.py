import os
import requests
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer

USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://127.0.0.1:8001/api/users')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://127.0.0.1:8002/api/products')
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://127.0.0.1:8003/api/cart')

def get_user_id(request):
    user_id = request.headers.get('X-User-Id') or request.query_params.get('user_id')
    if user_id:
        try:
            return int(user_id)
        except ValueError:
            return None
    return None

def get_role(request):
    return request.headers.get('X-User-Role') or request.query_params.get('role')

def has_role(request, *roles):
    return get_role(request) in roles

def apply_order_status(order, status_val, reason=None):
    if status_val not in dict(Order.STATUS_CHOICES):
        return False
    order.status = status_val
    if status_val == 'confirmed' and not order.confirmed_at:
        order.confirmed_at = timezone.now()
    if status_val == 'processing' and not order.processing_at:
        order.processing_at = timezone.now()
    if status_val == 'cancelled' and reason:
        order.cancelled_reason = reason
    order.save()
    return True

@api_view(['GET', 'POST'])
def order_list_view(request):
    user_id = get_user_id(request)
    if not user_id:
        return Response({'error': 'Unauthorized: Missing user_id'}, status=status.HTTP_401_UNAUTHORIZED)
        
    if request.method == 'GET':
        orders = Order.objects.filter(user_id=user_id).order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)
        
    elif request.method == 'POST':
        address_id = request.data.get('address_id')
        if not address_id:
            return Response({'error': 'address_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        headers = {'X-User-Id': str(user_id)}
        
        # 1. Fetch address details from User Service
        address_str = ""
        try:
            addr_res = requests.get(f"{USER_SERVICE_URL}/me/addresses", headers=headers, timeout=10)
            if addr_res.status_code == 200:
                addresses = addr_res.json()
                # Find matching address_id
                selected_addr = next((a for a in addresses if a['id'] == address_id), None)
                if not selected_addr:
                    return Response({'error': 'Selected address not found'}, status=status.HTTP_404_NOT_FOUND)
                address_str = f"Name: {selected_addr['full_name']}, Phone: {selected_addr['phone']}, Address: {selected_addr['address_line']}"
            else:
                return Response({'error': 'Failed to retrieve addresses from User Service'}, status=status.HTTP_502_BAD_GATEWAY)
        except requests.exceptions.RequestException:
            return Response({'error': 'User Service is unreachable'}, status=status.HTTP_502_BAD_GATEWAY)
            
        # 2. Fetch Cart Items from Cart Service checkout preview
        try:
            cart_res = requests.get(f"{CART_SERVICE_URL}/checkout-preview", headers=headers, timeout=10)
            if cart_res.status_code == 200:
                cart_data = cart_res.json()
                cart_items = cart_data.get('items', [])
                total_price = cart_data.get('total_price', 0.0)
                if not cart_items:
                    return Response({'error': 'Your cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Failed to retrieve cart items'}, status=status.HTTP_502_BAD_GATEWAY)
        except requests.exceptions.RequestException:
            return Response({'error': 'Cart Service is unreachable'}, status=status.HTTP_502_BAD_GATEWAY)
            
        # 3. Check and deduct stocks from Product Service
        products_to_update = []
        for item in cart_items:
            prod_id = item['product_id']
            qty = item['quantity']
            try:
                prod_res = requests.get(f"{PRODUCT_SERVICE_URL}/{prod_id}", timeout=10)
                if prod_res.status_code == 200:
                    prod_info = prod_res.json()
                    current_stock = prod_info.get('stock', 0)
                    if current_stock < qty:
                        return Response({'error': f"Product {prod_info.get('name')} is out of stock. Needed: {qty}, Available: {current_stock}"}, status=status.HTTP_400_BAD_REQUEST)
                    products_to_update.append({
                        'id': prod_id,
                        'new_stock': current_stock - qty,
                        'price': float(prod_info.get('price'))
                    })
                else:
                    return Response({'error': f"Product ID {prod_id} not found in catalog"}, status=status.HTTP_404_NOT_FOUND)
            except requests.exceptions.RequestException:
                return Response({'error': 'Product Service is unreachable'}, status=status.HTTP_502_BAD_GATEWAY)
                
        # 4. Create Order and OrderItems
        order = Order.objects.create(
            user_id=user_id,
            total_price=total_price,
            status='pending',
            address=address_str
        )
        
        for p_update in products_to_update:
            OrderItem.objects.create(
                order=order,
                product_id=p_update['id'],
                quantity=next(item['quantity'] for item in cart_items if item['product_id'] == p_update['id']),
                price=p_update['price']
            )
            # Deduct stock in Product Service
            try:
                requests.put(f"{PRODUCT_SERVICE_URL}/{p_update['id']}", json={'stock': p_update['new_stock']}, timeout=10)
            except requests.exceptions.RequestException:
                # In real production, we would use Saga pattern or Outbox pattern to guarantee eventual consistency.
                pass
                
        # 5. Clear Cart in Cart Service
        try:
            requests.delete(f"{CART_SERVICE_URL}", headers=headers, timeout=10)
        except requests.exceptions.RequestException:
            pass
            
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT'])
def order_detail_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        user_id = get_user_id(request)
        if not user_id or (order.user_id != user_id):
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(OrderSerializer(order).data)
        
    elif request.method == 'PUT':
        # Let's allow updating order status (used by other services like Payment)
        status_val = request.data.get('status')
        if not status_val or not apply_order_status(order, status_val, request.data.get('cancelled_reason')):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)

@api_view(['POST'])
def cancel_order_view(request, order_id):
    user_id = get_user_id(request)
    if not user_id:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
    try:
        order = Order.objects.get(id=order_id, user_id=user_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if order.status not in ['pending', 'processing']:
        return Response({'error': f"Cannot cancel order with status '{order.status}'"}, status=status.HTTP_400_BAD_REQUEST)
        
    # Restore stocks in Product Service
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        try:
            res = requests.get(f"{PRODUCT_SERVICE_URL}/{item.product_id}", timeout=10)
            if res.status_code == 200:
                current_stock = res.json().get('stock', 0)
                requests.put(f"{PRODUCT_SERVICE_URL}/{item.product_id}", json={'stock': current_stock + item.quantity}, timeout=10)
        except requests.exceptions.RequestException:
            pass
            
    order.status = 'cancelled'
    order.save()
    return Response(OrderSerializer(order).data)

@api_view(['GET'])
def admin_order_list_view(request):
    if not has_role(request, 'admin', 'staff'):
        return Response({'error': 'Admin or staff role required'}, status=status.HTTP_403_FORBIDDEN)

    orders = Order.objects.all().order_by('-created_at')
    status_filter = request.query_params.get('status')
    user_id = request.query_params.get('user_id')
    staff_id = request.query_params.get('assigned_staff_id')
    if status_filter:
        orders = orders.filter(status=status_filter)
    if user_id:
        orders = orders.filter(user_id=user_id)
    if staff_id:
        orders = orders.filter(assigned_staff_id=staff_id)
    return Response(OrderSerializer(orders, many=True).data)

@api_view(['GET'])
def admin_order_detail_view(request, order_id):
    if not has_role(request, 'admin', 'staff'):
        return Response({'error': 'Admin or staff role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = Order.objects.get(id=order_id)
        return Response(OrderSerializer(order).data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def admin_order_status_view(request, order_id):
    if not has_role(request, 'admin', 'staff'):
        return Response({'error': 'Admin or staff role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    status_val = request.data.get('status')
    if not status_val or not apply_order_status(order, status_val, request.data.get('cancelled_reason')):
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(OrderSerializer(order).data)

@api_view(['PUT'])
def admin_assign_staff_view(request, order_id):
    if not has_role(request, 'admin'):
        return Response({'error': 'Admin role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    staff_id = request.data.get('staff_id') or request.data.get('assigned_staff_id')
    if not staff_id:
        return Response({'error': 'staff_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        order.assigned_staff_id = int(staff_id)
    except (TypeError, ValueError):
        return Response({'error': 'staff_id must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
    order.save(update_fields=['assigned_staff_id', 'updated_at'])
    return Response(OrderSerializer(order).data)

@api_view(['GET'])
def staff_order_list_view(request):
    if not has_role(request, 'staff', 'admin'):
        return Response({'error': 'Staff role required'}, status=status.HTTP_403_FORBIDDEN)
    staff_id = get_user_id(request)
    orders = Order.objects.all().order_by('-created_at')
    if staff_id and get_role(request) == 'staff':
        orders = orders.filter(Q(assigned_staff_id=staff_id) | Q(assigned_staff_id__isnull=True))
    return Response(OrderSerializer(orders, many=True).data)

@api_view(['PUT'])
def staff_confirm_order_view(request, order_id):
    if not has_role(request, 'staff', 'admin'):
        return Response({'error': 'Staff role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    apply_order_status(order, 'confirmed')
    return Response(OrderSerializer(order).data)

@api_view(['PUT'])
def staff_ready_to_ship_view(request, order_id):
    if not has_role(request, 'staff', 'admin'):
        return Response({'error': 'Staff role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    apply_order_status(order, 'ready_to_ship')
    return Response(OrderSerializer(order).data)
