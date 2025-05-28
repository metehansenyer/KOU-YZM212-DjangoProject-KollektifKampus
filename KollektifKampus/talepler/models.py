from django.db import models
# KullaniciProfili modelini kullanmak için
from dersler.models import Ders

# Kullanıcıların ders taleplerini temsil eden model
class DersIstegi(models.Model):
    # Beklenen bilgi seviyesi seçenekleri
    SEVIYE_CHOICES = [
        ('BASLANGIC', 'Başlangıç'),
        ('ORTA', 'Orta'),
        ('ILERI', 'İleri'),
        ('FARKETMEZ', 'Farketmez'),
    ]

    # Talebin mevcut durumunu belirten seçenekler
    TALEP_DURUMLARI = [
        ('AKTIF', 'Aktif'),
        ('EGITMEN_ATANDI', 'Eğitmen Atandı'),
        ('OGRENCI_TAMAMLADI', 'Öğrenci Tamamladı'),
        ('EGITMEN_TAMAMLADI', 'Eğitmen Tamamladı'),
        ('TAMAMLANDI', 'Tamamlandı'),
        ('KAPALI', 'Kapalı'),
    ]

    # Talebi oluşturan kullanıcı (KullaniciProfili modeline ForeignKey)
    talep_eden_kullanici = models.ForeignKey('kullanicilar.KullaniciProfili', on_delete=models.CASCADE, related_name='ders_istekleri', verbose_name="Talep Eden Kullanıcı")

    # İlgili standart ders (Ders modeline ForeignKey, boş bırakılabilir)
    ders = models.ForeignKey(Ders, on_delete=models.SET_NULL, null=True, blank=True, related_name='ders_istekleri', verbose_name="İlgili Standart Ders")

    # Talebin başlığı veya özel konu adı
    talep_basligi = models.CharField(max_length=255, verbose_name="Talep Başlığı/Özel Konu")
    # Talebin detaylı açıklaması
    detayli_aciklama = models.TextField(verbose_name="Detaylı Açıklama", help_text="Öğrenmek istediğiniz konular, mevcut bilgi seviyeniz ve dersten beklentileriniz.")
    # Beklenen bilgi seviyesi
    beklenen_seviye = models.CharField(max_length=10, choices=SEVIYE_CHOICES, default='FARKETMEZ', verbose_name="Beklenen Seviye")

    # Ders karşılığında teklif edilenler
    teklif_edilen_karsilik = models.TextField(blank=True, verbose_name="Teklif Edilen Karşılık", help_text="Ders karşılığında ne teklif ediyorsunuz? (örn: bir kahve, ücret, tatlı, karşılıklı ders vb.)")
    # Tercih edilen buluşma mekanı veya yöntemi
    mekan_tercihi = models.TextField(blank=True, verbose_name="Mekan Tercihi", help_text="Buluşma için tercih ettiğiniz mekan türü (örn: kampüs kütüphanesi, kafe, online vb.)")
    # Uygun olunan genel zaman aralıkları
    zaman_tercihi = models.TextField(blank=True, verbose_name="Zaman Tercihi", help_text="Ders için uygun olduğunuz genel zaman aralıkları.")

    # Talebin mevcut durumu
    talep_durumu = models.CharField(max_length=20, choices=TALEP_DURUMLARI, default='AKTIF', verbose_name="Talebin Durumu")

    # Öğrencinin talebi tamamladığı tarih
    ogrenci_tamamlama_tarihi = models.DateTimeField(null=True, blank=True, verbose_name="Öğrenci Tamamlama Tarihi")
    # Eğitmenin talebi tamamladığı tarih
    egitmen_tamamlama_tarihi = models.DateTimeField(null=True, blank=True, verbose_name="Eğitmen Tamamlama Tarihi")

    # Talebe atanan eğitmen (KullaniciProfili modeline ForeignKey, boş bırakılabilir)
    atanan_egitmen = models.ForeignKey(
        'kullanicilar.KullaniciProfili',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atanan_ders_istekleri', # Related name güncellendi
        verbose_name="Atanan Eğitmen"
    )

    # Talebin oluşturulma tarihi (otomatik eklenir)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    # Talebin son güncellenme tarihi (otomatik güncellenir)
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    # Modelin meta seçenekleri
    class Meta:
        verbose_name = "Ders İsteği"
        verbose_name_plural = "Ders İstekleri"
        # Varsayılan sıralama: oluşturulma tarihine göre azalan
        ordering = ['-olusturulma_tarihi']

    # Modelin string temsili
    def __str__(self):
        return f"{self.talep_basligi} (Talep Eden: {self.talep_eden_kullanici.user.username})"

# Eğitmenlerin ders taleplerine yaptığı başvuruları temsil eden model
class EgitmenBasvurusu(models.Model):
    # Başvurunun mevcut durumunu belirten seçenekler
    BASVURU_DURUM_CHOICES = [
        ('BEKLEMEDE', 'Beklemede'),
        ('KABUL_EDILDI', 'Kabul Edildi'),
        ('REDDEDILDI', 'Reddedildi'),
        ('GERI_CEKILDI', 'Geri Çekildi'),
    ]

    # Başvurunun yapıldığı ders isteği (DersIstegi modeline ForeignKey)
    ders_istegi = models.ForeignKey(DersIstegi, on_delete=models.CASCADE, related_name='egitmen_basvurulari', verbose_name="Ders İsteği")
    # Başvuruyu yapan eğitmen (KullaniciProfili modeline ForeignKey)
    basvuran_egitmen = models.ForeignKey('kullanicilar.KullaniciProfili', on_delete=models.CASCADE, related_name='yaptigi_egitmen_basvurulari', verbose_name="Başvuran Eğitmen")
    # Başvuru ile birlikte gönderilen mesaj
    basvuru_mesaji = models.TextField(blank=True, verbose_name="Başvuru Mesajı", help_text="Neden yardımcı olabileceğinize dair kısa bir açıklama.")
    # Başvurunun mevcut durumu
    basvuru_durumu = models.CharField(max_length=15, choices=BASVURU_DURUM_CHOICES, default='BEKLEMEDE', verbose_name="Başvuru Durumu")
    # Başvurunun yapıldığı tarih (otomatik eklenir)
    basvuru_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Başvuru Tarihi")

    # Modelin meta seçenekleri
    class Meta:
        verbose_name = "Eğitmen Başvurusu"
        verbose_name_plural = "Eğitmen Başvuruları"
        # Varsayılan sıralama: başvuru tarihine göre azalan
        ordering = ['-basvuru_tarihi']
        # Bir eğitmenin aynı ders isteğine birden fazla başvuru yapmasını engeller
        unique_together = ('ders_istegi', 'basvuran_egitmen')

    # Modelin string temsili
    def __str__(self):
        return f"{self.basvuran_egitmen.user.username} -> {self.ders_istegi.talep_basligi} ({self.get_basvuru_durumu_display()})"
