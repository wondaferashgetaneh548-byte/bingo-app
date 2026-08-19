from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bingo/(?P<room_name>\w+)/$', consumers.BingoRoomConsumer.as_asgi()),
]