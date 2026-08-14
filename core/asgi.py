import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import bingo.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# HTTP እና WebSocket ጥያቄዎችን ለይቶ ይመራል
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bingo.routing.websocket_urlpatterns
        )
    ),
})