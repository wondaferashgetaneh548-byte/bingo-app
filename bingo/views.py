import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet, Transaction

def index(request):
    return render(request, 'bingo/index.html')

def rooms_list(request):
    return render(request, 'bingo/rooms.html')
def bingo_view(request): # የ እጅህ view ስም ከ bingo_view ሊይይዝ ይችላል
    response = render(request, 'bingo.html') # የ HTML ፋይልህ ስም
    response['ngrok-skip-browser-warning'] = 'true'
    return response
def room_detail(request, stake):
    context = {
        'stake': stake,
        'room_name': f'room_{stake}'
    }
    return render(request, 'bingo/index.html', context)

@csrf_exempt
def select_card(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            card_id = data.get('card_id')
            return JsonResponse({
                'status': 'success',
                'message': f'ካርቴላ #{card_id} በትክክል ተይዟል!'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid Method'}, status=405)

# ---------------- WALLET VIEWS ----------------

@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'bingo/wallet.html', {
        'wallet': wallet,
        'transactions': transactions
    })

@login_required
def deposit(request):
    if request.method == 'POST':
        try:
            amount_str = request.POST.get('amount', '0').strip()
            amount = float(amount_str) if amount_str else 0.0
            payment_method = request.POST.get('payment_method', 'Telebirr')
            
            if amount > 0:
                wallet, created = Wallet.objects.get_or_create(user=request.user)
                wallet.balance = float(wallet.balance) + amount
                wallet.save()
                
                Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='DEPOSIT',
                    payment_method=payment_method,
                    status='APPROVED'
                )
                messages.success(request, f"በተሳካ ሁኔታ {amount} ETB ገብቷል!")
            else:
                messages.error(request, "እባክዎን ከ 0 በላይ የሆነ የብር መጠን ያስገቡ!")
        except ValueError:
            messages.error(request, "እባክዎን ትክክለኛ ቁጥር ያስገቡ!")
            
    return redirect('bingo:wallet')

@login_required
def withdraw(request):
    if request.method == 'POST':
        try:
            amount_str = request.POST.get('amount', '0').strip()
            amount = float(amount_str) if amount_str else 0.0
            account_number = request.POST.get('account_number', '')
            payment_method = request.POST.get('payment_method', 'Telebirr')
            
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            
            if amount > 0 and float(wallet.balance) >= amount:
                wallet.balance = float(wallet.balance) - amount
                wallet.save()
                
                Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='WITHDRAW',
                    payment_method=payment_method,
                    account_number=account_number,
                    status='APPROVED'
                )
                messages.success(request, f"በተሳካ ሁኔታ {amount} ETB ወጥቷል!")
            else:
                messages.error(request, "በቂ ሂሳብ የሎትም ወይም የተሳሳተ መጠን ያስገቡ!")
        except ValueError:
            messages.error(request, "እባክዎን ትክክለኛ ቁጥር ያስገቡ!")
            
    return redirect('bingo:wallet')