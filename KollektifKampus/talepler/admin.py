from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import DersIstegi, EgitmenBasvurusu

# Ders İstekleri modelinin admin panelindeki görünümünü yapılandırır
@admin.register(DersIstegi)
class DersIstegiAdmin(admin.ModelAdmin):
    # Listeleme sayfasında gösterilecek alanlar
    list_display = (
        'talep_basligi',
        'talep_eden_kullanici',
        'ders',
        'beklenen_seviye',
        'talep_durumu',
        'olusturulma_tarihi',
        'guncellenme_tarihi'
    )
    # Filtreleme seçenekleri
    list_filter = ('talep_durumu', 'beklenen_seviye', 'ders', 'talep_eden_kullanici__universite')
    # Arama yapılabilecek alanlar
    search_fields = (
        'talep_basligi',
        'detayli_aciklama',
        'ders__ders_adi',
        'talep_eden_kullanici__user__username',
        'talep_eden_kullanici__user__first_name',
        'talep_eden_kullanici__user__last_name'
    )
    # ForeignKey alanları için otomatik tamamlama kutuları
    autocomplete_fields = ['talep_eden_kullanici', 'ders']
    # Sadece okunabilir alanlar
    readonly_fields = ('olusturulma_tarihi', 'guncellenme_tarihi')
    # Alanların gruplandırılması ve düzeni
    fieldsets = (
        (None, {
            'fields': ('talep_eden_kullanici', 'ders', 'talep_basligi', 'detayli_aciklama')
        }),
        ('Detaylar ve Tercihler', {
            'fields': ('beklenen_seviye', 'teklif_edilen_karsilik', 'mekan_tercihi', 'zaman_tercihi')
        }),
        ('Durum ve Zaman Bilgisi', {
            'fields': ('talep_durumu', 'olusturulma_tarihi', 'guncellenme_tarihi')
        }),
    )
    # Varsayılan sıralama
    ordering = ('-olusturulma_tarihi',)

    # Queryset'i optimize etmek için ilgili ForeignKey alanlarını önceden yükler
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('talep_eden_kullanici__user', 'ders')

# Eğitmen Başvuruları modelinin admin panelindeki görünümünü yapılandırır
@admin.register(EgitmenBasvurusu)
class EgitmenBasvurusuAdmin(admin.ModelAdmin):
    # Listeleme sayfasında gösterilecek alanlar (özel link fonksiyonları dahil)
    list_display = ('ders_istegi_link', 'basvuran_egitmen_link', 'basvuru_durumu', 'basvuru_tarihi')
    # Filtreleme seçenekleri
    list_filter = ('basvuru_durumu', 'basvuran_egitmen__universite', 'ders_istegi__ders')
    # Arama yapılabilecek alanlar
    search_fields = (
        'ders_istegi__talep_basligi',
        'basvuran_egitmen__user__username',
        'basvuran_egitmen__user__first_name',
        'basvuru_mesaji'
    )
    # ForeignKey alanları için otomatik tamamlama kutuları
    autocomplete_fields = ['ders_istegi', 'basvuran_egitmen']
    # Sadece okunabilir alanlar
    readonly_fields = ('basvuru_tarihi',)
    # Varsayılan sıralama
    ordering = ('-basvuru_tarihi',)

    # Alanların gruplandırılması ve düzeni
    fieldsets = (
        (None, {
            'fields': ('ders_istegi', 'basvuran_egitmen', 'basvuru_mesaji', 'basvuru_durumu')
        }),
        ('Zaman Bilgisi', {
            'fields': ('basvuru_tarihi',)
        }),
    )

    # Ders isteği detayına link oluşturan fonksiyon
    def ders_istegi_link(self, obj):
        link = reverse("admin:talepler_dersistegi_change", args=[obj.ders_istegi.id])
        return format_html('<a href="{}">{}</a>', link, obj.ders_istegi.talep_basligi)
    # Admin listesinde gösterilecek sütun başlığı
    ders_istegi_link.short_description = "Ders İsteği"

    # Başvuran eğitmenin profiline link oluşturan fonksiyon
    def basvuran_egitmen_link(self, obj):
        # KullaniciProfili admin linki için app_label ve model_name doğru olmalı
        link = reverse("admin:kullanicilar_kullaniciprofili_change", args=[obj.basvuran_egitmen.id])
        return format_html('<a href="{}">{}</a>', link, obj.basvuran_egitmen.user.username)
    # Admin listesinde gösterilecek sütun başlığı
    basvuran_egitmen_link.short_description = "Başvuran Eğitmen"

    # Queryset'i optimize etmek için ilgili ForeignKey alanlarını önceden yükler
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'ders_istegi__talep_eden_kullanici__user',
            'basvuran_egitmen__user',
            'ders_istegi__ders'
        )
