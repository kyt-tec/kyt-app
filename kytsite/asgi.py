import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from kytapp import routing as kyt_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kytsite.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            kyt_routing.websocket_urlpatterns
        )
    ),
})
