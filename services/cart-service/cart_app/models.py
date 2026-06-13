from django.db import models

class Cart(models.Model):
    user_id = models.IntegerField(unique=True)  # Logic reference to User Service User ID
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carts'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()  # Logic reference to Product Service Product ID
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product_id')
