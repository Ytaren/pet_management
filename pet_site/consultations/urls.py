from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('pet-consult/', views.pet_consult_view, name='pet_consult'),
    path('history/', views.consultation_history_view, name='consultation_history'),
    path('history/delete/<int:pk>/', views.delete_consultation_history, name='delete_consultation_history'),
]
