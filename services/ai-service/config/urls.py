from django.contrib import admin
from django.urls import path
from ai_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ai/behaviors', views.behavior_list_view, name='behavior_list'),
    path('api/ai/knowledge-base', views.knowledge_base_list_view, name='knowledge_base_list'),
    path('api/ai/knowledge-base/<int:entry_id>', views.knowledge_base_detail_view, name='knowledge_base_detail'),
    path('api/ai/knowledge-base/search', views.knowledge_search_view, name='knowledge_search'),
    path('api/ai/rag/context', views.rag_context_view, name='rag_context'),
]
