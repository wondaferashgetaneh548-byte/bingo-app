from django.urls import path
from . import views

app_name = 'bingo'

urlpatterns = [
    path('', views.rooms_list, name='rooms_list'),
    path('index/', views.index, name='index'),
    path('room/<int:stake>/', views.room_detail, name='room_detail'),
    path('select-card/', views.select_card, name='select_card'),
    
    # የቦርሳና የገንዘብ ዝውውር (Wallet, Deposit, Withdraw) URLs
    path('wallet/', views.wallet_view, name='wallet'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
]