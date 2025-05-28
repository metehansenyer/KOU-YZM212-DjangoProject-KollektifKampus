from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy

# Kullanıcının eğitmen, moderatör veya admin rolüne sahip olmasını gerektiren mixin
class EgitmenRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Kullanıcının giriş yapmış olduğunu, profilinin olduğunu ve eğitmen yetkisine sahip olduğunu kontrol et
        return self.request.user.is_authenticated and hasattr(self.request.user, 'profil') and self.request.user.profil.is_egitmen()

    def handle_no_permission(self):
        # Yetki yoksa hata mesajı göster ve ana sayfaya yönlendir
        messages.error(self.request, "Bu sayfaya erişim için eğitmen yetkisi gerekmektedir.")
        return redirect('home')

# Sadece moderatör ve admin rolündeki kullanıcıların erişebileceği mixin
class ModeratorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Kullanıcının giriş yapmış olduğunu ve moderatör yetkisine sahip olduğunu kontrol et
        return self.request.user.is_authenticated and self.request.user.profil.is_moderator()

    def handle_no_permission(self):
        # Yetki yoksa hata mesajı göster ve ana sayfaya yönlendir
        messages.error(self.request, "Bu sayfaya erişim için moderatör yetkisi gerekmektedir.")
        return redirect('home')

# Sadece admin rolündeki kullanıcıların erişebileceği mixin
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Kullanıcının giriş yapmış olduğunu ve admin yetkisine sahip olduğunu kontrol et
        return self.request.user.is_authenticated and self.request.user.profil.is_admin()

    def handle_no_permission(self):
        # Yetki yoksa hata mesajı göster ve ana sayfaya yönlendir
        messages.error(self.request, "Bu sayfaya erişim için yönetici yetkisi gerekmektedir.")
        return redirect('home')

# İçerik sahibi, moderatör veya admin rolündeki kullanıcıların erişebileceği mixin
# Bu mixin'i kullanan view'larda get_object() metodu olmalı
class ContentOwnerOrModeratorRequiredMixin(UserPassesTestMixin):
    # İçerik sahibi kullanıcıyı belirten model field adı (varsayılan)
    owner_field = 'talep_eden_kullanici'

    def test_func(self):
        # Kullanıcı giriş yapmamışsa erişimi engelle
        if not self.request.user.is_authenticated:
            return False

        # Kullanıcının profili yoksa erişimi engelle
        if not hasattr(self.request.user, 'profil'):
            return False

        # Kullanıcı moderatör veya admin ise erişime izin ver
        if self.request.user.profil.is_moderator():
            return True

        # İçerik sahibi kontrolü
        try:
            obj = self.get_object()
        except AttributeError:
            # get_object() metodu yoksa veya hata verirse erişimi engelle
            return False

        # İçerik sahibi field'ı objede var mı kontrol et
        if hasattr(obj, self.owner_field):
            owner = getattr(obj, self.owner_field)

            # owner bir KullaniciProfili nesnesi ise, ilişkili User nesnesini kontrol et
            if hasattr(owner, 'user'):
                return owner.user == self.request.user
            # owner direkt bir User nesnesi ise, direkt User nesnesini kontrol et
            else:
                return owner == self.request.user

        # Belirtilen owner_field objede yoksa erişimi engelle
        return False

    def handle_no_permission(self):
        # Yetki yoksa hata mesajı göster ve ana sayfaya yönlendir
        messages.error(self.request, "Bu içeriği görüntüleme veya düzenleme yetkiniz bulunmamaktadır.")
        return redirect('home')