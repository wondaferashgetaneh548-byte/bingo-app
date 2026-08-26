from django.urls import path
from . import views

urlpatterns = [
    # 1. Root - መጀመሪያ Login ገጽ (login.html)
    path('', views.index, name='index'),
    
    # 2. Home Page (ቢንጎ ጌም - Play button ያለው ገጽ)
    path('home/', views.home, name='home'),
    
    # 3. Rooms List Page (10birr, 20birr... Join buttons)
    path('rooms/', views.rooms_list, name='rooms_list'),
    
    # 4. Game Room Page (የ 1-400 ካርቴላ መምረጫ Grid)
    path('room/<str:stake>/', views.room_detail, name='room_detail'),
    path('room/name/<str:room_name>/', views.room_detail_by_name, name='room_detail_by_name'),
    
    # API Endpoints
    path('select-card/', views.select_card, name='select_card'),
    path('api/auth-user/', views.auth_user, name='auth_user'),
    
    # Wallet & transactions
    path('wallet/', views.wallet, name='wallet'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
]