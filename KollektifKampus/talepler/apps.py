from django.apps import AppConfig

# 'talepler' uygulamasının yapılandırması
class TaleplerConfig(AppConfig):
    # Modeller için varsayılan otomatik artan birincil anahtar türünü belirtir
    default_auto_field = 'django.db.models.BigAutoField'
    # Uygulamanın adını belirtir
    name = 'talepler'
