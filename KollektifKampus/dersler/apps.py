from django.apps import AppConfig

# Dersler uygulamasının yapılandırma sınıfı
class DerslerConfig(AppConfig):
    # Modeller için varsayılan otomatik artan birincil anahtar türünü belirtir
    default_auto_field = 'django.db.models.BigAutoField'
    # Uygulamanın adını belirtir
    name = 'dersler'
