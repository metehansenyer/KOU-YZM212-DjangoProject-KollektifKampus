from django.db import models

# Sohbet modeli, bir ders isteğiyle ilişkili sohbet kanalını temsil eder.
class Sohbet(models.Model):
    # Bu sohbetin ilişkili olduğu ders isteği. Bir ders isteği için tek bir sohbet kanalı olur.
    ders_istegi = models.OneToOneField(
        'talepler.DersIstegi',
        on_delete=models.CASCADE,
        related_name='sohbet_kanali',
        verbose_name="İlgili Ders İsteği"
    )
    # Sohbete katılan kullanıcı profilleri. Bir sohbetin birden fazla katılımcısı olabilir.
    katilimcilar = models.ManyToManyField(
        'kullanicilar.KullaniciProfili',
        related_name='katildigi_sohbetler',
        verbose_name="Sohbet Katılımcıları"
    )
    # Sohbet kanalının oluşturulma tarihi ve saati.
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        # Admin panelinde gösterilecek tekil isim.
        verbose_name = "Sohbet Kanalı"
        # Admin panelinde gösterilecek çoğul isim.
        verbose_name_plural = "Sohbet Kanalları"
        # Sohbetleri oluşturulma tarihine göre tersten sırala (en yeni üstte).
        ordering = ['-olusturulma_tarihi']

    # Sohbet objesinin string temsilini döndürür.
    def __str__(self):
        # Katılımcı kullanıcı adlarını birleştir.
        katilimci_isimleri = ", ".join([k.user.username for k in self.katilimcilar.all()])
        # Sohbetin başlığını ve katılımcılarını içeren bir string döndür.
        return f"Ders İsteği '{self.ders_istegi.talep_basligi}' için sohbet (Katılımcılar: {katilimci_isimleri})"

# Mesaj model, bir sohbet kanalındaki tek bir mesajı temsil eder.
class Mesaj(models.Model):
    # Mesajın ait olduğu sohbet kanalı. Bir sohbetin birden fazla mesajı olabilir.
    sohbet = models.ForeignKey(Sohbet, on_delete=models.CASCADE, related_name='mesajlar', verbose_name="Sohbet Kanalı")
    # Mesajı gönderen kullanıcı profili. Gönderen silinse bile mesaj kalır.
    gonderen_kullanici = models.ForeignKey(
        'kullanicilar.KullaniciProfili',
        on_delete=models.SET_NULL,
        null=True,
        related_name='gonderdigi_mesajlar',
        verbose_name="Gönderen Kullanıcı"
    )
    # Mesajın metin içeriği.
    icerik = models.TextField(verbose_name="Mesaj İçeriği")
    # Mesajın gönderilme tarihi ve saati.
    gonderilme_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme Tarihi")
    # Mesajın okunup okunmadığı bilgisi.
    okundu_bilgisi = models.BooleanField(default=False, verbose_name="Okundu Bilgisi")

    class Meta:
        # Admin panelinde gösterilecek tekil isim.
        verbose_name = "Sohbet Mesajı"
        # Admin panelinde gösterilecek çoğul isim.
        verbose_name_plural = "Sohbet Mesajları"
        # Mesajları gönderilme tarihine göre sırala (en eski üstte).
        ordering = ['gonderilme_tarihi']

    # Mesaj objesinin string temsilini döndürür.
    def __str__(self):
        # Gönderen kullanıcı adını al, yoksa "Bilinmeyen Kullanıcı" yaz.
        gonderen = self.gonderen_kullanici.user.username if self.gonderen_kullanici else "Bilinmeyen Kullanıcı"
        # Gönderen, tarih/saat ve mesaj içeriğinin ilk 50 karakterini içeren bir string döndür.
        return f"{gonderen} ({self.gonderilme_tarihi:%d.%m.%Y %H:%M}): {self.icerik[:50]}..."
