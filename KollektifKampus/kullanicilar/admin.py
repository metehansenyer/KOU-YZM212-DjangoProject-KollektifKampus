from django.contrib import admin
from .models import KullaniciProfili, EgitmenBasvuruFormu

# KullaniciProfili modelinin admin arayüzü yapılandırması
class KullaniciProfiliAdmin(admin.ModelAdmin):
    # Admin listeleme sayfasında gösterilecek alanlar
    list_display = ('user', 'adi_soyadi', 'universite', 'bolum', 'kullanici_rolu', 'ban_durumu')
    # Admin listeleme sayfasında filtreleme seçenekleri
    list_filter = ('kullanici_rolu', 'ban_durumu', 'universite')
    # Admin listeleme sayfasında arama yapılabilecek alanlar
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'universite', 'bolum')

# EgitmenBasvuruFormu modelinin admin arayüzü yapılandırması
class EgitmenBasvuruFormuAdmin(admin.ModelAdmin):
    # Admin listeleme sayfasında gösterilecek alanlar
    list_display = ('kullanici', 'basvuru_durumu', 'basvuru_tarihi', 'degerlendiren_moderator')
    # Admin listeleme sayfasında filtreleme seçenekleri
    list_filter = ('basvuru_durumu', 'basvuru_tarihi')
    # Admin listeleme sayfasında arama yapılabilecek alanlar
    search_fields = ('kullanici__user__username', 'uzmanlik_alanlari')
    # Admin düzenleme sayfasında sadece okunabilir alanlar
    readonly_fields = ('basvuru_tarihi',)

# KullaniciProfili modelini özel admin sınıfı ile kaydet
admin.site.register(KullaniciProfili, KullaniciProfiliAdmin)
# EgitmenBasvuruFormu modelini özel admin sınıfı ile kaydet
admin.site.register(EgitmenBasvuruFormu, EgitmenBasvuruFormuAdmin)
