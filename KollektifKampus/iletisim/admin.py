from django.contrib import admin
from .models import Sohbet, Mesaj

class MesajInline(admin.TabularInline):
    # Sohbet detay sayfasında mesajları göstermek için inline sınıfı
    model = Mesaj
    # Yeni mesaj eklemek için boş form sayısı (0 olarak ayarlanmış)
    extra = 0
    # Admin panelinden düzenlenemeyecek alanlar
    readonly_fields = ('gonderen_kullanici', 'gonderilme_tarihi', 'icerik', 'okundu_bilgisi')
    # Admin panelinden mesaj silmeyi engelle
    can_delete = False
    # Mesajları gönderilme tarihine göre sırala
    ordering = ('gonderilme_tarihi',)

    def has_add_permission(self, request, obj=None):
        # Admin panelinden yeni mesaj eklemeyi engelle
        return False

@admin.register(Sohbet)
class SohbetAdmin(admin.ModelAdmin):
    # Sohbet listeleme sayfasında gösterilecek alanlar
    list_display = ('__str__', 'ders_istegi_link', 'katilimci_listesi', 'olusturulma_tarihi')
    # Sohbet listeleme sayfasında filtreleme seçenekleri
    list_filter = ('olusturulma_tarihi',)
    # Sohbet arama alanları
    search_fields = ('ders_istegi__talep_basligi', 'katilimcilar__user__username')
    # Otomatik tamamlama özelliği kullanılacak alanlar
    autocomplete_fields = ['ders_istegi', 'katilimcilar']
    # Admin panelinden düzenlenemeyecek alanlar
    readonly_fields = ('olusturulma_tarihi',)
    # Sohbet detay sayfasında gösterilecek inline sınıfları
    inlines = [MesajInline]
    # Sohbetleri oluşturulma tarihine göre tersten sırala
    ordering = ('-olusturulma_tarihi',)

    def ders_istegi_link(self, obj):
        # Ders isteği objesine admin panelinde link oluşturur
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.ders_istegi:
            link = reverse("admin:talepler_dersistegi_change", args=[obj.ders_istegi.id])
            return format_html('<a href="{}">{}</a>', link, obj.ders_istegi.talep_basligi)
        return "-"
    # ders_istegi_link fonksiyonunun admin panelindeki sütun başlığı
    ders_istegi_link.short_description = "Ders İsteği"

    def katilimci_listesi(self, obj):
        # Sohbet katılımcılarının kullanıcı adlarını listeler
        return ", ".join([k.user.username for k in obj.katilimcilar.all()])
    # katilimci_listesi fonksiyonunun admin panelindeki sütun başlığı
    katilimci_listesi.short_description = "Katılımcılar"

    def get_queryset(self, request):
        # Queryset'i optimize etmek için ilgili modelleri önceden yükler
        return super().get_queryset(request).prefetch_related('katilimcilar__user').select_related('ders_istegi')

@admin.register(Mesaj)
class MesajAdmin(admin.ModelAdmin):
    # Mesaj listeleme sayfasında gösterilecek alanlar
    list_display = ('sohbet_link', 'gonderen_kullanici_link', 'icerik_ozeti', 'gonderilme_tarihi', 'okundu_bilgisi')
    # Mesaj listeleme sayfasında filtreleme seçenekleri
    list_filter = ('okundu_bilgisi', 'gonderilme_tarihi', 'gonderen_kullanici__universite')
    # Mesaj arama alanları
    search_fields = ('icerik', 'gonderen_kullanici__user__username', 'sohbet__ders_istegi__talep_basligi')
    # Otomatik tamamlama özelliği kullanılacak alanlar
    autocomplete_fields = ['sohbet', 'gonderen_kullanici']
    # Admin panelinden düzenlenemeyecek alanlar
    readonly_fields = ('gonderilme_tarihi',)
    # Mesajları gönderilme tarihine göre tersten sırala
    ordering = ('-gonderilme_tarihi',)

    def sohbet_link(self, obj):
        # Mesajın ait olduğu sohbet objesine admin panelinde link oluşturur
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.sohbet:
            link = reverse("admin:iletisim_sohbet_change", args=[obj.sohbet.id])
            return format_html('<a href="{}">Sohbet #{}</a>', link, obj.sohbet.id)
        return "-"
    # sohbet_link fonksiyonunun admin panelindeki sütun başlığı
    sohbet_link.short_description = "Sohbet"

    def gonderen_kullanici_link(self, obj):
        # Mesajı gönderen kullanıcı profiline admin panelinde link oluşturur
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.gonderen_kullanici:
            link = reverse("admin:kullanicilar_kullaniciprofili_change", args=[obj.gonderen_kullanici.id])
            return format_html('<a href="{}">{}</a>', link, obj.gonderen_kullanici.user.username)
        return "Bilinmeyen"
    # gonderen_kullanici_link fonksiyonunun admin panelindeki sütun başlığı
    gonderen_kullanici_link.short_description = "Gönderen"

    def icerik_ozeti(self, obj):
        # Mesaj içeriğinin ilk 50 karakterini gösterir
        return obj.icerik[:50] + '...' if len(obj.icerik) > 50 else obj.icerik
    # icerik_ozeti fonksiyonunun admin panelindeki sütun başlığı
    icerik_ozeti.short_description = "İçerik Özeti"

    def get_queryset(self, request):
        # Queryset'i optimize etmek için ilgili modelleri önceden yükler
        return super().get_queryset(request).select_related('sohbet__ders_istegi', 'gonderen_kullanici__user')
