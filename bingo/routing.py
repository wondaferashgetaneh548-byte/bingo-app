from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # ሁለቱንም አይነት አፃፃፍ (በ slash እና ያለ slash) እንዲቀበል ተደርጓል
    re_path(r'^ws/bingo/$', consumers.BingoConsumer.as_asgi()),
    re_path(r'ws/bingo/', consumers.BingoConsumer.as_asgi()),
]