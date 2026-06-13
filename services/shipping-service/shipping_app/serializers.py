from rest_framework import serializers
from .models import Shipment

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            'id', 'order_id', 'shipper_id', 'tracking_number', 'status', 'address',
            'assigned_at', 'picked_up_at', 'shipped_at', 'delivered_at',
            'estimated_delivery', 'delivery_note', 'created_at', 'updated_at'
        ]
