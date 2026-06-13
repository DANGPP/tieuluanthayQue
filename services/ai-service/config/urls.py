from django.contrib import admin
from django.urls import path
from ai_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ai/behaviors', views.behavior_list_view, name='behavior_list'),
]
