from django.apps import AppConfig

# 'iletisim' Django uygulaması için yapılandırma sınıfı.
class IletisimConfig(AppConfig):
    # Bu uygulamadaki modeller için kullanılacak birincil anahtar türünü belirtir.
    default_auto_field = 'django.db.models.BigAutoField'
    # Django uygulamasının adı.
    name = 'iletisim'
