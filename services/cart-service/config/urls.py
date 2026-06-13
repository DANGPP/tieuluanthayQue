from django.contrib import admin
from django.urls import path
from cart_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cart', views.cart_view, name='cart'),
    path('api/cart/items', views.add_cart_item_view, name='add_cart_item'),
    path('api/cart/items/<int:product_id>', views.cart_item_detail_view, name='cart_item_detail'),
    path('api/cart/checkout-preview', views.checkout_preview_view, name='checkout_preview'),
]
