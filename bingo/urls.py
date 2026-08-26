from django.urls import path
from . import views

urlpatterns = [
    # 1. መጀመሪያ የሚከፈተው (Login Page / index.html)
    path('', views.index, name='index'),
    
    # 2. የ Stake/ብር መጠን መምረጫ (rooms_list.html)
    path('rooms/', views.rooms_list, name='rooms_list'),
    
    # 3. በቁጥር የሚጠራ (ምሳሌ፦ /room/10/)
    path('room/<int:stake>/', views.room_detail, name='room_detail'),
    
    # 4. በስም የሚጠራ (ምሳሌ፦ /room_10/)
    path('room_<str:room_name>/', views.room_detail_by_name, name='room_detail_by_name'),
    
    path('select-card/', views.select_card, name='select_card'),
    path('wallet/', views.wallet, name='wallet'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
]