from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import json

def index(request):
    return HttpResponse("<h1>Welcome to Bingo Game</h1><a href='/rooms/'>Go to Rooms</a>")

def rooms_list(request):
    return HttpResponse("<h1>Bingo Rooms List</h1><p>Select a room to join.</p>")

def room_detail(request, stake):
    return HttpResponse(f"<h1>Bingo Room - Stake: {stake}</h1>")

def room_detail_by_name(request, room_name):
    return HttpResponse(f"<h1>Bingo Room: {room_name}</h1>")

def select_card(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def wallet(request):
    return HttpResponse("<h1>Wallet Page</h1>")

@login_required
def deposit(request):
    return HttpResponse("<h1>Deposit Page</h1>")

@login_required
def withdraw(request):
    return HttpResponse("<h1>Withdraw Page</h1>")

def auth_user(request):
    return JsonResponse({'user': request.user.username if request.user.is_authenticated else 'Guest'})