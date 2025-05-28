from django.urls import path
from .views import KullaniciKayitView, KullaniciProfiliDetayView, KullaniciProfiliGuncelleView, SifreSifirlamaView, SifreSifirlamaOnayView, SifreSifirlamaTamamView, SifreSifirlamaBasariView, kullanici_rolu_degistir, egitmen_basvurusu_view, egitmen_basvurusu_detay
from django.contrib.auth import views as auth_views

# Uygulama adını tanımla
app_name = 'kullanicilar'

# URL desenleri listesi
urlpatterns = [
    # Kullanıcı giriş sayfası
    path('giris/', auth_views.LoginView.as_view(template_name='kullanicilar/giris.html'), name='giris'),
    # Kullanıcı çıkış işlemi
    path('cikis/', auth_views.LogoutView.as_view(), name='cikis'),
    # Kullanıcı profilini güncelleme sayfası
    path('profil/duzenle/', KullaniciProfiliGuncelleView.as_view(), name='profil_guncelle'),
    # Yeni kullanıcı kayıt sayfası
    path('kayit/', KullaniciKayitView.as_view(), name='kayit_ol'),
    # Kullanıcı profil detay sayfası (kullanıcı adına göre)
    path('profil/<str:username>/', KullaniciProfiliDetayView.as_view(), name='profil_detay'),
    # Kullanıcı rolünü değiştirme işlemi (admin/moderatör için)
    path('profil/<str:username>/rol-degistir/', kullanici_rolu_degistir, name='kullanici_rolu_degistir'),

    # Şifre sıfırlama akışı URL'leri
    # Şifre sıfırlama isteği sayfası
    path('sifre-sifirla/', SifreSifirlamaView.as_view(), name='sifre_sifirla'),
    # Şifre sıfırlama onay sayfası (e-posta linkinden gelen)
    path('sifre-sifirla/onay/<uidb64>/<token>/', SifreSifirlamaOnayView.as_view(), name='sifre_sifirla_onay'),
    # Şifre sıfırlama tamamlandı sayfası
    path('sifre-sifirla/tamam/', SifreSifirlamaTamamView.as_view(), name='sifre_sifirla_tamam'),
    # Şifre sıfırlama başarı sayfası
    path('sifre-sifirla/basari/', SifreSifirlamaBasariView.as_view(), name='sifre_sifirla_basari'),

    # Eğitmen başvuru URL'leri
    # Eğitmen başvuru formu sayfası
    path('egitmen-basvurusu/', egitmen_basvurusu_view, name='egitmen_basvurusu'),
    # Eğitmen başvuru detay sayfası (moderatör/admin için)
    path('egitmen-basvurusu/<int:basvuru_id>/detay/', egitmen_basvurusu_detay, name='egitmen_basvurusu_detay'),
]