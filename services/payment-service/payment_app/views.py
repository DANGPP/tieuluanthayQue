import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from .serializers import PaymentSerializer

ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://127.0.0.1:8004/api/orders')
SHIPPING_SERVICE_URL = os.getenv('SHIPPING_SERVICE_URL', 'http://127.0.0.1:8006/api/shipments')

def get_role(request):
    return request.headers.get('X-User-Role') or request.query_params.get('role')

def has_role(request, *roles):
    return get_role(request) in roles

@api_view(['POST'])
def create_payment_view(request):
    order_id = request.data.get('order_id')
    amount = request.data.get('amount')
    method = request.data.get('method', 'card')
    
    if not order_id or not amount:
        return Response({'error': 'order_id and amount are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    payment = Payment.objects.create(
        order_id=order_id,
        amount=amount,
        method=method,
        status='pending'
    )
    return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def confirm_payment_view(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment intent not found'}, status=status.HTTP_404_NOT_FOUND)
        
    transaction_id = request.data.get('transaction_id')
    status_val = request.data.get('status')  # 'success' or 'failed'
    
    if not transaction_id or not status_val:
        return Response({'error': 'transaction_id and status are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    if status_val not in ['success', 'failed']:
        return Response({'error': 'status must be success or failed'}, status=status.HTTP_400_BAD_REQUEST)
        
    payment.transaction_id = transaction_id
    payment.status = status_val
    payment.save()
    
    # Notify Order Service
    order_status = 'processing' if status_val == 'success' else 'cancelled'
    user_id = request.headers.get('X-User-Id') or request.query_params.get('user_id')
    headers = {'X-User-Id': str(user_id)} if user_id else {}
    
    try:
        # Update Order Status in Order Service
        order_update_res = requests.put(
            f"{ORDER_SERVICE_URL}/{payment.order_id}", 
            json={'status': order_status}, 
            timeout=10
        )
        
        # If success, trigger Shipment Service
        if status_val == 'success':
            # Get order details to retrieve address
            order_res = requests.get(f"{ORDER_SERVICE_URL}/{payment.order_id}", headers=headers, timeout=10)
            if order_res.status_code == 200:
                order_data = order_res.json()
                address = order_data.get('address', 'Default Address')
                
                # Create shipment
                ship_payload = {
                    'order_id': payment.order_id,
                    'address': address
                }
                requests.post(SHIPPING_SERVICE_URL, json=ship_payload, timeout=10)
    except requests.exceptions.RequestException:
        # In real projects, retry queue / outbox pattern handles this.
        pass
        
    return Response(PaymentSerializer(payment).data)

@api_view(['GET'])
def admin_payment_list_view(request):
    if not has_role(request, 'admin', 'staff'):
        return Response({'error': 'Admin or staff role required'}, status=status.HTTP_403_FORBIDDEN)
    payments = Payment.objects.all().order_by('-created_at')
    status_filter = request.query_params.get('status')
    order_id = request.query_params.get('order_id')
    if status_filter:
        payments = payments.filter(status=status_filter)
    if order_id:
        payments = payments.filter(order_id=order_id)
    return Response(PaymentSerializer(payments, many=True).data)

@api_view(['GET', 'PUT'])
def admin_payment_detail_view(request, payment_id):
    if not has_role(request, 'admin', 'staff'):
        return Response({'error': 'Admin or staff role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(PaymentSerializer(payment).data)

    status_val = request.data.get('status')
    if status_val not in ['pending', 'success', 'failed']:
        return Response({'error': 'Invalid payment status'}, status=status.HTTP_400_BAD_REQUEST)
    payment.status = status_val
    if request.data.get('transaction_id'):
        payment.transaction_id = request.data.get('transaction_id')
    payment.save()
    return Response(PaymentSerializer(payment).data)
