import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://127.0.0.1:8002/api/products')

def get_user_id(request):
    # Retrieve user_id from headers or query parameters
    user_id = request.headers.get('X-User-Id') or request.query_params.get('user_id')
    if user_id:
        try:
            return int(user_id)
        except ValueError:
            return None
    return None

def get_or_create_cart(user_id):
    cart, created = Cart.objects.get_or_create(user_id=user_id)
    return cart

@api_view(['GET', 'DELETE'])
def cart_view(request):
    user_id = get_user_id(request)
    if not user_id:
        return Response({'error': 'Unauthorized: Missing user_id'}, status=status.HTTP_401_UNAUTHORIZED)
        
    cart = get_or_create_cart(user_id)
    
    if request.method == 'GET':
        items = CartItem.objects.filter(cart=cart)
        serialized_items = []
        total_price = 0.0
        
        for item in items:
            item_data = CartItemSerializer(item).data
            # Call product service to get product details
            try:
                res = requests.get(f"{PRODUCT_SERVICE_URL}/{item.product_id}", timeout=10)
                if res.status_code == 200:
                    prod_info = res.json()
                    item_data['product_name'] = prod_info.get('name')
                    item_data['price'] = float(prod_info.get('price', 0))
                    item_data['subtotal'] = item_data['price'] * item.quantity
                    total_price += item_data['subtotal']
                else:
                    item_data['product_name'] = "Unknown Product"
                    item_data['price'] = 0.0
                    item_data['subtotal'] = 0.0
            except requests.exceptions.RequestException:
                item_data['product_name'] = "Product Service Offline"
                item_data['price'] = 0.0
                item_data['subtotal'] = 0.0
                
            serialized_items.append(item_data)
            
        return Response({
            'cart_id': cart.id,
            'user_id': cart.user_id,
            'items': serialized_items,
            'total_price': total_price,
            'created_at': cart.created_at
        })
        
    elif request.method == 'DELETE':
        CartItem.objects.filter(cart=cart).delete()
        return Response({'message': 'Cart cleared successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def add_cart_item_view(request):
    user_id = get_user_id(request)
    if not user_id:
        return Response({'error': 'Unauthorized: Missing user_id'}, status=status.HTTP_401_UNAUTHORIZED)
        
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    if not product_id:
        return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response({'error': 'quantity must be positive'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Verify product and stock in product-service
    try:
        res = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}", timeout=10)
        if res.status_code == 404:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        elif res.status_code == 200:
            prod_info = res.json()
            available_stock = prod_info.get('stock', 0)
            if available_stock < quantity:
                return Response({'error': f"Insufficient stock. Available: {available_stock}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Failed to verify product details'}, status=status.HTTP_502_BAD_GATEWAY)
    except requests.exceptions.RequestException:
        return Response({'error': 'Product Service is unreachable'}, status=status.HTTP_502_BAD_GATEWAY)
        
    cart = get_or_create_cart(user_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
    
    if not created:
        # Check stock again for new total quantity
        new_quantity = cart_item.quantity + quantity
        try:
            res = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}", timeout=10)
            if res.status_code == 200:
                available_stock = res.json().get('stock', 0)
                if available_stock < new_quantity:
                    return Response({'error': f"Insufficient stock to add more. Available: {available_stock}, in cart: {cart_item.quantity}"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException:
            pass
            
        cart_item.quantity = new_quantity
    else:
        cart_item.quantity = quantity
        
    cart_item.save()
    return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
def cart_item_detail_view(request, product_id):
    user_id = get_user_id(request)
    if not user_id:
        return Response({'error': 'Unauthorized: Missing user_id'}, status=status.HTTP_401_UNAUTHORIZED)
        
    cart = get_or_create_cart(user_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'PUT':
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({'error': 'quantity is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            quantity = int(quantity)
        except ValueError:
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)
            
        if quantity <= 0:
            cart_item.delete()
            return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
            
        # Verify product and stock in product-service
        try:
            res = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}", timeout=10)
            if res.status_code == 200:
                prod_info = res.json()
                available_stock = prod_info.get('stock', 0)
                if available_stock < quantity:
                    return Response({'error': f"Insufficient stock. Available: {available_stock}"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException:
            return Response({'error': 'Product Service is unreachable'}, status=status.HTTP_502_BAD_GATEWAY)
            
        cart_item.quantity = quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)
        
    elif request.method == 'DELETE':
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def checkout_preview_view(request):
    user_id = get_user_id(request)
    if not user_id:
        return Response({'error': 'Unauthorized: Missing user_id'}, status=status.HTTP_401_UNAUTHORIZED)
        
    cart = get_or_create_cart(user_id)
    items = CartItem.objects.filter(cart=cart)
    
    serialized_items = []
    total_price = 0.0
    
    for item in items:
        item_data = CartItemSerializer(item).data
        try:
            res = requests.get(f"{PRODUCT_SERVICE_URL}/{item.product_id}", timeout=10)
            if res.status_code == 200:
                prod_info = res.json()
                item_data['product_name'] = prod_info.get('name')
                item_data['price'] = float(prod_info.get('price', 0))
                item_data['subtotal'] = item_data['price'] * item.quantity
                total_price += item_data['subtotal']
            else:
                item_data['product_name'] = "Unknown Product"
                item_data['price'] = 0.0
                item_data['subtotal'] = 0.0
        except requests.exceptions.RequestException:
            item_data['product_name'] = "Product Service Offline"
            item_data['price'] = 0.0
            item_data['subtotal'] = 0.0
            
        serialized_items.append(item_data)
        
    return Response({
        'user_id': user_id,
        'items': serialized_items,
        'total_price': total_price
    })
