import requests
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer

SERVICE_URLS = {
    'user': os.getenv('USER_API_URL', 'http://127.0.0.1:8001/api'),
    'product': os.getenv('PRODUCT_API_URL', 'http://127.0.0.1:8002/api'),
    'cart': os.getenv('CART_API_URL', 'http://127.0.0.1:8003/api'),
    'order': os.getenv('ORDER_API_URL', 'http://127.0.0.1:8004/api'),
    'payment': os.getenv('PAYMENT_API_URL', 'http://127.0.0.1:8005/api'),
    'shipping': os.getenv('SHIPPING_API_URL', 'http://127.0.0.1:8006/api'),
    'ai': os.getenv('AI_API_URL', 'http://127.0.0.1:8007/api'),
}

SERVICE_HEALTH_URLS = {
    'user': os.getenv('USER_HEALTH_URL', 'http://127.0.0.1:8001/admin/'),
    'product': os.getenv('PRODUCT_HEALTH_URL', 'http://127.0.0.1:8002/admin/'),
    'cart': os.getenv('CART_HEALTH_URL', 'http://127.0.0.1:8003/admin/'),
    'order': os.getenv('ORDER_HEALTH_URL', 'http://127.0.0.1:8004/admin/'),
    'payment': os.getenv('PAYMENT_HEALTH_URL', 'http://127.0.0.1:8005/admin/'),
    'shipping': os.getenv('SHIPPING_HEALTH_URL', 'http://127.0.0.1:8006/admin/'),
    'ai': os.getenv('AI_HEALTH_URL', 'http://127.0.0.1:8007/admin/'),
    'gateway': os.getenv('GATEWAY_HEALTH_URL', 'http://127.0.0.1:8008/admin/'),
}


def index_view(request):
    return render(request, 'gateway_app/index.html')


def _json_body(request):
    if not request.body:
        return None
    try:
        import json
        return json.loads(request.body.decode('utf-8'))
    except ValueError:
        return None


def _proxy(service, path, method='GET', data=None, params=None, user_id=None, role=None):
    headers = {}
    if user_id:
        headers['X-User-Id'] = str(user_id)
    if role:
        headers['X-User-Role'] = str(role)

    try:
        response = requests.request(
            method=method,
            url=f"{SERVICE_URLS[service]}{path}",
            json=data,
            params=params,
            headers=headers,
            timeout=15,
        )
    except requests.exceptions.RequestException as exc:
        return JsonResponse(
            {'error': f'{service}-service is unreachable', 'detail': str(exc)},
            status=502,
        )

    if response.status_code == 204:
        return JsonResponse({'message': 'OK'}, status=200)

    try:
        payload = response.json()
    except ValueError:
        payload = {'raw': response.text}
    return JsonResponse(payload, status=response.status_code, safe=not isinstance(payload, list))


@csrf_exempt
def ui_status_view(request):
    services = []
    for name, url in SERVICE_HEALTH_URLS.items():
        try:
            response = requests.get(url, timeout=3, allow_redirects=False)
            online = response.status_code < 500
            services.append({'name': name, 'online': online, 'status': response.status_code})
        except requests.exceptions.RequestException:
            services.append({'name': name, 'online': False, 'status': None})
    return JsonResponse({'services': services})


@csrf_exempt
def ui_login_view(request):
    return _proxy('user', '/auth/login', method='POST', data=_json_body(request))


@csrf_exempt
def ui_products_view(request):
    return _proxy('product', '/products', params=request.GET.dict())


@csrf_exempt
def ui_addresses_view(request):
    return _proxy('user', '/users/me/addresses', params=request.GET.dict(), user_id=request.GET.get('user_id'), role=request.GET.get('role'))


@csrf_exempt
def ui_cart_view(request):
    user_id = request.GET.get('user_id')
    if request.method == 'DELETE':
        return _proxy('cart', '/cart', method='DELETE', user_id=user_id, role=request.GET.get('role'))
    return _proxy('cart', '/cart', user_id=user_id, role=request.GET.get('role'))


@csrf_exempt
def ui_cart_items_view(request, product_id=None):
    data = _json_body(request)
    user_id = request.GET.get('user_id') or (data or {}).get('user_id')
    role = request.GET.get('role') or (data or {}).get('role')

    if request.method == 'POST':
        return _proxy('cart', '/cart/items', method='POST', data=data, user_id=user_id, role=role)
    if request.method == 'PUT' and product_id:
        return _proxy('cart', f'/cart/items/{product_id}', method='PUT', data=data, user_id=user_id, role=role)
    if request.method == 'DELETE' and product_id:
        return _proxy('cart', f'/cart/items/{product_id}', method='DELETE', user_id=user_id, role=role)
    return JsonResponse({'error': 'Unsupported cart operation'}, status=400)


@csrf_exempt
def ui_checkout_preview_view(request):
    return _proxy('cart', '/cart/checkout-preview', user_id=request.GET.get('user_id'), role=request.GET.get('role'))


@csrf_exempt
def ui_orders_view(request):
    data = _json_body(request)
    user_id = request.GET.get('user_id') or (data or {}).get('user_id')
    role = request.GET.get('role') or (data or {}).get('role')
    if request.method == 'POST':
        return _proxy('order', '/orders', method='POST', data=data, user_id=user_id, role=role)
    return _proxy('order', '/orders', user_id=user_id, role=role)


@csrf_exempt
def ui_order_detail_view(request, order_id):
    return _proxy('order', f'/orders/{order_id}', user_id=request.GET.get('user_id'), role=request.GET.get('role'))


@csrf_exempt
def ui_payments_view(request):
    return _proxy('payment', '/payments', method='POST', data=_json_body(request))


@csrf_exempt
def ui_payment_confirm_view(request, payment_id):
    data = _json_body(request)
    return _proxy(
        'payment',
        f'/payments/{payment_id}/confirm',
        method='POST',
        data=data,
        user_id=(data or {}).get('user_id'),
        role=(data or {}).get('role'),
    )


@csrf_exempt
def ui_shipment_by_order_view(request, order_id):
    return _proxy('shipping', f'/shipments/order/{order_id}')


@csrf_exempt
def ui_shipment_update_view(request, shipment_id):
    return _proxy('shipping', f'/shipments/{shipment_id}', method='PUT', data=_json_body(request))


@csrf_exempt
def ui_behaviors_view(request):
    data = _json_body(request)
    if request.method == 'POST':
        return _proxy('ai', '/ai/behaviors', method='POST', data=data)
    return _proxy('ai', '/ai/behaviors', params=request.GET.dict())


@csrf_exempt
def ui_knowledge_base_view(request):
    data = _json_body(request)
    if request.method == 'POST':
        return _proxy('ai', '/ai/knowledge-base', method='POST', data=data)
    return _proxy('ai', '/ai/knowledge-base', params=request.GET.dict())


@csrf_exempt
def ui_knowledge_search_view(request):
    return _proxy('ai', '/ai/knowledge-base/search', params=request.GET.dict())


@csrf_exempt
def ui_rag_context_view(request):
    return _proxy('ai', '/ai/rag/context', params=request.GET.dict())

def _actor(request):
    data = _json_body(request) or {}
    return (
        request.GET.get('user_id') or data.get('user_id'),
        request.GET.get('role') or data.get('role'),
        data,
    )

@csrf_exempt
def ui_admin_users_view(request):
    user_id, role, data = _actor(request)
    if request.method == 'POST':
        return _proxy('user', '/admin/users', method='POST', data=data, user_id=user_id, role=role)
    params = request.GET.dict()
    params.pop('user_id', None)
    params.pop('role', None)
    return _proxy('user', '/admin/users', params=params, user_id=user_id, role=role)

@csrf_exempt
def ui_admin_user_detail_view(request, target_user_id):
    user_id, role, data = _actor(request)
    if request.method == 'PUT':
        return _proxy('user', f'/admin/users/{target_user_id}', method='PUT', data=data, user_id=user_id, role=role)
    if request.method == 'DELETE':
        return _proxy('user', f'/admin/users/{target_user_id}', method='DELETE', user_id=user_id, role=role)
    return _proxy('user', f'/admin/users/{target_user_id}', user_id=user_id, role=role)

@csrf_exempt
def ui_admin_products_view(request, product_id=None):
    user_id, role, data = _actor(request)
    if product_id:
        if request.method == 'PUT':
            return _proxy('product', f'/products/{product_id}', method='PUT', data=data, user_id=user_id, role=role)
        if request.method == 'DELETE':
            return _proxy('product', f'/products/{product_id}', method='DELETE', user_id=user_id, role=role)
        return _proxy('product', f'/products/{product_id}', user_id=user_id, role=role)
    if request.method == 'POST':
        return _proxy('product', '/products', method='POST', data=data, user_id=user_id, role=role)
    return _proxy('product', '/products', params=request.GET.dict(), user_id=user_id, role=role)

@csrf_exempt
def ui_admin_categories_view(request):
    user_id, role, data = _actor(request)
    if request.method == 'POST':
        return _proxy('product', '/categories', method='POST', data=data, user_id=user_id, role=role)
    params = request.GET.dict()
    params.pop('user_id', None)
    params.pop('role', None)
    return _proxy('product', '/categories', params=params, user_id=user_id, role=role)

@csrf_exempt
def ui_admin_orders_view(request, order_id=None, action=None):
    user_id, role, data = _actor(request)
    if order_id and action == 'status':
        return _proxy('order', f'/admin/orders/{order_id}/status', method='PUT', data=data, user_id=user_id, role=role)
    if order_id and action == 'assign-staff':
        return _proxy('order', f'/admin/orders/{order_id}/assign-staff', method='PUT', data=data, user_id=user_id, role=role)
    if order_id:
        return _proxy('order', f'/admin/orders/{order_id}', user_id=user_id, role=role)
    return _proxy('order', '/admin/orders', params=request.GET.dict(), user_id=user_id, role=role)

@csrf_exempt
def ui_staff_orders_view(request, order_id=None, action=None):
    user_id, role, data = _actor(request)
    if order_id and action == 'confirm':
        return _proxy('order', f'/staff/orders/{order_id}/confirm', method='PUT', data=data, user_id=user_id, role=role)
    if order_id and action == 'ready-to-ship':
        return _proxy('order', f'/staff/orders/{order_id}/ready-to-ship', method='PUT', data=data, user_id=user_id, role=role)
    return _proxy('order', '/staff/orders', params=request.GET.dict(), user_id=user_id, role=role)

@csrf_exempt
def ui_admin_payments_view(request, payment_id=None):
    user_id, role, data = _actor(request)
    if payment_id and request.method == 'PUT':
        return _proxy('payment', f'/admin/payments/{payment_id}', method='PUT', data=data, user_id=user_id, role=role)
    if payment_id:
        return _proxy('payment', f'/admin/payments/{payment_id}', user_id=user_id, role=role)
    return _proxy('payment', '/admin/payments', params=request.GET.dict(), user_id=user_id, role=role)

@csrf_exempt
def ui_admin_shipments_view(request, shipment_id=None, action=None):
    user_id, role, data = _actor(request)
    if shipment_id and action == 'assign-shipper':
        return _proxy('shipping', f'/admin/shipments/{shipment_id}/assign-shipper', method='PUT', data=data, user_id=user_id, role=role)
    return _proxy('shipping', '/admin/shipments', params=request.GET.dict(), user_id=user_id, role=role)

@csrf_exempt
def ui_shipper_shipments_view(request, shipment_id=None, action=None):
    user_id, role, data = _actor(request)
    if shipment_id and action == 'status':
        return _proxy('shipping', f'/shipper/shipments/{shipment_id}/status', method='PUT', data=data, user_id=user_id, role=role)
    if shipment_id and action == 'note':
        return _proxy('shipping', f'/shipper/shipments/{shipment_id}/note', method='PUT', data=data, user_id=user_id, role=role)
    return _proxy('shipping', '/shipper/shipments', params=request.GET.dict(), user_id=user_id, role=role)

@api_view(['GET', 'POST'])
def customer_list_view(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        return Response(CustomerSerializer(customers, many=True).data)
        
    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def customer_detail_view(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        return Response(CustomerSerializer(customer).data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
