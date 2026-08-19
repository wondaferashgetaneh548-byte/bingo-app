import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import bingo.routing  # 'bingo' የሚለውን በእውነተኛው የApp ስምህ ተካው

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # 'core' የሚለውን በፕሮጀክትህ ስም ተካው

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            bingo.routing.websocket_urlpatterns  # የApp ስምህ .routing
        )
    ),
})