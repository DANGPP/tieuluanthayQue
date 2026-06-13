from django.contrib import admin
from django.urls import path
from product_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/categories', views.category_list_view, name='category_list'),
    path('api/products', views.product_list_view, name='product_list'),
    path('api/products/<int:product_id>', views.product_detail_view, name='product_detail'),
]
