from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import KullaniciProfili

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # User modeli kaydedildiğinde (oluşturulduğunda veya güncellendiğinde) tetiklenir.
    # İlişkili KullaniciProfili nesnesini oluşturur veya günceller.
    
    # Eğer User nesnesi yeni oluşturulduysa
    if created:
        # Bu User için yeni bir KullaniciProfili nesnesi oluştur
        KullaniciProfili.objects.create(user=instance)
    else:
        # Eğer User nesnesi güncelleniyorsa
        # Şu an için güncelleme durumunda profil üzerinde özel bir işlem yapılmıyor.
        # İleride User üzerindeki değişikliklerin profile yansıması gerekirse buraya kod eklenebilir.
        pass