from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import DersIstegi, EgitmenBasvurusu
from kullanicilar.models import KullaniciProfili
from .forms import DersIstegiForm, EgitmenBasvurusuForm
from dersler.models import Ders
from django.utils import timezone
from datetime import datetime
from iletisim.models import Sohbet, Mesaj

# Tüm aktif ders isteklerini listeleyen View
class DersIstegiListView(ListView):
    model = DersIstegi
    template_name = 'home.html'  # Artık home.html şablonunu kullanacak
    context_object_name = 'ders_talepleri'  # home.html'de kullanılan değişken adına uygun olarak değiştirildi
    ordering = ['-olusturulma_tarihi']
    paginate_by = 10

    # Listelenecek queryset'i döndürür, filtreleme ve arama uygular
    def get_queryset(self):
        # Varsayılan olarak sadece aktif talepleri getir ve ilgili kullanıcı/ders bilgilerini çek
        queryset = DersIstegi.objects.filter(talep_durumu='AKTIF').select_related('talep_eden_kullanici__user', 'ders').order_by('-olusturulma_tarihi')

        # Arama terimine göre filtreleme
        arama_terimi = self.request.GET.get('arama', '')
        if arama_terimi:
            queryset = queryset.filter(
                Q(talep_basligi__icontains=arama_terimi) |
                Q(detayli_aciklama__icontains=arama_terimi) |
                Q(talep_eden_kullanici__user__username__icontains=arama_terimi)
            )

        # Ders kategorisine göre filtreleme
        kategori = self.request.GET.get('kategori', '')
        if kategori:
            queryset = queryset.filter(ders__kategori=kategori)

        # Seviyeye göre filtreleme
        seviye = self.request.GET.get('seviye', '')
        if seviye:
            queryset = queryset.filter(beklenen_seviye=seviye)
            
        # Tarih aralığına göre filtreleme
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

    # Template'e gönderilecek ek bağlam verilerini sağlar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filtre seçenekleri için gerekli verileri ekle
        context['kategoriler'] = Ders.objects.values_list('kategori', flat=True).distinct().order_by('kategori')
        context['seviyeler'] = dict(DersIstegi.SEVIYE_CHOICES)

        return context

# Yeni ders isteği oluşturmak için kullanılan View (Giriş yapılması zorunlu)
class DersIstegiCreateView(LoginRequiredMixin, CreateView):
    model = DersIstegi
    form_class = DersIstegiForm
    template_name = 'talepler/dersistegi_form.html'

    # Form başarıyla gönderildikten sonra yönlendirilecek URL'yi belirler
    def get_success_url(self):
        # Yeni oluşturulan talebin detay sayfasına yönlendir
        return reverse_lazy('talepler:ders_istegi_detay', kwargs={'pk': self.object.pk})

    # Form geçerliyse çalışır
    def form_valid(self, form):
        # Formu kaydetmeden önce talep eden kullanıcıyı ve durumu ata
        try:
            # Giriş yapmış kullanıcının KullaniciProfili nesnesini al
            kullanici_profili = KullaniciProfili.objects.get(user=self.request.user)
            form.instance.talep_eden_kullanici = kullanici_profili
        except KullaniciProfili.DoesNotExist:
            # Kullanıcı profili yoksa hata mesajı göster ve formu geçersiz kıl
            messages.error(self.request, "Ders talebi oluşturabilmek için bir kullanıcı profilinizin olması gerekmektedir. Lütfen profilinizi tamamlayın.")
            form.add_error(None, "Kullanıcı profiliniz bulunamadı. Ders talebi oluşturamazsınız.")
            return self.form_invalid(form)

        form.instance.talep_durumu = 'AKTIF' # Varsayılan durum: Aktif
        messages.success(self.request, "✅ Ders talebiniz başarıyla oluşturuldu! Artık eğitmen başvurularını bekleyebilirsiniz.")
        return super().form_valid(form)

    # Template'e gönderilecek ek bağlam verilerini sağlar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_baslik'] = "Yeni Ders Talebi Oluştur"
        return context

    # Form geçerli değilse çalışır
    def form_invalid(self, form):
        messages.error(self.request, "❌ Form gönderilirken hatalar oluştu. Lütfen aşağıdaki hataları düzeltin ve tekrar deneyin.")
        return super().form_invalid(form)

# Belirli bir ders isteğinin detayını gösteren View
class DersIstegiDetailView(DetailView):
    model = DersIstegi
    template_name = 'talepler/dersistegi_detail.html'
    context_object_name = 'ders_istegi'

    # Performans için ilgili alanları ve değerlendirmeleri önceden çeker
    def get_queryset(self):
        return super().get_queryset().select_related(
            'talep_eden_kullanici__user',
            'ders',
            'atanan_egitmen__user'
        ).prefetch_related('degerlendirmeleri__degerlendiren_kullanici__user',
                          'degerlendirmeleri__degerlendirilen_kullanici__user')

    # Template'e gönderilecek ek bağlam verilerini sağlar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ders_istegi = self.object
        kullanici = self.request.user

        # Kullanıcı giriş yapmamışsa sadece temel bilgileri göster
        if not kullanici.is_authenticated:
            return context

        # Giriş yapmış kullanıcının profilini al
        kullanici_profili = KullaniciProfili.objects.get(user=kullanici)

        # Kullanıcı daha önce bu isteğe başvurmuş mu kontrol et
        context['kullanici_daha_once_basvurdu'] = EgitmenBasvurusu.objects.filter(
            ders_istegi=ders_istegi,
            basvuran_egitmen=kullanici_profili
        ).exists()

        # Kullanıcının talep sahibi olup olmadığını kontrol et
        context['is_talep_sahibi'] = (ders_istegi.talep_eden_kullanici == kullanici_profili)
        # Kullanıcının atanan eğitmen olup olmadığını kontrol et
        context['is_atanan_egitmen'] = (ders_istegi.atanan_egitmen == kullanici_profili)

        # Eğer kullanıcı talep sahibi ise, gelen başvuruları getir
        if context['is_talep_sahibi']:
            context['gelen_basvurular'] = EgitmenBasvurusu.objects.filter(ders_istegi=ders_istegi).order_by('-basvuru_tarihi').select_related('basvuran_egitmen__user')
        else:
            # Talep sahibi değilse, talep aktifse, kullanıcı daha önce başvurmadıysa ve kullanıcı eğitmen ise başvuru formunu ekle
            if ders_istegi.talep_durumu == 'AKTIF' and not context['kullanici_daha_once_basvurdu'] and kullanici_profili.is_egitmen():
                context['egitmen_basvuru_formu'] = EgitmenBasvurusuForm()

        # Ders isteği tamamlandıysa, kullanıcının değerlendirme yapıp yapamayacağını kontrol et
        if ders_istegi.talep_durumu == 'TAMAMLANDI':
            from geribildirim.models import Degerlendirme

            # Değerlendirme değişkenlerini varsayılan olarak False olarak ayarla
            context['ogrenci_degerlendirme_yapabilir'] = False
            context['egitmen_degerlendirme_yapabilir'] = False

            # Öğrencinin eğitmeni değerlendirme durumunu kontrol et
            if context['is_talep_sahibi'] and ders_istegi.atanan_egitmen:
                context['ogrenci_degerlendirme_yapabilir'] = not Degerlendirme.objects.filter(
                    ders_istegi=ders_istegi,
                    degerlendiren_kullanici=kullanici_profili,
                    degerlendirilen_kullanici=ders_istegi.atanan_egitmen
                ).exists()
                
            # Eğitmenin öğrenciyi değerlendirme durumunu kontrol et
            elif context['is_atanan_egitmen']:
                context['egitmen_degerlendirme_yapabilir'] = not Degerlendirme.objects.filter(
                    ders_istegi=ders_istegi,
                    degerlendiren_kullanici=kullanici_profili,
                    degerlendirilen_kullanici=ders_istegi.talep_eden_kullanici
                ).exists()

            # Eski değişkeni geriye dönük uyumluluk için koru (başka yerlerde kullanılıyor olabilir)
            if context['is_talep_sahibi']:
                context['kullanici_degerlendirme_yapabilir'] = context['ogrenci_degerlendirme_yapabilir']
            elif context['is_atanan_egitmen']:
                context['kullanici_degerlendirme_yapabilir'] = context['egitmen_degerlendirme_yapabilir']

        return context

# Belirli bir ders isteğini güncellemek için kullanılan View (Giriş yapılması ve yetki kontrolü zorunlu)
class DersIstegiUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DersIstegi
    form_class = DersIstegiForm
    template_name = 'talepler/dersistegi_form.html'

    # Güncelleme başarıyla tamamlandıktan sonra yönlendirilecek URL'yi belirler
    def get_success_url(self):
        return reverse_lazy('talepler:ders_istegi_detay', kwargs={'pk': self.object.pk})

    # Form geçerliyse çalışır
    def form_valid(self, form):
        messages.success(self.request, "✨ TALEP BAŞARIYLA GÜNCELLENDİ! ✨ Değişiklikleriniz kaydedildi ve yeni bilgilerle görüntülenecek.")
        return super().form_valid(form)

    # Form geçerli değilse çalışır
    def form_invalid(self, form):
        messages.error(self.request, "❌ Form güncellenirken hatalar oluştu. Lütfen aşağıdaki hataları düzeltin ve tekrar deneyin.")
        return super().form_invalid(form)

    # Kullanıcının bu işlemi yapmaya yetkili olup olmadığını kontrol eder
    def test_func(self):
        ders_istegi = self.get_object()
        try:
            kullanici_profili = KullaniciProfili.objects.get(user=self.request.user)

            # Kullanıcı talep sahibi mi veya admin/moderatör mü kontrolü
            is_owner_or_admin = ders_istegi.talep_eden_kullanici == kullanici_profili or \
                   kullanici_profili.kullanici_rolu in ['MODERATOR', 'ADMIN']

            # Talep sadece aktifse ve atanmış bir eğitmeni yoksa güncellenebilir/silinebilir
            can_be_modified = ders_istegi.talep_durumu == 'AKTIF' and not ders_istegi.atanan_egitmen

            # Eğer talep güncellenemez durumdaysa ve kullanıcı talep sahibiyse, hata mesajı göster
            if not can_be_modified and ders_istegi.talep_eden_kullanici == kullanici_profili:
                messages.error(self.request, "Bu talep artık güncellenemez. Sadece aktif ve eğitmen atanmamış talepler güncellenebilir.")

            return is_owner_or_admin and can_be_modified

        except KullaniciProfili.DoesNotExist:
            # Kullanıcı profili yoksa yetkisi yoktur
            return False

    # Template'e gönderilecek ek bağlam verilerini sağlar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_baslik'] = "Ders Talebini Düzenle"
        return context

# Belirli bir ders isteğini silmek için kullanılan View (Giriş yapılması ve yetki kontrolü zorunlu)
class DersIstegiDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = DersIstegi
    template_name = 'talepler/dersistegi_confirm_delete.html'
    context_object_name = 'ders_istegi'
    success_url = reverse_lazy('home')

    # Kullanıcının bu işlemi yapmaya yetkili olup olmadığını kontrol eder
    def test_func(self):
        ders_istegi = self.get_object()
        try:
            kullanici_profili = KullaniciProfili.objects.get(user=self.request.user)

            # Kullanıcı talep sahibi mi veya admin/moderatör mü kontrolü
            is_owner_or_admin = ders_istegi.talep_eden_kullanici == kullanici_profili or \
                   kullanici_profili.kullanici_rolu in ['MODERATOR', 'ADMIN']

            # Talep sadece aktifse ve atanmış bir eğitmeni yoksa güncellenebilir/silinebilir
            can_be_deleted = ders_istegi.talep_durumu == 'AKTIF' and not ders_istegi.atanan_egitmen

            # Eğer talep silinemez durumdaysa ve kullanıcı talep sahibiyse, hata mesajı göster
            if not can_be_deleted and ders_istegi.talep_eden_kullanici == kullanici_profili:
                messages.error(self.request, "Bu talep artık silinemez. Sadece aktif ve eğitmen atanmamış talepler silinebilir.")

            return is_owner_or_admin and can_be_deleted

        except KullaniciProfili.DoesNotExist:
            # Profili olmayan kullanıcı silemez
            return False

    # Silme işlemi başarılı olduğunda çalışır
    def delete(self, request, *args, **kwargs):
        # Silme işlemi öncesinde nesneyi al
        self.object = self.get_object()
        # Başarı mesajını ekle
        messages.success(self.request, f"'{self.object.talep_basligi}' başlıklı ders talebi başarıyla silindi.")
        # Silme işlemini gerçekleştir ve yanıtı döndür
        return super().delete(request, *args, **kwargs)

# Eğitmenlerin bir ders isteğine başvurmasını sağlayan fonksiyonel View (Giriş yapılması zorunlu)
@login_required
def egitmen_basvurusu_yap(request, ders_istegi_id):
    # İlgili ders isteğini veya 404 hatasını döndür
    ders_istegi = get_object_or_404(DersIstegi, pk=ders_istegi_id)
    # Giriş yapmış kullanıcının profilini al
    kullanici_profili = KullaniciProfili.objects.get(user=request.user)

    # Kullanıcının eğitmen rolüne sahip olup olmadığını kontrol et
    if not kullanici_profili.is_egitmen():
        messages.error(request, "Ders taleplerine sadece eğitmen rolüne sahip kullanıcılar başvurabilir.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

    # Ders isteği sahibinin kendi isteğine başvurmasını engelle
    if ders_istegi.talep_eden_kullanici == kullanici_profili:
        messages.error(request, "Kendi ders isteğinize eğitmen olarak başvuramazsınız.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

    # Kullanıcının daha önce bu isteğe başvurup başvurmadığını kontrol et
    if EgitmenBasvurusu.objects.filter(ders_istegi=ders_istegi, basvuran_egitmen=kullanici_profili).exists():
        messages.warning(request, "Bu ders isteğine daha önce başvuruda bulundunuz.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

    # Ders isteğinin aktif olup olmadığını kontrol et
    if ders_istegi.talep_durumu != 'AKTIF':
        messages.error(request, "Bu ders isteği artık aktif değil, başvuru yapamazsınız.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

    # Eğer istek POST ise (form gönderilmişse)
    if request.method == 'POST':
        form = EgitmenBasvurusuForm(request.POST)
        # Form geçerliyse başvuruyu kaydet
        if form.is_valid():
            basvuru = form.save(commit=False)
            basvuru.ders_istegi = ders_istegi
            basvuru.basvuran_egitmen = kullanici_profili
            basvuru.basvuru_durumu = 'BEKLEMEDE' # Başlangıç durumu: Beklemede
            basvuru.save()
            messages.success(request, f"'{ders_istegi.talep_basligi}' başlıklı ders isteğine eğitmen olarak başarıyla başvurdunuz.")
            return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)
        else:
            # Form geçerli değilse hata mesajı göster
            messages.error(request, "Başvurunuzda bir hata oluştu. Lütfen tekrar deneyin.")
            return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)
    else:
        # Eğer istek GET ise (doğrudan URL ile gelinmişse) bilgi mesajı göster
        messages.info(request, "Eğitmen başvurusu yapmak için lütfen ders detay sayfasındaki formu kullanın.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

# Ders isteği sahibinin eğitmen başvurularını yönetmesini (kabul/red) sağlayan fonksiyonel View (Giriş yapılması zorunlu)
@login_required
def egitmen_basvuru_yonet(request, basvuru_id):
    # İlgili başvuruyu ve ilişkili ders isteği/kullanıcı bilgilerini çek veya 404 hatası döndür
    basvuru = get_object_or_404(EgitmenBasvurusu.objects.select_related('ders_istegi__talep_eden_kullanici__user', 'basvuran_egitmen__user'), pk=basvuru_id)
    ders_istegi = basvuru.ders_istegi
    # Giriş yapmış kullanıcının profilini al
    kullanici_profili = KullaniciProfili.objects.get(user=request.user)

    # Sadece ders isteği sahibi bu işlemi yapabilir, yetki kontrolü
    if ders_istegi.talep_eden_kullanici != kullanici_profili:
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

    # Sadece aktif ders isteklerindeki bekleyen başvurular yönetilebilir, durum kontrolü
    if ders_istegi.talep_durumu != 'AKTIF':
         messages.error(request, "Bu ders isteği aktif olmadığı için başvuru yönetilemez.")
         return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

    # Başvurunun durumunun 'BEKLEMEDE' olup olmadığını kontrol et
    if basvuru.basvuru_durumu != 'BEKLEMEDE':
        messages.warning(request, "Bu başvuru zaten işleme alınmış (Kabul edilmiş veya Reddedilmiş). Tekrar işlem yapılamaz.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

    # Eğer istek POST ise (form gönderilmişse)
    if request.method == 'POST':
        action = request.POST.get('action') # Formdan gelen 'action' değerini al (kabul veya reddet)
        if action == 'kabul':
            # Başvuruyu kabul et
            basvuru.basvuru_durumu = 'KABUL_EDILDI'
            basvuru.save()
            # Ders isteğinin durumunu 'Eğitmen Atandı' olarak güncelle ve atanan eğitmeni belirle
            ders_istegi.talep_durumu = 'EGITMEN_ATANDI'
            ders_istegi.atanan_egitmen = basvuru.basvuran_egitmen
            ders_istegi.save()

            # Aynı ders isteğine yapılan diğer bekleyen başvuruları otomatik olarak reddet
            EgitmenBasvurusu.objects.filter(ders_istegi=ders_istegi, basvuru_durumu='BEKLEMEDE').update(basvuru_durumu='REDDEDILDI')

            # Otomatik olarak sohbet oluşturma işlemi
            try:
                # Ders isteği için zaten bir sohbet var mı kontrol et
                try:
                    sohbet = Sohbet.objects.get(ders_istegi=ders_istegi)
                except Sohbet.DoesNotExist:
                    # Yoksa yeni sohbet oluştur
                    sohbet = Sohbet.objects.create(ders_istegi=ders_istegi)

                    # Sohbete katılımcıları ekle (ders isteği sahibi ve atanan eğitmen)
                    sohbet.katilimcilar.add(ders_istegi.talep_eden_kullanici, ders_istegi.atanan_egitmen)

                    # Hoş geldiniz mesajı oluştur (sistem mesajı olarak)
                    Mesaj.objects.create(
                        sohbet=sohbet,
                        gonderen_kullanici=None,
                        icerik="Hoş geldiniz! Bu sohbet kanalı ders isteğiyle ilgili iletişim kurmanız için otomatik olarak oluşturulmuştur."
                    )
            except Exception as e:
                # Sohbet oluşturulurken bir hata olursa, işlemi durdurma ancak hatayı loglama
                print(f"Sohbet oluşturma hatası: {e}")

            messages.success(request, f"{basvuru.basvuran_egitmen.user.username} kullanıcısının eğitmenlik başvurusu kabul edildi. Ders isteği 'Eğitmen Atandı' olarak güncellendi ve diğer bekleyen başvurular reddedildi.")
        elif action == 'reddet':
            # Başvuruyu reddet
            basvuru.basvuru_durumu = 'REDDEDILDI'
            basvuru.save()
            messages.success(request, f"{basvuru.basvuran_egitmen.user.username} kullanıcısının eğitmenlik başvurusu reddedildi.")
            # TODO: Başvurana bildirim gönderilebilir.
        else:
            # Geçersiz işlem durumunda hata mesajı
            messages.error(request, "Geçersiz işlem.")

        # İşlem sonrası ders isteği detay sayfasına yönlendir
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)
    else:
        # GET isteği ile gelinirse (genellikle olmamalı), detay sayfasına yönlendir
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi.pk)

# Eğitmenin yaptığı başvuruyu geri çekmesini sağlayan fonksiyonel View (Giriş yapılması zorunlu)
@login_required
def egitmen_basvurusu_geri_cek(request, basvuru_id):
    # İlgili başvuruyu veya 404 hatasını döndür
    basvuru = get_object_or_404(EgitmenBasvurusu, pk=basvuru_id)
    # Giriş yapmış kullanıcının profilini al
    kullanici_profili = KullaniciProfili.objects.get(user=request.user)

    # Sadece başvuruyu yapan kişi geri çekebilir, yetki kontrolü
    if basvuru.basvuran_egitmen != kullanici_profili:
        messages.error(request, "Bu başvuru size ait olmadığı için geri çekemezsiniz.")
        # Kullanıcının geldiği sayfaya veya profil sayfasına yönlendir
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('kullanicilar:profil_detay', kwargs={'username': request.user.username})))

    # Başvurunun durumunun 'BEKLEMEDE' olup olmadığını kontrol et
    if basvuru.basvuru_durumu != 'BEKLEMEDE':
        messages.warning(request, f"Bu başvuru zaten '{basvuru.get_basvuru_durumu_display()}' durumunda olduğu için geri çekilemez.")
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('kullanicilar:profil_detay', kwargs={'username': request.user.username})))

    # Eğer istek POST ise (onay formu gönderilmişse)
    if request.method == 'POST':
        # Başvurunun durumunu 'GERI_CEKILDI' olarak güncelle
        basvuru.basvuru_durumu = 'GERI_CEKILDI'
        basvuru.save()
        messages.success(request, f"'{basvuru.ders_istegi.talep_basligi}' ders isteğine yaptığınız başvuru başarıyla geri çekildi.")
        # Kullanıcının profil sayfasına yönlendir
        return redirect(reverse_lazy('kullanicilar:profil_detay', kwargs={'username': request.user.username}))
    else:
        # GET isteği ile gelinirse, direkt işlem yapma, bilgi mesajı göster ve geldiği yere yönlendir
        messages.info(request, "Başvuruyu geri çekmek için lütfen profil sayfanızdaki ilgili butonu kullanın.")
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('kullanicilar:profil_detay', kwargs={'username': request.user.username})))

# Ders isteğini tamamlandı olarak işaretlemeyi sağlayan fonksiyonel View (Giriş yapılması zorunlu)
@login_required
def ders_istegi_tamamla(request, ders_istegi_id):
    # Eğitmen atanmış bir ders isteğini 'Tamamlandı' durumuna getirir.
    # Sadece ders isteğinin sahibi veya atanan eğitmen bu işlemi yapabilir.
    # İki tarafın da onayı gereklidir.
    # İlgili ders isteğini veya 404 hatasını döndür
    ders_istegi = get_object_or_404(DersIstegi, pk=ders_istegi_id)
    # Giriş yapmış kullanıcının profilini al veya 404 hatası döndür
    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)

    # Kullanıcının talep sahibi veya atanan eğitmen olup olmadığını kontrol et, yetki kontrolü
    if kullanici_profili != ders_istegi.talep_eden_kullanici and kullanici_profili != ders_istegi.atanan_egitmen:
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

    # Ders isteğinin mevcut durumunu al
    durum = ders_istegi.talep_durumu

    # Sadece belirli durumdaki taleplerin tamamlanabileceğini kontrol et
    if durum not in ['EGITMEN_ATANDI', 'OGRENCI_TAMAMLADI', 'EGITMEN_TAMAMLADI']:
        if durum == 'TAMAMLANDI':
            messages.info(request, "Bu ders zaten her iki tarafça tamamlandı olarak işaretlenmiştir.")
        else:
            messages.error(request, "Bu ders talebi şu anda tamamlanamaz.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

    # Eğer istek POST ise (tamamlama onayı verilmişse)
    if request.method == 'POST':
        # Eğer işlemi yapan kullanıcı talep sahibi ise
        if kullanici_profili == ders_istegi.talep_eden_kullanici:
            # Eğer eğitmen daha önce tamamladıysa, ders tamamen tamamlanmış olur
            if durum == 'EGITMEN_TAMAMLADI':
                ders_istegi.talep_durumu = 'TAMAMLANDI'
                ders_istegi.ogrenci_tamamlama_tarihi = timezone.now()
                ders_istegi.save()
                
                # Sohbet ve mesajlarını sil
                try:
                    sohbet = Sohbet.objects.get(ders_istegi=ders_istegi)
                    # Önce mesajları sil
                    Mesaj.objects.filter(sohbet=sohbet).delete()
                    # Sonra sohbeti sil
                    sohbet.delete()
                except Sohbet.DoesNotExist:
                    # Sohbet yoksa bir şey yapma
                    pass
                
                messages.success(request, "Ders başarıyla tamamlandı olarak işaretlenmiştir. Artık eğitmeni değerlendirebilirsiniz.")
            # Eğitmen henüz tamamlamadıysa, sadece öğrenci tamamladı durumuna geçer
            else:
                ders_istegi.talep_durumu = 'OGRENCI_TAMAMLADI'
                ders_istegi.ogrenci_tamamlama_tarihi = timezone.now()
                ders_istegi.save()
                messages.success(request, "Dersi tamamlandı olarak işaretlediniz. Tamamlanma işleminin gerçekleşmesi için eğitmenin de dersi tamamlandı olarak işaretlemesi gerekiyor.")

        # Eğer işlemi yapan kullanıcı atanan eğitmen ise
        elif kullanici_profili == ders_istegi.atanan_egitmen:
            # Eğer öğrenci daha önce tamamladıysa, ders tamamen tamamlanmış olur
            if durum == 'OGRENCI_TAMAMLADI':
                ders_istegi.talep_durumu = 'TAMAMLANDI'
                ders_istegi.egitmen_tamamlama_tarihi = timezone.now()
                ders_istegi.save()
                
                # Sohbet ve mesajlarını sil
                try:
                    sohbet = Sohbet.objects.get(ders_istegi=ders_istegi)
                    # Önce mesajları sil
                    Mesaj.objects.filter(sohbet=sohbet).delete()
                    # Sonra sohbeti sil
                    sohbet.delete()
                except Sohbet.DoesNotExist:
                    # Sohbet yoksa bir şey yapma
                    pass
                
                messages.success(request, "Ders başarıyla tamamlandı olarak işaretlenmiştir. Artık öğrenciyi değerlendirebilirsiniz.")
            # Öğrenci henüz tamamlamadıysa, sadece eğitmen tamamladı durumuna geçer
            else:
                ders_istegi.talep_durumu = 'EGITMEN_TAMAMLADI'
                ders_istegi.egitmen_tamamlama_tarihi = timezone.now()
                ders_istegi.save()
                messages.success(request, "Dersi tamamlandı olarak işaretlediniz. Tamamlanma işleminin gerçekleşmesi için öğrencinin de dersi tamamlandı olarak işaretlemesi gerekiyor.")

        # İşlem sonrası ders isteği detay sayfasına yönlendir
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

    # Eğer istek GET ise (onay sayfası gösterilecekse)
    context = {
        'ders_istegi': ders_istegi,
        'is_ogrenci': kullanici_profili == ders_istegi.talep_eden_kullanici,
        'is_egitmen': kullanici_profili == ders_istegi.atanan_egitmen,
        'durum': durum
    }
    # Tamamlama onay sayfasını render et
    return render(request, 'talepler/dersistegi_tamamla.html', context)
