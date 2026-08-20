from django.urls import path
from . import views

urlpatterns = [
    path('', views.rooms_list, name='rooms_list'),
    path('index/', views.index, name='index'),
    path('room/<int:stake>/', views.room_detail, name='room_detail'),
    path('room_<str:room_name>/', views.room_detail_by_name, name='room_detail'),
    path('select-card/', views.select_card, name='select_card'),
    path('wallet/', views.wallet, name='wallet'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
]