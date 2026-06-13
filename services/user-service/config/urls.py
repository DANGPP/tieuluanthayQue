from django.contrib import admin
from django.urls import path
from user_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register', views.register_view, name='register'),
    path('api/auth/login', views.login_view, name='login'),
    path('api/users/me', views.user_me_view, name='user_me'),
    path('api/users', views.admin_user_list_view, name='admin_user_list'),
    path('api/users/<int:user_id>', views.get_user_by_id, name='get_user_by_id'),
    path('api/users/<int:user_id>/role', views.get_user_role_view, name='get_user_role'),
    path('api/admin/users', views.admin_user_list_view, name='admin_user_list_alias'),
    path('api/admin/users/<int:user_id>', views.admin_user_detail_view, name='admin_user_detail'),
    path('api/users/me/addresses', views.address_list_view, name='address_list'),
    path('api/users/me/addresses/<int:address_id>', views.address_detail_view, name='address_detail'),
]
