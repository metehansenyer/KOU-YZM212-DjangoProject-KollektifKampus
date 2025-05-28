from django.urls import path
from . import views # Talepler uygulaması view'larını içe aktar

app_name = 'talepler' # Uygulama için URL isimlendirme alanı

urlpatterns = [
    # Tüm ders isteklerini listeleme sayfası
    path('', views.DersIstegiListView.as_view(), name='ders_istekleri_listesi'),
    # Yeni ders isteği oluşturma sayfası
    path('olustur/', views.DersIstegiCreateView.as_view(), name='ders_istegi_olustur'),
    # Belirli bir ders isteğinin detay sayfası
    path('<int:pk>/', views.DersIstegiDetailView.as_view(), name='ders_istegi_detay'),
    # Belirli bir ders isteğini güncelleme sayfası
    path('<int:pk>/guncelle/', views.DersIstegiUpdateView.as_view(), name='ders_istegi_guncelle'),
    # Belirli bir ders isteğini silme işlemi
    path('<int:pk>/sil/', views.DersIstegiDeleteView.as_view(), name='ders_istegi_sil'),
    # Bir ders isteğine eğitmen olarak başvurma işlemi
    path('<int:ders_istegi_id>/basvur/', views.egitmen_basvurusu_yap, name='egitmen_basvurusu_yap'),
    # Bir eğitmen başvurusunu yönetme (kabul/red) işlemi
    path('basvuru/<int:basvuru_id>/yonet/', views.egitmen_basvuru_yonet, name='egitmen_basvuru_yonet'),
    # Yapılan bir eğitmen başvurusunu geri çekme işlemi
    path('basvuru/<int:basvuru_id>/geri-cek/', views.egitmen_basvurusu_geri_cek, name='egitmen_basvurusu_geri_cek'),
    # Bir ders isteğini tamamlama işlemi (öğrenci veya eğitmen tarafından)
    path('<int:ders_istegi_id>/tamamla/', views.ders_istegi_tamamla, name='ders_istegi_tamamla'),
]