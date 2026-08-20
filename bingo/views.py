from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def rooms_list(request):
    return render(request, 'bingo/rooms_list.html')

@login_required
def index(request):
    return render(request, 'bingo/index.html')

@login_required
def room_detail(request, stake):
    context = {
        'stake': stake,
        'room_name': f"room_{stake}"
    }
    return render(request, 'bingo/bingo_room.html', context)

@login_required
def room_detail_by_name(request, room_name):
    # 'room_10' ከተላከ stake=10 አድርጎ ይወስዳል
    stake = room_name.replace('room_', '')
    try:
        stake = int(stake)
    except ValueError:
        stake = 10
    return render(request, 'bingo/bingo_room.html', {'stake': stake, 'room_name': f"room_{stake}"})

@login_required
def select_card(request):
    return render(request, 'bingo/select_card.html')

@login_required
def wallet(request):
    return render(request, 'bingo/wallet.html')

@login_required
def deposit(request):
    return render(request, 'bingo/deposit.html')

@login_required
def withdraw(request):
    return render(request, 'bingo/withdraw.html')