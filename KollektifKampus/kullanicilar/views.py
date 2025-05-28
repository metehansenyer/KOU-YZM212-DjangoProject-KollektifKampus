from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import KullaniciKayitFormu, KullaniciProfiliGuncelleForm, EgitmenBasvuruForm
from .models import KullaniciProfili, EgitmenBasvuruFormu
from talepler.models import DersIstegi, EgitmenBasvurusu
from geribildirim.models import Degerlendirme

# Şifre sıfırlama işlemleri için kullanılan view sınıfları
class SifreSifirlamaView(SuccessMessageMixin, PasswordResetView):
    # Şifre sıfırlama formu için kullanılan şablon
    template_name = 'kullanicilar/sifre_sifirla.html'
    # Şifre sıfırlama e-postası için kullanılan şablon
    email_template_name = 'kullanicilar/sifre_sifirla_email.html'
    # Şifre sıfırlama e-postasının konu şablonu
    subject_template_name = 'kullanicilar/sifre_sifirla_konu.txt'
    # Başarılı şifre sıfırlama isteği sonrası yönlendirilecek URL
    success_url = reverse_lazy('kullanicilar:sifre_sifirla_tamam')
    # Başarılı işlem sonrası gösterilecek mesaj
    success_message = "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."

    # Form geçerli olduğunda çalışır
    def form_valid(self, form):
        email = form.cleaned_data["email"]
        # Girilen e-posta adresiyle ilişkili bir kullanıcı olup olmadığını kontrol et
        if not User.objects.filter(email=email).exists():
            # Kullanıcı bulunamazsa forma hata ekle
            form.add_error('email', ValidationError("Bu e-posta adresi ile ilişkili bir hesap bulunamadı."))
            # Hatalı formu tekrar render et
            return self.form_invalid(form)
        # Kullanıcı bulunursa varsayılan form_valid işlemini çağır
        return super().form_valid(form)

    # Form geçerli olmadığında çalışır
    def form_invalid(self, form):
        # Django'nun mesaj sistemini kullanmak yerine, form hatalarını doğrudan şablona gönderir
        return self.render_to_response(self.get_context_data(form=form))

# Şifre sıfırlama bağlantısına tıklandığında şifreyi onaylama view'ı
class SifreSifirlamaOnayView(PasswordResetConfirmView):
    # Şifre onaylama formu için kullanılan şablon
    template_name = 'kullanicilar/sifre_sifirla_onay.html'
    # Şifre başarıyla sıfırlandıktan sonra yönlendirilecek URL
    success_url = reverse_lazy('kullanicilar:sifre_sifirla_basari')

# Şifre sıfırlama e-postasının gönderildiğini bildiren view
class SifreSifirlamaTamamView(PasswordResetDoneView):
    # Tamamlandı sayfası için kullanılan şablon
    template_name = 'kullanicilar/sifre_sifirla_tamam.html'

# Şifre sıfırlama işleminin başarıyla tamamlandığını bildiren view
class SifreSifirlamaBasariView(PasswordResetCompleteView):
    # Başarı sayfası için kullanılan şablon
    template_name = 'kullanicilar/sifre_sifirla_basari.html'

# Yeni kullanıcı kaydı için kullanılan view
class KullaniciKayitView(SuccessMessageMixin, CreateView):
    # Kullanıcı kayıt formu
    form_class = KullaniciKayitFormu
    # Kayıt sayfası şablonu
    template_name = 'kullanicilar/kayit_ol.html'
    # Başarılı kayıt sonrası yönlendirilecek URL
    success_url = reverse_lazy('home')
    # Başarılı kayıt sonrası gösterilecek mesaj
    success_message = "Başarıyla kayıt oldunuz ve giriş yaptınız! Kollektif Kampüs'e hoş geldiniz."

    # Form geçerli olduğunda çalışır
    def form_valid(self, form):
        # Kullanıcıyı kaydet
        user = form.save()
        # Kullanıcıyı otomatik olarak giriş yap
        login(self.request, user)
        # Varsayılan form_valid işlemini çağır
        return super().form_valid(form)

    # Şablona gönderilecek ek bağlam verilerini sağlar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Form başlığını bağlama ekle
        context['form_baslik'] = "Yeni Kullanıcı Kaydı"
        return context

# Kullanıcı profil detaylarını görüntülemek için kullanılan view
class KullaniciProfiliDetayView(DetailView):
    # Kullanılacak model
    model = KullaniciProfili
    # Profil detay sayfası şablonu
    template_name = 'kullanicilar/profil_detay.html'
    # Şablonda kullanılacak bağlam değişkeni adı
    context_object_name = 'profil'
    # URL'deki slug olarak kullanılacak model alanı
    slug_field = 'user__username'
    # URL'deki slug parametresinin adı
    slug_url_kwarg = 'username'

    # Şablona gönderilecek ek bağlam verilerini sağlar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Profil sahibi kullanıcının aldığı değerlendirmelerin ortalama puanını hesapla
        degerlendirme_sayisi = self.object.aldigi_degerlendirmeler.count()
        if degerlendirme_sayisi > 0:
            ortalama_puan = self.object.aldigi_degerlendirmeler.aggregate(Avg('puan'))['puan__avg']
            context['ortalama_puan'] = round(ortalama_puan, 1) if ortalama_puan else None
            context['degerlendirme_sayisi'] = degerlendirme_sayisi
        
        # Profil sahibi kullanıcının oluşturduğu ders isteklerini al
        ders_istekleri = DersIstegi.objects.filter(
            talep_eden_kullanici=self.object
        ).select_related('ders', 'atanan_egitmen__user').order_by('-olusturulma_tarihi')
        context['ders_istekleri'] = ders_istekleri

        # Profil sahibi kullanıcının eğitmen olarak atandığı ders isteklerini al
        atanan_ders_istekleri = DersIstegi.objects.filter(
            atanan_egitmen=self.object
        ).select_related('talep_eden_kullanici__user', 'ders').order_by('-olusturulma_tarihi')

        # Verdiği derslerin detaylarını ve değerlendirme bilgilerini hesapla
        verdigi_dersler_detayli = []
        for ders in atanan_ders_istekleri:
            # Ders ile ilgili ortalama puan hesapla (şu anda None olarak ayarlanmış)
            ortalama_puan = None
            # Tamamlanmış dersler için değerlendirme kontrolü
            if ders.talep_durumu == 'TAMAMLANDI':
                degerlendirme = None # Bu kısım eksik veya hatalı görünüyor, değerlendirme bilgisi alınmıyor

            # Giriş yapmış kullanıcının bu dersi değerlendirip değerlendiremeyeceğini kontrol et
            kullanici_degerlendirme_yapabilir = (
                ders.talep_durumu == 'TAMAMLANDI' and
                not Degerlendirme.objects.filter(
                    ders_istegi=ders,
                    degerlendiren_kullanici=self.request.user.profil
                ).exists() if self.request.user.is_authenticated else False
            )

            # Ders detaylarını listeye ekle
            verdigi_dersler_detayli.append({
                'ders_istegi': ders,
                'ortalama_puan': ortalama_puan,
                'kullanici_degerlendirme_yapabilir': kullanici_degerlendirme_yapabilir
            })

        context['verdigi_dersler_detayli'] = verdigi_dersler_detayli

        # Eğer giriş yapmış kullanıcı kendi profiline bakıyorsa, eğitmen başvurularını al
        if self.request.user.is_authenticated and self.request.user.profil == self.object:
            # Kullanıcının yaptığı eğitmen başvurularını al (ders isteklerine yapılan başvurular)
            egitmen_basvurulari = EgitmenBasvurusu.objects.filter(
                basvuran_egitmen=self.object
            ).select_related(
                'ders_istegi',
                'ders_istegi__talep_eden_kullanici',
                'ders_istegi__talep_eden_kullanici__user'
            ).order_by('-basvuru_tarihi')
            context['egitmen_basvurulari'] = egitmen_basvurulari

        # Kullanıcı rolleri listesini bağlama ekle (admin kullanıcılar için rol değiştirme formunda kullanılabilir)
        context['kullanici_roller'] = KullaniciProfili.KULLANICI_ROLLER

        return context

# Kullanıcı profil bilgilerini güncellemek için kullanılan view
class KullaniciProfiliGuncelleView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    # Kullanılacak model
    model = KullaniciProfili
    # Profil güncelleme formu
    form_class = KullaniciProfiliGuncelleForm
    # Profil güncelleme sayfası şablonu
    template_name = 'kullanicilar/profil_guncelle.html'

    # Güncellenecek KullaniciProfili nesnesini döndürür (giriş yapmış kullanıcının profili)
    def get_object(self, queryset=None):
        return KullaniciProfili.objects.get(user=self.request.user)

    # Kullanıcının view'a erişim izni olup olmadığını kontrol eder (LoginRequiredMixin zaten giriş kontrolü yapar)
    def test_func(self):
        # Şu anda her zaman True döndürüyor, LoginRequiredMixin yeterli
        return True

    # Başarılı güncelleme sonrası yönlendirilecek URL
    def get_success_url(self):
        return reverse_lazy('kullanicilar:profil_detay', kwargs={'username': self.request.user.username})

    # Form geçerli olduğunda çalışır
    def form_valid(self, form):
        # Başarı mesajı göster
        messages.success(self.request, "Profiliniz başarıyla güncellendi.")
        # Varsayılan form_valid işlemini çağır
        return super().form_valid(form)

    # Şablona gönderilecek ek bağlam verilerini sağlar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Form başlığını bağlama ekle
        context['form_baslik'] = "Profil Bilgilerini Güncelle"
        return context

@login_required
def egitmen_basvurusu_view(request):
    # Kullanıcının zaten eğitmen rolüne sahip olup olmadığını kontrol et
    if request.user.profil.is_egitmen():
        messages.info(request, "Zaten eğitmen rolüne sahipsiniz.")
        # Eğitmense profil sayfasına yönlendir
        return redirect('kullanicilar:profil_detay', username=request.user.username)

    # Kullanıcının daha önce bekleyen bir eğitmen başvurusu olup olmadığını kontrol et
    bekleyen_basvuru = EgitmenBasvuruFormu.objects.filter(
        kullanici=request.user.profil,
        basvuru_durumu='BEKLEMEDE'
    ).first()

    # Bekleyen başvuru varsa kullanıcıyı bilgilendir ve başvuru detayına yönlendir
    if bekleyen_basvuru:
        messages.info(request, "Zaten bekleyen bir eğitmen başvurunuz bulunmaktadır. Başvurunuz değerlendirildikten sonra tekrar deneyebilirsiniz.")
        return redirect('kullanicilar:egitmen_basvurusu_detay', basvuru_id=bekleyen_basvuru.id)

    # Kullanıcının daha önce reddedilmiş bir başvurusu olup olmadığını kontrol et (en son reddedilen)
    reddedilmis_basvuru = EgitmenBasvuruFormu.objects.filter(
        kullanici=request.user.profil,
        basvuru_durumu='REDDEDILDI'
    ).order_by('-basvuru_tarihi').first()

    # POST isteği ise formu işle
    if request.method == 'POST':
        form = EgitmenBasvuruForm(request.POST)
        # Form geçerliyse
        if form.is_valid():
            # Başvuruyu kaydet (henüz veritabanına commit etme)
            basvuru = form.save(commit=False)
            # Başvuruyu yapan kullanıcıyı ata
            basvuru.kullanici = request.user.profil
            # Başvuru durumunu 'BEKLEMEDE' olarak ayarla
            basvuru.basvuru_durumu = 'BEKLEMEDE'
            # Başvuruyu veritabanına kaydet
            basvuru.save()

            # Başarı mesajı göster
            messages.success(request, "Eğitmen başvurunuz başarıyla alınmıştır. Başvurunuz moderatörler tarafından değerlendirilecektir.")
            # Başvuru detay sayfasına yönlendir
            return redirect('kullanicilar:egitmen_basvurusu_detay', basvuru_id=basvuru.id)
    # GET isteği ise boş form oluştur
    else:
        form = EgitmenBasvuruForm()

    # Şablona gönderilecek bağlam verileri
    context = {
        'form': form,
        'reddedilmis_basvuru': reddedilmis_basvuru # Reddedilmiş başvuru varsa şablonda gösterilebilir
    }
    # Form şablonunu render et
    return render(request, 'kullanicilar/egitmen_basvurusu_form.html', context)

@login_required
def egitmen_basvurusu_detay(request, basvuru_id):
    # Belirtilen ID'ye ve giriş yapmış kullanıcının profiline ait başvuruyu getir, yoksa 404 döndür
    basvuru = get_object_or_404(EgitmenBasvuruFormu, id=basvuru_id, kullanici=request.user.profil)

    # Şablona gönderilecek bağlam verileri
    context = {
        'basvuru': basvuru # Başvuru nesnesini bağlama ekle
    }
    # Başvuru detay şablonunu render et
    return render(request, 'kullanicilar/egitmen_basvurusu_detay.html', context)

@login_required
def kullanici_rolu_degistir(request, username):
    # Giriş yapmış kullanıcının admin yetkisi olup olmadığını kontrol et
    if not request.user.profil.is_admin():
        # Admin değilse hata mesajı göster ve hedef kullanıcının profiline yönlendir
        messages.error(request, "Kullanıcı rollerini sadece yöneticiler değiştirebilir.")
        return redirect('kullanicilar:profil_detay', username=username)

    # Rolü değiştirilecek hedef kullanıcıyı ve profilini getir, yoksa 404 döndür
    hedef_kullanici = get_object_or_404(User, username=username)
    profil = hedef_kullanici.profil

    # İstek POST ise rol değişikliğini işle
    if request.method == 'POST':
        # POST verilerinden yeni rolü al
        yeni_rol = request.POST.get('kullanici_rolu')

        # Alınan rol değerinin geçerli roller listesinde olup olmadığını kontrol et
        if yeni_rol in [r[0] for r in KullaniciProfili.KULLANICI_ROLLER]:
            # Profilin rolünü yeni rolle güncelle
            profil.kullanici_rolu = yeni_rol
            # Değişikliği veritabanına kaydet
            profil.save()

            # Rolün görünen adını al
            rol_ad = dict(KullaniciProfili.KULLANICI_ROLLER)[yeni_rol]
            # Başarı mesajı göster
            messages.success(request, f"{hedef_kullanici.username} kullanıcısının rolü {rol_ad} olarak değiştirildi.")
        else:
            # Geçersiz rol seçimi durumunda hata mesajı göster
            messages.error(request, "Geçersiz rol seçimi.")

    # İşlem sonrası hedef kullanıcının profil sayfasına yönlendir
    return redirect('kullanicilar:profil_detay', username=username)
