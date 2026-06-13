from django.contrib import admin
from .models import KnowledgeBaseEntry, UserBehavior


@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id', 'action_type', 'timestamp')
    list_filter = ('action_type',)
    search_fields = ('user_id', 'product_id')


@admin.register(KnowledgeBaseEntry)
class KnowledgeBaseEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'intent', 'source_type', 'priority', 'is_active')
    list_filter = ('category', 'intent', 'source_type', 'is_active')
    search_fields = ('title', 'content', 'tags')
