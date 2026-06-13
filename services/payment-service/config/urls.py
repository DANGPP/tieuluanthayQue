from django.contrib import admin
from django.urls import path
from payment_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/payments', views.create_payment_view, name='create_payment'),
    path('api/payments/<int:payment_id>/confirm', views.confirm_payment_view, name='confirm_payment'),
    path('api/admin/payments', views.admin_payment_list_view, name='admin_payment_list'),
    path('api/admin/payments/<int:payment_id>', views.admin_payment_detail_view, name='admin_payment_detail'),
]
