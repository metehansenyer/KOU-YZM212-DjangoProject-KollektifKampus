from django.contrib import admin
from .models import Ders

# Ders modelini Django admin paneline kaydetmek için
@admin.register(Ders)
class DersAdmin(admin.ModelAdmin):
    # Admin listeleme sayfasında gösterilecek alanlar
    list_display = ('ders_adi', 'kategori', 'aktif_mi', 'olusturulma_tarihi', 'guncellenme_tarihi')

    # Admin listeleme sayfasında filtreleme için kullanılacak alanlar
    list_filter = ('aktif_mi', 'kategori')

    # Admin listeleme sayfasında arama yapmak için kullanılacak alanlar
    search_fields = ('ders_adi', 'kategori', 'aciklama')

    # Admin listeleme sayfasında doğrudan düzenlenebilir alanlar
    list_editable = ('aktif_mi', 'kategori')

    # Admin listeleme sayfasındaki varsayılan sıralama
    ordering = ('ders_adi',)
