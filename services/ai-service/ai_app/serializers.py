from rest_framework import serializers
from .models import UserBehavior

class UserBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = ['id', 'user_id', 'product_id', 'action_type', 'timestamp']
