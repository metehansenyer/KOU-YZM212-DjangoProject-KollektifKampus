import os

# Gerekli Django ve Channels kütüphanelerini içe aktar
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Django ayarları için ortam değişkenini ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kollektif_kampus_projesi.settings')

# Standart Django HTTP uygulamasını al
django_asgi_app = get_asgi_application()

# WebSocket URL yönlendirmelerini içeren modülü içe aktar
import iletisim.routing

# Protokol türüne göre yönlendirme yapan ASGI uygulamasını tanımla
application = ProtocolTypeRouter({
    # HTTP istekleri için standart Django uygulamasını kullan
    "http": django_asgi_app,

    # WebSocket istekleri için Channels yapısını kullan
    "websocket": AllowedHostsOriginValidator( # Sadece izin verilen hostlardan gelen WebSocket bağlantılarına izin ver
        AuthMiddlewareStack( # Kimlik doğrulama bilgilerini WebSocket bağlantısına ekle
            URLRouter( # WebSocket URL'lerini yönlendir
                iletisim.routing.websocket_urlpatterns # iletisim uygulamasının WebSocket URL kalıpları
            )
        )
    ),
})
