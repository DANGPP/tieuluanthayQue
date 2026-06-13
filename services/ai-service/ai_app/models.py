from django.db import models

class UserBehavior(models.Model):
    ACTION_CHOICES = (
        ('view', 'View'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('rate', 'Rate'),
        ('search', 'Search'),
    )
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_user_behaviors'


class KnowledgeBaseEntry(models.Model):
    SOURCE_CHOICES = (
        ('product', 'Product'),
        ('category', 'Category'),
        ('policy', 'Policy'),
        ('faq', 'FAQ'),
        ('guide', 'Guide'),
        ('recommendation_rule', 'Recommendation Rule'),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    intent = models.CharField(max_length=100, blank=True)
    source_type = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='guide')
    product_id = models.IntegerField(null=True, blank=True)
    tags = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_knowledge_base'
        ordering = ['-priority', 'category', 'title']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['intent']),
            models.Index(fields=['source_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title
