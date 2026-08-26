from django.urls import path
from . import views

urlpatterns = [
    # 1. Root URL (http://127.0.0.1:8000/) - መጀመሪያ Login (index.html) ያሳያል
    path('', views.index, name='index'),
    
    # 2. የ Stake/ብር መጠን መምረጫ ገፅ (rooms_list.html)
    path('rooms/', views.rooms_list, name='rooms_list'),
    
    # 3. የጨዋታው ክፍል ገፅ (room.html)
    path('room/<str:stake>/', views.room_detail, name='room_detail'),
    path('room/name/<str:room_name>/', views.room_detail_by_name, name='room_detail_by_name'),
    
    # API endpoints
    path('select-card/', views.select_card, name='select_card'),
    path('api/auth-user/', views.auth_user, name='auth_user'),
    
    # Wallet & transactions
    path('wallet/', views.wallet, name='wallet'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
]