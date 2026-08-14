from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # በ trailing slash እና ያለ trailing slash የሚመጡትን ሁሉ በትክክል ያስተናግዳል
    re_path(r'^ws/bingo/?$', consumers.BingoConsumer.as_asgi()),
]