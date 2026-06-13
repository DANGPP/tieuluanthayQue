from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            'id', 'user_id', 'assigned_staff_id', 'total_price', 'status', 'address',
            'confirmed_at', 'processing_at', 'cancelled_reason', 'items', 'created_at', 'updated_at'
        ]
