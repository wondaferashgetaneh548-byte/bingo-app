from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
import json

def index(request):
    """1. መጀመሪያ የሚከፈተው - Login Page"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'bingo/index.html')

@login_required
def home(request):
    """2. ከ Login በኋላ የሚመጣው Landing Page (ቢንጎ ጌም + Play Button)"""
    return render(request, 'bingo/home.html')

@login_required
def rooms_list(request):
    """3. Play ሲነካ የሚመጣው የ Stake ዝርዝር (10birr, 20birr, Join buttons...)"""
    return render(request, 'bingo/rooms_list.html')

@login_required
def room_detail(request, stake):
    """4. Join ሲነካ የሚመጣው የጨዋታ ክፍል (1-400 Cartela Grid)"""
    context = {
        'stake': stake,
        'room_name': f"room_{stake}"
    }
    return render(request, 'bingo/room.html', context)

def room_detail_by_name(request, room_name):
    """በክፍል ስም (Room Name) ወደ ጨዋታ ክፍል መግቢያ View"""
    context = {
        'room_name': room_name
    }
    return render(request, 'bingo/room.html', context)

def select_card(request):
    """ተጫዋች ካርቴላ ሲመርጥ በ HTTP API የሚስተናገድበት"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cartela_id = data.get('cartela_id')
            return JsonResponse({'status': 'success', 'cartela_id': cartela_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def wallet(request):
    """የተጫዋች የገንዘብ ቦርሳ View"""
    return HttpResponse("<h1>Wallet Page</h1>")

@login_required
def deposit(request):
    """ገንዘብ ገቢ ማድረጊያ View"""
    return HttpResponse("<h1>Deposit Page</h1>")

@login_required
def withdraw(request):
    """ገንዘብ ወጪ ማድረጊያ View"""
    return HttpResponse("<h1>Withdraw Page</h1>")

def auth_user(request):
    """የተጫዋች Authentication ማረጋገጫ API View"""
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True, 'username': request.user.username})
    return JsonResponse({'authenticated': False, 'username': 'Guest'})