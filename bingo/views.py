from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
import json

def index(request):
    """የመግቢያ Home Page View"""
    return render(request, 'room.html')

def rooms_list(request):
    """የክፍሎች ዝርዝር View (ወደ room.html ይመራል)"""
    return render(request, 'room.html')

def room_detail(request, stake):
    """በውርርድ መጠን (Stake) ወደ room.html መግቢያ View"""
    context = {
        'stake': stake,
        'room_name': f"room_{stake}"
    }
    return render(request, 'room.html', context)

def room_detail_by_name(request, room_name):
    """በክፍል ስም (Room Name) ወደ room.html መግቢያ View"""
    context = {
        'room_name': room_name
    }
    return render(request, 'room.html', context)

def select_card(request):
    """ተጫዋች ካርቴላ ሲመርጥ በ HTTP API የሚስተናገድበት (ከፈለጉ)"""
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