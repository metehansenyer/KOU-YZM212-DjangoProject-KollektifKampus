from django.views.generic import ListView
from django.db.models import Count, Q
from talepler.models import DersIstegi
from kullanicilar.models import KullaniciProfili
from django.contrib.auth.models import User
from dersler.models import Ders
from datetime import datetime

class HomePageView(ListView):
    model = DersIstegi
    template_name = "home.html"
    context_object_name = 'ders_talepleri'
    paginate_by = 10

    def get_queryset(self):
        # Aktif durumdaki ders taleplerini çek, ilgili kullanıcı, ders ve eğitmen bilgilerini önceden yükle
        queryset = DersIstegi.objects.filter(talep_durumu='AKTIF').select_related(
            'talep_eden_kullanici__user', 'ders', 'atanan_egitmen__user'
        )

        # GET parametrelerinden arama terimini al
        arama_terimi = self.request.GET.get('arama', '')
        # Arama terimi varsa, başlık, açıklama veya kullanıcı adına göre filtrele
        if arama_terimi:
            queryset = queryset.filter(
                Q(talep_basligi__icontains=arama_terimi) |
                Q(detayli_aciklama__icontains=arama_terimi) |
                Q(talep_eden_kullanici__user__username__icontains=arama_terimi)
            )

        # GET parametrelerinden kategori bilgisini al
        kategori = self.request.GET.get('kategori', '')
        # Kategori varsa, dersin kategorisine göre filtrele
        if kategori:
            queryset = queryset.filter(ders__kategori=kategori)

        # GET parametrelerinden seviye bilgisini al
        seviye = self.request.GET.get('seviye', '')
        # Seviye varsa, beklenen seviyeye göre filtrele
        if seviye:
            queryset = queryset.filter(beklenen_seviye=seviye)

        # GET parametrelerinden tarih aralığı bilgilerini al
        tarih_baslangic = self.request.GET.get('tarih_baslangic', '')
        tarih_bitis = self.request.GET.get('tarih_bitis', '')

        # Başlangıç tarihi varsa, filtrele
        if tarih_baslangic:
            try:
                # Tarih formatını ayrıştır
                baslangic = datetime.strptime(tarih_baslangic, '%Y-%m-%d')
                # Oluşturulma tarihi başlangıç tarihinden büyük veya eşit olanları filtrele
                queryset = queryset.filter(olusturulma_tarihi__gte=baslangic)
            except ValueError:
                # Geçersiz tarih formatı durumunda hata yoksayılır, filtre uygulanmaz
                pass

        # Bitiş tarihi varsa, filtrele
        if tarih_bitis:
            try:
                # Tarih formatını ayrıştır
                bitis = datetime.strptime(tarih_bitis, '%Y-%m-%d')
                # Bitiş tarihini günün sonuna ayarla (23:59:59)
                bitis = bitis.replace(hour=23, minute=59, second=59)
                # Oluşturulma tarihi bitiş tarihinden küçük veya eşit olanları filtrele
                queryset = queryset.filter(olusturulma_tarihi__lte=bitis)
            except ValueError:
                # Geçersiz tarih formatı durumunda hata yoksayılır, filtre uygulanmaz
                pass

        # GET parametrelerinden sıralama bilgisini al, varsayılan olarak oluşturulma tarihine göre tersten sırala
        siralama = self.request.GET.get('siralama', '-olusturulma_tarihi')
        # Sonuçları belirtilen kritere göre sırala
        queryset = queryset.order_by(siralama)

        return queryset

    def get_context_data(self, **kwargs):
        # Üst sınıfın context verilerini al
        context = super().get_context_data(**kwargs)

        # Filtreleme seçenekleri için mevcut ders kategorilerini çek ve context'e ekle
        context['kategoriler'] = Ders.objects.values_list('kategori', flat=True).distinct().order_by('kategori')
        # Seviye seçeneklerini context'e ekle
        context['seviyeler'] = dict(DersIstegi.SEVIYE_CHOICES)

        return context