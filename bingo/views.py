import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


# 1. Telegram Web App አውቶማቲክ ምዝገባ እና መግቢያ (Auth API)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def auth_user(request):
    data = request.data
    telegram_id = str(data.get('telegram_id'))
    username = data.get('username', f"Player_{telegram_id}")

    if not telegram_id or telegram_id == 'undefined':
        return Response({'error': 'ትክክለኛ Telegram ID አልቀረበም'}, status=400)

    # ተጠቃሚው ካለ ያመጣዋል፤ ከሌለ አዲስ አካውንት ይፈጥራል (Register/Login)
    user, created = User.objects.get_or_create(
        username=telegram_id,
        defaults={'first_name': username}
    )

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'status': 'success',
        'is_new_user': created,
        'token': token.key,
        'username': user.first_name,
        'user_id': user.id
    })


# 2. የክፍሎች ዝርዝር ማሳያ ገጽ
@login_required
def rooms_list(request):
    stakes = [10, 20, 50, 100, 200, 500]
    context = {
        'stakes': stakes
    }
    return render(request, 'bingo/rooms_list.html', context)


# 3. ዋናው መነሻ ገጽ (Index Page)
def index(request):
    return render(request, 'bingo/index.html')


# 4. በቁጥር ለሚመጡ ክፍሎች (ምሳሌ፦ /bingo/room/100/)
@login_required
def room_detail(request, stake):
    context = {
        'stake': stake,
        'room_name': f"room_{stake}"
    }
    return render(request, 'bingo/bingo_room.html', context)


# 5. በስም ለሚመጡ ክፍሎች (ምሳሌ፦ /bingo/room_100/)
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


# 6. ካርቴላ መምረጫ ገጽ / API
@csrf_exempt
def select_card(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        # የካርቴላ መምረጥ Logic
        return JsonResponse({'status': 'success', 'card_id': card_id})
    return render(request, 'bingo/select_card.html')


# 7. የኪስ ቦርሳ (Wallet) ገጽ
@login_required
def wallet(request):
    context = {
        'balance': getattr(request.user, 'balance', 0.0)
    }
    return render(request, 'bingo/wallet.html', context)


# 8. ገንዘብ ገቢ ማድረጊያ (Deposit)
@login_required
def deposit(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # የገንዘብ ገቢ ማድረጊያ Process logic
        messages.success(request, f"{amount} ብር በስኬት ገቢ ሆኗል!")
        return redirect('wallet')
    return render(request, 'bingo/deposit.html')


# 9. ገንዘብ ወጪ ማድረጊያ (Withdraw)
@login_required
def withdraw(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # የገንዘብ ወጪ ማድረጊያ Process logic
        messages.success(request, f"{amount} ብር ወጪ ለማድረግ ጥያቄ ቀርቧል!")
        return redirect('wallet')
    return render(request, 'bingo/withdraw.html')