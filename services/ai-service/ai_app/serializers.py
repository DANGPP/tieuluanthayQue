from rest_framework import serializers
from .models import KnowledgeBaseEntry, UserBehavior

class UserBehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = ['id', 'user_id', 'product_id', 'action_type', 'timestamp']


class KnowledgeBaseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBaseEntry
        fields = [
            'id',
            'title',
            'content',
            'category',
            'intent',
            'source_type',
            'product_id',
            'tags',
            'priority',
            'is_active',
            'created_at',
            'updated_at',
        ]
