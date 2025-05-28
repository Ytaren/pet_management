from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    # 宠物列表和CRUD操作
    path('', views.PetListView.as_view(), name='pet_list'),
    path('add/', views.PetCreateView.as_view(), name='pet_add'),
    path('<int:pk>/', views.PetDetailView.as_view(), name='pet_detail'),
    path('<int:pk>/edit/', views.PetUpdateView.as_view(), name='pet_edit'),
    path('<int:pk>/delete/', views.PetDeleteView.as_view(), name='pet_delete'),
    
    # AJAX接口
    path('ajax/breeds/', views.get_breeds_by_type, name='get_breeds_by_type'),
]
