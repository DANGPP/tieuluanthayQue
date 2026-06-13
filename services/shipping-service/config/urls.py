from django.contrib import admin
from django.urls import path
from shipping_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/shipments', views.create_shipment_view, name='create_shipment'),
    path('api/shipments/<int:shipment_id>', views.update_shipment_view, name='update_shipment'),
    path('api/shipments/order/<int:order_id>', views.get_shipment_by_order_view, name='get_shipment_by_order'),
    path('api/admin/shipments', views.admin_shipment_list_view, name='admin_shipment_list'),
    path('api/admin/shipments/<int:shipment_id>/assign-shipper', views.admin_assign_shipper_view, name='admin_assign_shipper'),
    path('api/shipper/shipments', views.shipper_shipment_list_view, name='shipper_shipment_list'),
    path('api/shipper/shipments/<int:shipment_id>/status', views.shipper_shipment_status_view, name='shipper_shipment_status'),
    path('api/shipper/shipments/<int:shipment_id>/note', views.shipper_shipment_note_view, name='shipper_shipment_note'),
]
