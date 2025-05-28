from django.apps import AppConfig

# Uygulama yapılandırması sınıfı
class GeribildirimConfig(AppConfig):
    # Modeller için varsayılan otomatik artan anahtar alan tipini belirtir
    default_auto_field = 'django.db.models.BigAutoField'
    # Uygulamanın Python yolunu belirtir
    name = 'geribildirim'
