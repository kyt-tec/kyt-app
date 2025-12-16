from django.urls import re_path
from . import consumers
from .consumers import Round1Consumer

websocket_urlpatterns = [
    
    # Round1〜3用
   re_path(r'ws/kyt/(?P<session_id>\w+)/$', consumers.Round1Consumer.as_asgi()),

    # Round4専用
    
]
