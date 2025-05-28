from django.urls import path
from . import views

# Bu uygulama için URL isim alanını tanımlar.
app_name = 'geribildirim'
 
# Uygulama URL desenlerini tanımlar.
urlpatterns = [
    # Belirli bir ders isteği için değerlendirme oluşturma sayfası URL'si.
    # <int:ders_istegi_id> kısmı, URL'den ders isteği ID'sini yakalar.
    path('degerlendirme-olustur/<int:ders_istegi_id>/', views.degerlendirme_olustur, name='degerlendirme_olustur'),
    
    # Belirli bir kullanıcının aldığı değerlendirmeleri listeleme sayfası URL'si.
    # <str:username> kısmı, URL'den kullanıcı adını yakalar.
    path('kullanici-degerlendirmeleri/<str:username>/', views.kullanici_degerlendirmeleri, name='kullanici_degerlendirmeleri'),
    
    # En iyi eğitmenleri listeleme sayfası URL'si.
    path('en-iyi-egitmenler/', views.en_iyi_egitmenler, name='en_iyi_egitmenler'),
] 