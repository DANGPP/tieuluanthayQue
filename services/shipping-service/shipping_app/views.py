import datetime
import os
import requests
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Shipment
from .serializers import ShipmentSerializer

ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://127.0.0.1:8004/api/orders')

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

def notify_order_status(order_id, status_val):
    try:
        requests.put(f"{ORDER_SERVICE_URL}/{order_id}", json={'status': status_val}, timeout=10)
    except requests.exceptions.RequestException:
        pass

def apply_shipment_status(shipment, status_val):
    if status_val not in dict(Shipment.STATUS_CHOICES):
        return False
    shipment.status = status_val
    if status_val == 'assigned' and not shipment.assigned_at:
        shipment.assigned_at = timezone.now()
    if status_val == 'picked_up':
        shipment.picked_up_at = timezone.now()
        shipment.shipped_at = shipment.shipped_at or timezone.now()
    if status_val == 'delivered':
        shipment.delivered_at = timezone.now()
        notify_order_status(shipment.order_id, 'completed')
    if status_val in ['assigned', 'picked_up', 'in_transit', 'out_for_delivery']:
        notify_order_status(shipment.order_id, 'shipping')
    shipment.save()
    return True

@api_view(['POST'])
def create_shipment_view(request):
    order_id = request.data.get('order_id')
    address = request.data.get('address')
    
    if not order_id or not address:
        return Response({'error': 'order_id and address are required'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Generate a dummy tracking number
    tracking_number = f"TRK{order_id}{int(timezone.now().timestamp())}"
    estimated_delivery = (timezone.now() + datetime.timedelta(days=3)).date()
    
    shipment = Shipment.objects.create(
        order_id=order_id,
        address=address,
        tracking_number=tracking_number,
        estimated_delivery=estimated_delivery,
        status='pending'
    )
    return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
def update_shipment_view(request, shipment_id):
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)
        
    status_val = request.data.get('status')
    if not status_val or status_val not in dict(Shipment.STATUS_CHOICES):
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
    apply_shipment_status(shipment, status_val)
    return Response(ShipmentSerializer(shipment).data)

@api_view(['GET'])
def get_shipment_by_order_view(request, order_id):
    try:
        shipment = Shipment.objects.get(order_id=order_id)
        return Response(ShipmentSerializer(shipment).data)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found for this order'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def admin_shipment_list_view(request):
    if not has_role(request, 'admin', 'staff'):
        return Response({'error': 'Admin or staff role required'}, status=status.HTTP_403_FORBIDDEN)

    shipments = Shipment.objects.all().order_by('-created_at')
    status_filter = request.query_params.get('status')
    shipper_id = request.query_params.get('shipper_id')
    if status_filter:
        shipments = shipments.filter(status=status_filter)
    if shipper_id:
        shipments = shipments.filter(shipper_id=shipper_id)
    return Response(ShipmentSerializer(shipments, many=True).data)

@api_view(['PUT'])
def admin_assign_shipper_view(request, shipment_id):
    if not has_role(request, 'admin', 'staff'):
        return Response({'error': 'Admin or staff role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)

    shipper_id = request.data.get('shipper_id')
    if not shipper_id:
        return Response({'error': 'shipper_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        shipment.shipper_id = int(shipper_id)
    except (TypeError, ValueError):
        return Response({'error': 'shipper_id must be an integer'}, status=status.HTTP_400_BAD_REQUEST)
    apply_shipment_status(shipment, 'assigned')
    return Response(ShipmentSerializer(shipment).data)

@api_view(['GET'])
def shipper_shipment_list_view(request):
    if not has_role(request, 'shipper', 'admin'):
        return Response({'error': 'Shipper role required'}, status=status.HTTP_403_FORBIDDEN)
    shipper_id = get_user_id(request)
    shipments = Shipment.objects.all().order_by('-created_at')
    if shipper_id and get_role(request) == 'shipper':
        shipments = shipments.filter(shipper_id=shipper_id)
    return Response(ShipmentSerializer(shipments, many=True).data)

@api_view(['PUT'])
def shipper_shipment_status_view(request, shipment_id):
    if not has_role(request, 'shipper', 'admin'):
        return Response({'error': 'Shipper role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)

    shipper_id = get_user_id(request)
    if get_role(request) == 'shipper' and shipment.shipper_id != shipper_id:
        return Response({'error': 'Shipment is not assigned to this shipper'}, status=status.HTTP_403_FORBIDDEN)
    status_val = request.data.get('status')
    if not status_val or not apply_shipment_status(shipment, status_val):
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(ShipmentSerializer(shipment).data)

@api_view(['PUT'])
def shipper_shipment_note_view(request, shipment_id):
    if not has_role(request, 'shipper', 'admin'):
        return Response({'error': 'Shipper role required'}, status=status.HTTP_403_FORBIDDEN)
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)

    shipper_id = get_user_id(request)
    if get_role(request) == 'shipper' and shipment.shipper_id != shipper_id:
        return Response({'error': 'Shipment is not assigned to this shipper'}, status=status.HTTP_403_FORBIDDEN)
    shipment.delivery_note = request.data.get('delivery_note', '')
    shipment.save(update_fields=['delivery_note', 'updated_at'])
    return Response(ShipmentSerializer(shipment).data)
