from django.db import models
from django.contrib.auth.models import User

# Kullanıcıların ek profil bilgilerini saklayan model
class KullaniciProfili(models.Model):
    # Kullanıcı rolleri için sabitler
    KULLANICI_ROLLER = [
        ('NORMAL', 'Normal Kullanıcı'),
        ('EGITMEN', 'Eğitmen'),
        ('MODERATOR', 'Moderatör'),
        ('ADMIN', 'Admin'),
    ]

    # Django'nun varsayılan User modeli ile birebir ilişki
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    # Kullanıcının üniversitesi
    universite = models.CharField(max_length=200, blank=True)
    # Kullanıcının bölümü
    bolum = models.CharField(max_length=200, blank=True)
    # Kullanıcının sınıfı
    sinif = models.CharField(max_length=50, blank=True)
    # Profil fotoğrafı indeksi (0-6 arası değer alır, 0=varsayılan)
    profil_fotografi_index = models.IntegerField(default=0, help_text="Profil fotoğrafı seçimi (0-6 arası)")
    # Kullanıcının rolü (NORMAL, EGITMEN, MODERATOR, ADMIN)
    kullanici_rolu = models.CharField(max_length=10, choices=KULLANICI_ROLLER, default='NORMAL')
    # Kullanıcının engellenip engellenmediği durumu
    ban_durumu = models.BooleanField(default=False)
    # Kullanıcının engelinin biteceği tarih ve saat
    ban_bitis_tarihi = models.DateTimeField(null=True, blank=True)
    # Kullanıcı hakkında kısa bilgi
    hakkinda = models.TextField(blank=True)

    # Modelin string temsili
    def __str__(self):
        return f'{self.user.username} Profili'

    # Kullanıcının adını ve soyadını birleştiren property
    @property
    def adi_soyadi(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    # Kullanıcının eğitmen rolüne sahip olup olmadığını kontrol eder (Eğitmen, Moderatör, Admin)
    def is_egitmen(self):
        return self.kullanici_rolu in ['EGITMEN', 'MODERATOR', 'ADMIN']
    
    # Kullanıcının moderatör rolüne sahip olup olmadığını kontrol eder (Moderatör, Admin)
    def is_moderator(self):
        return self.kullanici_rolu in ['MODERATOR', 'ADMIN']
    
    # Kullanıcının admin rolüne sahip olup olmadığını kontrol eder
    def is_admin(self):
        return self.kullanici_rolu == 'ADMIN'


# Normal kullanıcıların eğitmen olmak için doldurduğu başvuru formu modeli
class EgitmenBasvuruFormu(models.Model):
    # Başvuru durumları için sabitler
    BASVURU_DURUM_CHOICES = [
        ('BEKLEMEDE', 'Beklemede'),
        ('ONAYLANDI', 'Onaylandı'),
        ('REDDEDILDI', 'Reddedildi'),
    ]
    
    # Başvuruyu yapan kullanıcı profili ile ilişki
    kullanici = models.ForeignKey(KullaniciProfili, on_delete=models.CASCADE, related_name='egitmen_basvurulari', verbose_name="Başvuran Kullanıcı")
    # Kullanıcının eğitim bilgileri
    egitim_bilgileri = models.TextField(verbose_name="Eğitim Bilgileri", help_text="Eğitim geçmişiniz, mezun olduğunuz bölümler veya devam ettiğiniz programlar")
    # Kullanıcının eğitmenlik veya öğretim deneyimi
    deneyim = models.TextField(verbose_name="Deneyim", help_text="Eğitmenlik veya öğretim alanındaki deneyimleriniz")
    # Kullanıcının uzmanlık alanları
    uzmanlik_alanlari = models.TextField(verbose_name="Uzmanlık Alanları", help_text="Hangi konularda ders verebileceğiniz")
    # Kullanıcının eğitmen olma motivasyonu
    motivasyon = models.TextField(verbose_name="Motivasyon", help_text="Neden eğitmen olmak istiyorsunuz?")
    
    # Başvurunun mevcut durumu (Beklemede, Onaylandı, Reddedildi)
    basvuru_durumu = models.CharField(max_length=15, choices=BASVURU_DURUM_CHOICES, default='BEKLEMEDE', verbose_name="Başvuru Durumu")
    # Başvurunun yapıldığı tarih ve saat (otomatik eklenir)
    basvuru_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Başvuru Tarihi")
    # Başvurunun değerlendirildiği tarih ve saat
    degerlendirilme_tarihi = models.DateTimeField(null=True, blank=True, verbose_name="Değerlendirilme Tarihi")
    # Başvuruyu değerlendiren moderatör profili ile ilişki
    degerlendiren_moderator = models.ForeignKey(
        KullaniciProfili, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='degerlendirdigi_egitmen_basvurulari',
        verbose_name="Değerlendiren Moderatör"
    )
    # Başvuru reddedildiyse sebebi
    red_sebebi = models.TextField(blank=True, verbose_name="Ret Sebebi", help_text="Başvuru reddedildiyse, sebebi buraya yazılır")
    
    # Modelin meta seçenekleri
    class Meta:
        verbose_name = "Eğitmen Başvuru Formu"
        verbose_name_plural = "Eğitmen Başvuru Formları"
        # Başvuruları en yeni tarihe göre sırala
        ordering = ['-basvuru_tarihi']
    
    # Modelin string temsili
    def __str__(self):
        return f"{self.kullanici.user.username} - Eğitmen Başvurusu ({self.get_basvuru_durumu_display()})"
