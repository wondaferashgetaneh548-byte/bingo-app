import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages

# የክፍሎች ዝርዝር ማሳያ ገጽ
@login_required
def rooms_list(request):
    stakes = [10, 20, 50, 100, 200, 500]
    context = {
        'stakes': stakes
    }
    return render(request, 'bingo/rooms_list.html', context)

# ዋናው መነሻ ገጽ (Index Page)
@login_required
def index(request):
    return render(request, 'bingo/index.html')

# በቁጥር ለሚመጡ ክፍሎች (ምሳሌ፦ /bingo/room/100/)
@login_required
def room_detail(request, stake):
    context = {
        'stake': stake,
        'room_name': f"room_{stake}"
    }
    return render(request, 'bingo/bingo_room.html', context)

# በስም ለሚመጡ ክፍሎች (ምሳሌ፦ /bingo/room_100/)
@login_required
def room_detail_by_name(request, room_name):
    stake_clean = str(room_name).replace('room_', '')
    try:
        stake = int(stake_clean)
    except ValueError:
        stake = 10
        
    context = {
        'stake': stake,
        'room_name': f"room_{stake}"
    }
    return render(request, 'bingo/bingo_room.html', context)

# ካርቴላ መምረጫ ገጽ / API
@login_required
def select_card(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        # የካርቴላ መምረጥ Logic እዚህ ይፃፋል
        return JsonResponse({'status': 'success', 'card_id': card_id})
    return render(request, 'bingo/select_card.html')

# የኪስ ቦርሳ (Wallet) ገጽ
@login_required
def wallet(request):
    context = {
        'balance': getattr(request.user, 'balance', 0.0)
    }
    return render(request, 'bingo/wallet.html', context)

# ገንዘብ ገቢ ማድረጊያ (Deposit)
@login_required
def deposit(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # የገንዘብ ገቢ ማድረጊያ Process
        messages.success(request, f"{amount} ብር በስኬት ገቢ ሆኗል!")
        return redirect('wallet')
    return render(request, 'bingo/deposit.html')

# ገንዘብ ወጪ ማድረጊያ (Withdraw)
@login_required
def withdraw(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # የገንዘብ ወጪ ማድረጊያ Process
        messages.success(request, f"{amount} ብር ወጪ ለማድረግ ጥያቄ ቀርቧል!")
        return redirect('wallet')
    return render(request, 'bingo/withdraw.html')