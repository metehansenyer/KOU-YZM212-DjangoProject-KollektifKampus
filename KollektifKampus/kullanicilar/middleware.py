from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse

class KullaniciEngelKontrolMiddleware:
    # Kullanıcının engellenme durumunu kontrol eden middleware.
    # Eğer kullanıcı engellenmişse ve engel süresi dolmamışsa, oturumu kapatır ve bilgilendirme mesajı gösterir.
    # Engel süresi dolmuşsa, engeli kaldırır.
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # İstek işlenmeden önce kullanıcı kontrolü yapılır
        # Kullanıcı giriş yapmışsa ve profil bilgisi varsa devam et
        if request.user.is_authenticated and hasattr(request.user, "profil"):
            profil = request.user.profil
            
            # Kullanıcının engelli olup olmadığını kontrol et
            if profil.ban_durumu:
                # Engel süresinin dolup dolmadığını kontrol et
                # ban_bitis_tarihi None değilse ve şu anki zamandan küçük veya eşitse süre dolmuş demektir
                if profil.ban_bitis_tarihi and profil.ban_bitis_tarihi <= timezone.now():
                    # Engel süresi dolmuş, engeli kaldır
                    profil.ban_durumu = False
                    profil.ban_bitis_tarihi = None
                    profil.save()
                else:
                    # Kullanıcı hala engelli
                    ban_suresi = ""
                    # Eğer engel bitiş tarihi belirlenmişse kalan süreyi hesapla
                    if profil.ban_bitis_tarihi:
                        kalan_sure = profil.ban_bitis_tarihi - timezone.now()
                        kalan_gun = kalan_sure.days
                        # Kalan gün 0'dan büyükse mesajı ekle
                        if kalan_gun > 0:
                            ban_suresi = f" Engel sürenizin bitmesine {kalan_gun} gün kaldı."
                    
                    # Kullanıcının oturumunu kapat
                    logout(request)
                    # Engellenme mesajını göster
                    messages.error(request, f"Hesabınız engellenmiştir.{ban_suresi} Detaylı bilgi için iletişime geçiniz.")
                    # Giriş sayfasına yönlendir
                    return redirect("kullanicilar:giris")
        
        # İstek işlendikten sonra yanıtı döndür
        response = self.get_response(request)
        return response