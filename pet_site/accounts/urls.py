from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('pet-consult/', views.pet_consult_view, name='pet-consult'),
    path('consultation-history/', views.consultation_history_view, name='consultation_history'),
    path('consultation-history/delete/<int:pk>/', views.delete_consultation_history, name='delete_consultation_history'),
]