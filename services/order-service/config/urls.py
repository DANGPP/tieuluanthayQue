from django.contrib import admin
from django.urls import path
from order_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/orders', views.order_list_view, name='order_list'),
    path('api/orders/<int:order_id>', views.order_detail_view, name='order_detail'),
    path('api/orders/<int:order_id>/cancel', views.cancel_order_view, name='cancel_order'),
    path('api/admin/orders', views.admin_order_list_view, name='admin_order_list'),
    path('api/admin/orders/<int:order_id>', views.admin_order_detail_view, name='admin_order_detail'),
    path('api/admin/orders/<int:order_id>/status', views.admin_order_status_view, name='admin_order_status'),
    path('api/admin/orders/<int:order_id>/assign-staff', views.admin_assign_staff_view, name='admin_assign_staff'),
    path('api/staff/orders', views.staff_order_list_view, name='staff_order_list'),
    path('api/staff/orders/<int:order_id>/confirm', views.staff_confirm_order_view, name='staff_confirm_order'),
    path('api/staff/orders/<int:order_id>/ready-to-ship', views.staff_ready_to_ship_view, name='staff_ready_to_ship'),
]
