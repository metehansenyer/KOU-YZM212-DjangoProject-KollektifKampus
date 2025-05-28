from django.contrib import admin
from .models import Degerlendirme

# Degerlendirme modelini Django admin paneline kaydeder
@admin.register(Degerlendirme)
class DegerlendirmeAdmin(admin.ModelAdmin):
    # Değerlendirme listeleme sayfasında gösterilecek alanlar
    list_display = (
        'ders_istegi_link', # Ders isteği başlığına link
        'degerlendiren_kullanici_link', # Değerlendiren kullanıcı adına link
        'degerlendirilen_kullanici_link', # Değerlendirilen kullanıcı adına link
        'puan', # Verilen puan
        'yorum_ozeti', # Yorumun kısa özeti
        'degerlendirme_tarihi' # Değerlendirme tarihi
    )
    # Listeleme sayfasının sağ tarafına filtre ekler
    list_filter = ('puan', 'degerlendirme_tarihi', 'degerlendiren_kullanici__universite', 'degerlendirilen_kullanici__universite')
    # Arama çubuğunda aranabilecek alanlar
    search_fields = (
        'ders_istegi__talep_basligi', # Ders isteği başlığına göre arama
        'degerlendiren_kullanici__user__username', # Değerlendiren kullanıcının kullanıcı adına göre arama
        'degerlendirilen_kullanici__user__username', # Değerlendirilen kullanıcının kullanıcı adına göre arama
        'yorum' # Yorum içeriğine göre arama
    )
    # İlişkili alanlar için otomatik tamamlama özelliği ekler
    autocomplete_fields = ['ders_istegi', 'degerlendiren_kullanici', 'degerlendirilen_kullanici']
    # Sadece okunabilir alanlar
    readonly_fields = ('degerlendirme_tarihi',)
    # Varsayılan sıralama
    ordering = ('-degerlendirme_tarihi',)

    # Admin formunda alanları gruplar
    fieldsets = (
        (None, {
            'fields': ('ders_istegi', 'degerlendiren_kullanici', 'degerlendirilen_kullanici')
        }),
        ('Değerlendirme Detayları', {
            'fields': ('puan', 'yorum')
        }),
        ('Zaman Bilgisi', {
            'fields': ('degerlendirme_tarihi',)
        }),
    )

    # Ders isteği başlığına admin panelinde link oluşturan metod
    def ders_istegi_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.ders_istegi:
            # Ders isteği detay sayfasına admin linki oluşturur
            link = reverse("admin:talepler_dersistegi_change", args=[obj.ders_istegi.id])
            # HTML formatında link döndürür
            return format_html('<a href="{}">{}</a>', link, obj.ders_istegi.talep_basligi)
        return "-"
    # Metodun admin panelindeki sütun başlığını belirler
    ders_istegi_link.short_description = "Ders İsteği"

    # Değerlendiren kullanıcı adına admin panelinde link oluşturan metod
    def degerlendiren_kullanici_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.degerlendiren_kullanici:
            # Kullanıcı profili detay sayfasına admin linki oluşturur
            link = reverse("admin:kullanicilar_kullaniciprofili_change", args=[obj.degerlendiren_kullanici.id])
            # HTML formatında link döndürür
            return format_html('<a href="{}">{}</a>', link, obj.degerlendiren_kullanici.user.username)
        return "-"
    # Metodun admin panelindeki sütun başlığını belirler
    degerlendiren_kullanici_link.short_description = "Değerlendiren Kullanıcı"

    # Değerlendirilen kullanıcı adına admin panelinde link oluşturan metod
    def degerlendirilen_kullanici_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.degerlendirilen_kullanici:
            # Kullanıcı profili detay sayfasına admin linki oluşturur
            link = reverse("admin:kullanicilar_kullaniciprofili_change", args=[obj.degerlendirilen_kullanici.id])
            # HTML formatında link döndürür
            return format_html('<a href="{}">{}</a>', link, obj.degerlendirilen_kullanici.user.username)
        return "-"
    # Metodun admin panelindeki sütun başlığını belirler
    degerlendirilen_kullanici_link.short_description = "Değerlendirilen Kullanıcı"

    # Yorumun ilk 50 karakterini gösteren ve sonuna '...' ekleyen metod
    def yorum_ozeti(self, obj):
        return obj.yorum[:50] + '...' if len(obj.yorum) > 50 else obj.yorum
    # Metodun admin panelindeki sütun başlığını belirler
    yorum_ozeti.short_description = "Yorum Özeti"

    # Performansı artırmak için ilişkili objeleri önceden yükleyen metod
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'ders_istegi', # Ders isteği objesini yükler
            'degerlendiren_kullanici__user', # Değerlendiren kullanıcının user objesini yükler
            'degerlendirilen_kullanici__user' # Değerlendirilen kullanıcının user objesini yükler
        )
