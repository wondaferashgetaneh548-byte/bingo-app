from django.urls import path
from . import views

urlpatterns = [
    path('', views.rooms_list, name='rooms_list'),
    path('room/<int:stake>/', views.room_detail, name='room_detail'),
    path('room_<str:room_name>/', views.room_detail_by_name, name='room_detail_by_name'),
]