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
