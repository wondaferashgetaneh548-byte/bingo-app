from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

def index(request):
    """የመግቢያ ወይም የዋና ገፅ View"""
    return render(request, 'index.html')

def rooms_list(request):
    """የተለያዩ የቋሚ ውርርድ ክፍሎችን (Rooms) የሚያሳይ View"""
    # ናሙና የክፍል ደረጃዎች (Stakes)
    stakes = [10, 20, 50, 100]
    return render(request, 'rooms_list.html', {'stakes': stakes})

def room_detail(request, stake):
    """በውርርድ መጠን (Stake) ወደ ክፍል መግቢያ View"""
    context = {
        'stake': stake,
        'room_name': f"room_{stake}"
    }
    return render(request, 'room_detail.html', context)

def room_detail_by_name(request, room_name):
    """በክፍል ስም (Room Name) ወደ ክፍል መግቢያ View"""
    context = {
        'room_name': room_name
    }
    return render(request, 'room_detail.html', context)

def select_card(request):
    """ተጫዋች ካርቴላ ሲመርጥ በ API ወይም AJAX የሚስተናገድበት View"""
    if request.method == 'POST':
        data = json.loads(request.body)
        cartela_id = data.get('cartela_id')
        return JsonResponse({'status': 'success', 'cartela_id': cartela_id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def wallet(request):
    """የተጫዋች የገንዘብ ቦርሳ (Wallet) ሁኔታ የሚያይበት View"""
    return render(request, 'wallet.html')

@login_required
def deposit(request):
    """ገንዘብ ገቢ ማድረጊያ View"""
    if request.method == 'POST':
        # የገንዘብ ገቢ ማድረጊያ Process እዚህ ይሰራል
        return redirect('wallet')
    return render(request, 'deposit.html')

@login_required
def withdraw(request):
    """ገንዘብ ወጪ ማድረጊያ View"""
    if request.method == 'POST':
        # የገንዘብ ወጪ ማድረጊያ Process እዚህ ይሰራል
        return redirect('wallet')
    return render(request, 'withdraw.html')

def auth_user(request):
    """የተጫዋች Auth/API View"""
    return JsonResponse({'user': request.user.username if request.user.is_authenticated else 'Guest'})