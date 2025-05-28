from django.urls import re_path
from . import consumers

# iletisim uygulaması için WebSocket URL desenleri
websocket_urlpatterns = [
    # Sohbet WebSocket bağlantıları için rota
    # ws/sohbet/123/ gibi URL'lerle eşleşir
    # sohbet_id'yi bir rakam grubu olarak yakalar
    re_path(r'ws/sohbet/(?P<sohbet_id>\d+)/$', consumers.SohbetConsumer.as_asgi()),
]