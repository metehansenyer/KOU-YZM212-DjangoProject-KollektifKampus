from django.urls import path
from . import views

# 'iletisim' uygulaması için URL yapılandırması
app_name = 'iletisim'

urlpatterns = [
    # Kullanıcının katıldığı sohbetlerin listelendiği sayfa
    path('sohbetlerim/', views.kullanici_sohbetleri, name='kullanici_sohbetleri'),

    # Belirli bir sohbetin detayını ve mesajlarını gösteren sayfa
    path('sohbet/<int:sohbet_id>/', views.sohbet_detay, name='sohbet_detay'),

    # Belirli bir sohbete mesaj göndermek için kullanılan AJAX endpoint'i
    path('mesaj-gonder/<int:sohbet_id>/', views.mesaj_gonder, name='mesaj_gonder'),

    # Yeni bir sohbet başlatmak için kullanılan endpoint (genellikle otomatik tetiklenir)
    path('sohbet-baslat/<int:ders_istegi_id>/', views.sohbet_baslat, name='sohbet_baslat'),

    # Kullanıcının okunmamış mesaj sayısını almak için kullanılan endpoint
    path('okunmayan-mesaj-sayisi/', views.okunmayan_mesaj_sayisi, name='okunmayan_mesaj_sayisi'),

    # Kullanıcının son mesajlarını almak için kullanılan endpoint
    path('son-mesajlar/', views.son_mesajlar, name='son_mesajlar'),
]