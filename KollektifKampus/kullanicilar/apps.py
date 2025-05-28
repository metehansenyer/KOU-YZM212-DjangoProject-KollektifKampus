from django.apps import AppConfig


class KullanicilarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kullanicilar'

    def ready(self):
        # Uygulama yüklendiğinde çalışacak metot
        # Sinyal alıcılarını kaydetmek için sinyaller modülünü içe aktar
        import kullanicilar.signals
