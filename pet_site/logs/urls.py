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
    path('quick-create/', views.quick_log_create, name='quick_log_create'),
    
    path('<int:pk>/', views.PetLogDetailView.as_view(), name='log_detail'),
    path('<int:pk>/edit/', views.PetLogUpdateView.as_view(), name='log_edit'),
    path('<int:pk>/delete/', views.PetLogDeleteView.as_view(), name='log_delete'),
    
    # 特定宠物的日志
    path('pet/<int:pet_id>/', views.pet_logs_by_pet, name='pet_logs'),
    
    # 详细记录管理中心
    path('<int:log_id>/detailed/', views.detailed_log_center_view, name='detailed_log_center'),
    
    # 喂食记录管理
    path('<int:log_id>/feeding/create/', views.FeedingLogCreateView.as_view(), name='feeding_log_create'),
    path('feeding/<int:pk>/edit/', views.FeedingLogUpdateView.as_view(), name='feeding_log_edit'),
    
    # 运动记录管理
    path('<int:log_id>/exercise/create/', views.ExerciseLogCreateView.as_view(), name='exercise_log_create'),
    path('exercise/<int:pk>/edit/', views.ExerciseLogUpdateView.as_view(), name='exercise_log_edit'),
    
    # 健康记录管理
    path('<int:log_id>/health/create/', views.HealthLogCreateView.as_view(), name='health_log_create'),
    path('health/<int:pk>/edit/', views.HealthLogUpdateView.as_view(), name='health_log_edit'),
    
    # 用药记录管理
    path('<int:log_id>/medication/create/', views.MedicationLogCreateView.as_view(), name='medication_log_create'),
    path('medication/<int:pk>/edit/', views.MedicationLogUpdateView.as_view(), name='medication_log_edit'),
    
    # 详细记录删除
    path('detailed/<str:record_type>/<int:record_id>/delete/', views.delete_detailed_record, name='delete_detailed_record'),
    
    # AI分析功能
    path('ai-analysis/', views.ai_analysis_view, name='ai_analysis'),
    path('ai-analysis/pet/<int:pet_id>/', views.ai_analysis_view, name='ai_analysis_for_pet'),
    
    # 数据导出
    path('export/pet/<int:pet_id>/', views.log_data_export, name='log_export'),
    
    # 智能提醒API
    path('api/reminders/', views.get_smart_reminders, name='smart_reminders'),

    # 数据可视化中心
    path('visualization/', views.visualization_center_view, name='visualization_center'),
    path('api/chart-data/', views.get_pet_log_chart_data, name='pet_log_chart_data'),
    path('api/ai-health-analysis/', views.ai_pet_health_analysis_view, name='ai_pet_health_analysis'),
]
