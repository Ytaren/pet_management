from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 认证相关
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # 用户设置相关
    path('settings/', views.user_settings_view, name='user_settings'),
    path('settings/profile/', views.profile_settings_view, name='profile_settings'),
    path('settings/security/', views.security_settings_view, name='security_settings'),
    path('settings/account-info/', views.account_info_view, name='account_info'),
    
    # AJAX接口
    path('api/delete-profile-picture/', views.delete_profile_picture, name='delete_profile_picture'),
]