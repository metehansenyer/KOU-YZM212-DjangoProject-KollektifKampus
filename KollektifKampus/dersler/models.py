from django.db import models

# Ders modelini tanımlar. Her bir dersin bilgilerini saklar.
class Ders(models.Model):
    # Dersin adını saklar. Maksimum 255 karakter uzunluğunda ve benzersiz olmalıdır.
    ders_adi = models.CharField(max_length=255, unique=True, verbose_name="Ders Adı")
    # Dersin ait olduğu kategoriyi saklar. Maksimum 100 karakter uzunluğunda olabilir ve boş bırakılabilir.
    kategori = models.CharField(max_length=100, blank=True, verbose_name="Kategori", help_text="Dersin ait olduğu genel kategori (örn: Matematik, Yazılım, Dil)")
    # Ders hakkında detaylı bir açıklama saklar. Metin alanı olup boş bırakılabilir.
    aciklama = models.TextField(blank=True, verbose_name="Açıklama", help_text="Ders hakkında kısa bir açıklama")
    # Dersin veritabanına eklendiği tarihi ve saati otomatik olarak saklar.
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    # Dersin en son güncellendiği tarihi ve saati otomatik olarak saklar.
    guncellenme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    # Dersin platformda aktif olup olmadığını belirten boolean alan. Varsayılan değeri True'dur.
    aktif_mi = models.BooleanField(default=True, verbose_name="Aktif Mi?", help_text="Bu dersin platformda seçilebilir olup olmadığını belirtir.")

    # Modelin meta seçeneklerini tanımlayan iç sınıf.
    class Meta:
        # Admin panelinde modelin tekil adını belirler.
        verbose_name = "Ders"
        # Admin panelinde modelin çoğul adını belirler.
        verbose_name_plural = "Dersler"
        # Sorgu sonuçlarının varsayılan sıralamasını belirler. Ders adına göre sıralanır.
        ordering = ['ders_adi'] # Dersleri ada göre sırala

    # Model nesnesinin string temsilini döndürür.
    def __str__(self):
        # Dersin adını döndürerek nesneyi temsil eder.
        return self.ders_adi
