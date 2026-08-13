from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/bingo/$', consumers.BingoConsumer.as_asgi()), # ወይም r'ws/bingo/' ከሆነ ከተለያዩ አፃፃፎች ጋር እንዲሄድ ከታች ያለውን ተጠቀም
]