from django.urls import path
from . import views

# Bu uygulama için URL isim alanı
app_name = 'moderasyon'

# Moderasyon uygulaması URL kalıpları
urlpatterns = [
    # Kullanıcı engelleme ve engel kaldırma işlemleri için URL'ler
    # Belirli bir kullanıcıyı engelleme
    path('kullanici/<int:user_id>/engelle/', views.kullanici_engelle, name='kullanici_engelle'),
    # Belirli bir kullanıcının engelini kaldırma
    path('kullanici/<int:user_id>/engel-kaldir/', views.kullanici_engel_kaldir, name='kullanici_engel_kaldir'),

    # Moderatör paneli ve alt sayfaları için URL'ler
    # Moderatör paneli ana sayfası
    path('panel/', views.moderator_panel, name='panel_anasayfa'),
    # Tüm kullanıcıları listeleme sayfası
    path('panel/kullanicilar/', views.KullaniciListesiView.as_view(), name='kullanici_listesi'),
    # Aktif ders isteklerini listeleme sayfası
    path('panel/ders-istekleri/', views.AktifDersIstekleriView.as_view(), name='aktif_ders_istekleri'),
    # Eğitmen başvurularını listeleme sayfası
    path('panel/egitmen-basvurulari/', views.EgitmenBasvurulariView.as_view(), name='egitmen_basvurulari'),
    # Eğitmen rol başvurularını listeleme sayfası
    path('panel/rol-basvurulari/', views.EgitmenRolBasvurulariListView.as_view(), name='egitmen_rol_basvurulari'),
    # Engellenmiş kullanıcıları listeleme sayfası
    path('panel/engelli-kullanicilar/', views.EngelliKullanicilarView.as_view(), name='engelli_kullanicilar'),

    # Veri yönetimi (içeri/dışarı aktarma) işlemleri için URL'ler
    # Veri yönetimi ana sayfası
    path('panel/veri-yonetimi/', views.veri_yonetimi, name='veri_yonetimi'),
    # Veriyi dışarı aktarma işlemi
    path('panel/veri-disari-aktar/', views.veri_disari_aktar, name='veri_disari_aktar'),
    # Veriyi içeri aktarma işlemi
    path('panel/veri-iceri-aktar/', views.veri_iceri_aktar, name='veri_iceri_aktar'),

    # Ders isteği işlemleri için URL'ler
    # Belirli bir ders isteğini inceleme
    path('ders-istegi/<int:ders_istegi_id>/incele/', views.ders_istegi_incele, name='ders_istegi_incele'),
    # Belirli bir ders isteğini kapatma
    path('ders-istegi/<int:ders_istegi_id>/kapat/', views.ders_istegi_kapat, name='ders_istegi_kapat'),

    # Eğitmen rol başvuruları işlemleri için URL'ler
    # Belirli bir eğitmen rol başvurusunu değerlendirme
    path('egitmen-rol-basvurusu/<int:basvuru_id>/degerlendir/', views.egitmen_rol_basvurusu_degerlendir, name='egitmen_rol_basvurusu_degerlendir'),
    # Belirli bir eğitmen rol başvurusunu hızlıca onaylama
    path('egitmen-rol-basvurusu/<int:basvuru_id>/onayla/', views.egitmen_rol_basvurusu_onayla, name='egitmen_rol_basvurusu_onayla'),
    # Belirli bir eğitmen rol başvurusunu reddetme
    path('egitmen-rol-basvurusu/<int:basvuru_id>/reddet/', views.egitmen_rol_basvurusu_reddet, name='egitmen_rol_basvurusu_reddet'),
]