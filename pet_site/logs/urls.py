from django.urls import path
from . import views

app_name = 'logs'

urlpatterns = [
    # 统一的日志中心 - 新的主入口
    path('', views.logs_center_view, name='logs_center'),
    
    # 原有功能保持兼容
    path('list/', views.PetLogListView.as_view(), name='log_list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # 日志 CRUD 操作
    path('create/', views.PetLogCreateView.as_view(), name='log_create'),
    path('create/pet/<int:pet_id>/', views.PetLogCreateView.as_view(), name='log_create_for_pet'),
    
    # 快速记录API
    path('quick-create/', views.quick_log_create, name='quick_log_create'),    # 快速记录API
    path('quick-create/', views.quick_log_create, name='quick_log_create'),
    
    path('<int:pk>/', views.PetLogDetailView.as_view(), name='log_detail'),
    path('<int:pk>/edit/', views.PetLogUpdateView.as_view(), name='log_edit'),
    path('<int:pk>/delete/', views.PetLogDeleteView.as_view(), name='log_delete'),
    
    # 特定宠物的日志
    path('pet/<int:pet_id>/', views.pet_logs_by_pet, name='pet_logs'),
    
    # AI分析功能 - 增强版
    path('ai-analysis/', views.ai_analysis_view, name='ai_analysis'),
    path('ai-analysis/pet/<int:pet_id>/', views.ai_analysis_view, name='ai_analysis_for_pet'),
    
    # 数据导出
    path('export/pet/<int:pet_id>/', views.log_data_export, name='log_export'),
    
    # 智能提醒API
    path('api/reminders/', views.get_smart_reminders, name='smart_reminders'),
]
