from django.contrib import admin
from django.urls import path, include
from .views import HomePageView
from django.views.generic import RedirectView

# Projenin ana URL yapılandırması
urlpatterns = [
    # Django admin paneli URL'si
    path('admin/', admin.site.urls),

    # Ana sayfa URL'si, HomePageView sınıfını kullanır
    path('', HomePageView.as_view(), name='home'),

    # 'talepler' uygulamasının URL'lerini dahil et, ama ana listesi sayfasını ana sayfaya yönlendir
    path('talepler/', include('talepler.urls')),

    # Eski '/login/' URL'sini 'kullanicilar:giris' adlı yeni URL'ye yönlendir
    path('login/', RedirectView.as_view(pattern_name='kullanicilar:giris'), name='login'),

    # Django'nun varsayılan kimlik doğrulama URL'lerini dahil et (login, logout, password reset vb.)
    path('accounts/', include('django.contrib.auth.urls')),

    # 'kullanicilar' uygulamasının URL'lerini dahil et
    path('kullanicilar/', include('kullanicilar.urls')),

    # 'geribildirim' uygulamasının URL'lerini dahil et
    path('geribildirim/', include('geribildirim.urls')),

    # 'iletisim' uygulamasının URL'lerini 'iletisim' namespace'i ile dahil et
    path('iletisim/', include('iletisim.urls', namespace='iletisim')),

    # 'moderasyon' uygulamasının URL'lerini dahil et
    path('moderasyon/', include('moderasyon.urls')),
]
