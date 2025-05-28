from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Ders değerlendirmelerini saklamak için kullanılan model
class Degerlendirme(models.Model):
    # İlgili Ders İsteği'ne ForeignKey ilişkisi
    # Ders isteği silindiğinde değerlendirme de silinir (CASCADE)
    # related_name, DersIstegi örneğinden değerlendirmelere erişimi sağlar (örn: ders_istegi.degerlendirmeleri.all())
    ders_istegi = models.ForeignKey(
        'talepler.DersIstegi',
        on_delete=models.CASCADE, # Veya SET_NULL eğer değerlendirme ders isteği silinse de kalmalıysa
        related_name='degerlendirmeleri',
        verbose_name="İlgili Ders İsteği" # Admin panelinde görünen isim
    )
    # Değerlendirmeyi yapan kullanıcı profiline ForeignKey ilişkisi
    # Değerlendiren kullanıcı silindiğinde değerlendirme de silinir (CASCADE)
    # related_name, KullaniciProfili örneğinden yaptığı değerlendirmelere erişimi sağlar
    degerlendiren_kullanici = models.ForeignKey(
        'kullanicilar.KullaniciProfili',
        on_delete=models.CASCADE, # Değerlendiren silinirse değerlendirme de silinsin
        related_name='yaptigi_degerlendirmeler',
        verbose_name="Değerlendirmeyi Yapan Kullanıcı" # Admin panelinde görünen isim
    )
    # Değerlendirilen kullanıcı profiline ForeignKey ilişkisi
    # Değerlendirilen kullanıcı silindiğinde değerlendirme de silinir (CASCADE)
    # related_name, KullaniciProfili örneğinden aldığı değerlendirmelere erişimi sağlar
    degerlendirilen_kullanici = models.ForeignKey(
        'kullanicilar.KullaniciProfili',
        on_delete=models.CASCADE, # Değerlendirilen silinirse değerlendirme de silinsin
        related_name='aldigi_degerlendirmeler',
        verbose_name="Değerlendirilen Kullanıcı" # Admin panelinde görünen isim
    )
    # Puan alanı, 1 ile 5 arasında değer alabilir
    puan = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Verilen Puan (1-5)" # Admin panelinde görünen isim
    )
    # Yorum alanı, boş bırakılabilir
    yorum = models.TextField(blank=True, verbose_name="Yorum") # Admin panelinde görünen isim
    # Değerlendirme tarihi alanı, kayıt oluşturulduğunda otomatik olarak ayarlanır
    degerlendirme_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Değerlendirme Tarihi") # Admin panelinde görünen isim

    # Model seçenekleri için Meta sınıfı
    class Meta:
        # Tekil nesne için insan tarafından okunabilir isim
        verbose_name = "Ders Değerlendirmesi"
        # Çoğul nesneler için insan tarafından okunabilir isim
        verbose_name_plural = "Ders Değerlendirmeleri"
        # Sorgu sonuçları için varsayılan sıralama (en yeni ilk)
        ordering = ['-degerlendirme_tarihi']
        # Bir kullanıcının, belirli bir ders isteği üzerinden başka bir kullanıcıyı yalnızca bir kez değerlendirebilmesini sağlar.
        unique_together = ('ders_istegi', 'degerlendiren_kullanici', 'degerlendirilen_kullanici')
        # Yaygın sorgu alanları için veritabanı indeksleri (daha hızlı arama için)
        indexes = [
            models.Index(fields=['ders_istegi', 'degerlendiren_kullanici']),
            models.Index(fields=['ders_istegi', 'degerlendirilen_kullanici']),
        ]

    # Model örneğinin string temsili
    def __str__(self):
        # Değerlendiren, değerlendirilen, ders isteği başlığı ve puanı içeren açıklayıcı bir string döndürür
        return f"{self.degerlendiren_kullanici.user.username} -> {self.degerlendirilen_kullanici.user.username} için {self.ders_istegi.talep_basligi} değerlendirmesi ({self.puan} puan)"

    # Özel doğrulama metodu
    def clean(self):
        from django.core.exceptions import ValidationError
        # Kullanıcının kendini değerlendirmesini engelle
        if self.degerlendiren_kullanici == self.degerlendirilen_kullanici:
            raise ValidationError("Kullanıcı kendini değerlendiremez.")

        from django.core.exceptions import ValidationError

        # Değerlendiren ve Değerlendirilen kullanıcıların ilgili ders isteğinin katılımcıları olup olmadığını kontrol et.
        # Değerlendiren kullanıcı ya talep eden ya da atanan eğitmen olmalı.
        # Değerlendirilen kullanıcı ise diğer katılımcı olmalı.
        is_valid_participant_pair = (
            (self.degerlendiren_kullanici == self.ders_istegi.talep_eden_kullanici and self.degerlendirilen_kullanici == self.ders_istegi.atanan_egitmen) or
            (self.degerlendiren_kullanici == self.ders_istegi.atanan_egitmen and self.degerlendirilen_kullanici == self.ders_istegi.talep_eden_kullanici)
        )

        if not is_valid_participant_pair:
             raise ValidationError("Değerlendirme yapan veya yapılan kullanıcı, ders isteğinin katılımcılarından biri olmalıdır.")

        # Ders isteğinin durumu "Tamamlandı" olmadan değerlendirme yapılamamalı.
        if self.ders_istegi.talep_durumu != 'TAMAMLANDI':
            raise ValidationError("Değerlendirme yapabilmek için dersin durumu 'Tamamlandı' olmalıdır.")

        # Üst sınıfın clean metodunu çağır
        super().clean()
