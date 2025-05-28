from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from kullanicilar.models import KullaniciProfili, EgitmenBasvuruFormu
from kullanicilar.mixins import ModeratorRequiredMixin
from kullanicilar.forms import EgitmenBasvuruDegerlendirmeForm
from talepler.models import DersIstegi, EgitmenBasvurusu
from geribildirim.models import Degerlendirme

@login_required
def kullanici_engelle(request, user_id):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Kullanıcı engelleme işlemini sadece moderatörler ve yöneticiler yapabilir.")
        return redirect('home')

    # Engellenecek hedef kullanıcıyı veritabanından al
    hedef_kullanici = get_object_or_404(User, id=user_id)

    # Kullanıcının kendini engellemesini engelle
    if hedef_kullanici == request.user:
        messages.error(request, "Kendinizi engelleyemezsiniz.")
        return redirect('kullanicilar:profil_detay', username=hedef_kullanici.username)

    # Admin rolündeki bir kullanıcının, admin olmayan bir moderatör tarafından engellenmesini engelle
    if hedef_kullanici.profil.is_admin() and not request.user.profil.is_admin():
        messages.error(request, "Bir yöneticiyi sadece başka bir yönetici engelleyebilir.")
        return redirect('kullanicilar:profil_detay', username=hedef_kullanici.username)

    # POST isteği geldiğinde engelleme işlemini gerçekleştir
    if request.method == 'POST':
        try:
            # Formdan engelleme süresini (gün olarak) al, varsayılan 7 gün
            engelleme_suresi = int(request.POST.get('engelleme_suresi', 7))
            # Engelleme süresini 1-30 gün aralığıyla sınırla
            if engelleme_suresi < 1:
                engelleme_suresi = 1
            elif engelleme_suresi > 30:
                engelleme_suresi = 30

            # Engelin bitiş tarihini hesapla
            ban_bitis_tarihi = timezone.now() + timedelta(days=engelleme_suresi)

            # Hedef kullanıcının profilini güncelle
            profil = hedef_kullanici.profil
            profil.ban_durumu = True
            profil.ban_bitis_tarihi = ban_bitis_tarihi
            profil.save()

            # Baş başarı mesajı göster
            messages.success(request, f"{hedef_kullanici.username} kullanıcısı {engelleme_suresi} gün süreyle engellenmiştir.")
        except ValueError:
            # Geçersiz süre girildiğinde hata mesajı göster
            messages.error(request, "Geçersiz engelleme süresi. Lütfen 1-30 arasında bir sayı girin.")

    # Kullanıcının profil detay sayfasına yönlendir
    return redirect('kullanicilar:profil_detay', username=hedef_kullanici.username)

@login_required
def kullanici_engel_kaldir(request, user_id):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Kullanıcı engelleme işlemini sadece moderatörler ve yöneticiler yapabilir.")
        return redirect('home')

    # Engeli kaldırılacak hedef kullanıcıyı veritabanından al
    hedef_kullanici = get_object_or_404(User, id=user_id)

    # POST isteği geldiğinde engel kaldırma işlemini gerçekleştir
    if request.method == 'POST':
        # Hedef kullanıcının profilini güncelle
        profil = hedef_kullanici.profil
        profil.ban_durumu = False
        profil.ban_bitis_tarihi = None
        profil.save()

        # Başarı mesajı göster
        messages.success(request, f"{hedef_kullanici.username} kullanıcısının engeli kaldırılmıştır.")

    # Kullanıcının profil detay sayfasına yönlendir
    return redirect('kullanicilar:profil_detay', username=hedef_kullanici.username)

# Moderatör Paneli Görünümleri

@login_required
def moderator_panel(request):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu sayfaya erişim için moderatör yetkisi gerekmektedir.")
        return redirect('home')

    # Panelde gösterilecek istatistikleri hesapla
    kullanici_sayisi = User.objects.count()
    aktif_ders_istegi_sayisi = DersIstegi.objects.filter(talep_durumu='AKTIF').count()
    tamamlanan_ders_sayisi = DersIstegi.objects.filter(talep_durumu='TAMAMLANDI').count()
    engelli_kullanici_sayisi = KullaniciProfili.objects.filter(ban_durumu=True).count()

    # Şablona gönderilecek bağlam verilerini hazırla
    context = {
        'kullanici_sayisi': kullanici_sayisi,
        'aktif_ders_istegi_sayisi': aktif_ders_istegi_sayisi,
        'tamamlanan_ders_sayisi': tamamlanan_ders_sayisi,
        'engelli_kullanici_sayisi': engelli_kullanici_sayisi,
    }

    # Moderatör paneli ana sayfası şablonunu render et
    return render(request, 'moderasyon/panel_anasayfa.html', context)

class KullaniciListesiView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = User # Kullanılacak model
    template_name = 'moderasyon/kullanici_listesi.html' # Kullanılacak şablon
    context_object_name = 'kullanicilar' # Şablonda kullanılacak nesne adı
    paginate_by = 20 # Sayfa başına kullanıcı sayısı

    def get_queryset(self):
        # Tüm kullanıcıları profil bilgileriyle birlikte al ve kayıt tarihine göre sırala
        queryset = User.objects.all().select_related('profil').order_by('-date_joined')

        # Arama sorgusu varsa kullanıcı adı, ad, soyad veya e-posta alanlarında filtrele
        arama = self.request.GET.get('arama', '')
        if arama:
            queryset = queryset.filter(
                Q(username__icontains=arama) |
                Q(first_name__icontains=arama) |
                Q(last_name__icontains=arama) |
                Q(email__icontains=arama)
            )

        # Rol filtresi varsa profile göre filtrele
        rol = self.request.GET.get('rol', '')
        if rol and rol in [r[0] for r in KullaniciProfili.KULLANICI_ROLLER]:
            queryset = queryset.filter(profil__kullanici_rolu=rol)

        # Engel durumu filtresi varsa profile göre filtrele
        engel_durumu = self.request.GET.get('engel_durumu', '')
        if engel_durumu == 'engelli':
            queryset = queryset.filter(profil__ban_durumu=True)
        elif engel_durumu == 'engelsiz':
            queryset = queryset.filter(profil__ban_durumu=False)

        return queryset

    def get_context_data(self, **kwargs):
        # Varsayılan bağlam verilerini al
        context = super().get_context_data(**kwargs)
        # Arama ve filtre değerlerini bağlama ekle
        context['arama'] = self.request.GET.get('arama', '')
        context['rol'] = self.request.GET.get('rol', '')
        context['engel_durumu'] = self.request.GET.get('engel_durumu', '')
        # Kullanıcı rol seçeneklerini bağlama ekle
        context['kullanici_roller'] = KullaniciProfili.KULLANICI_ROLLER
        return context

class AktifDersIstekleriView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = DersIstegi # Kullanılacak model
    template_name = 'moderasyon/aktif_ders_istekleri.html' # Kullanılacak şablon
    context_object_name = 'ders_istekleri' # Şablonda kullanılacak nesne adı
    paginate_by = 15 # Sayfa başına ders isteği sayısı

    def get_queryset(self):
        # Durumu 'AKTIF' olan ders isteklerini al, ilgili kullanıcı ve ders bilgileriyle birlikte
        # ve oluşturulma tarihine göre tersten sırala
        return DersIstegi.objects.filter(
            talep_durumu='AKTIF'
        ).select_related(
            'talep_eden_kullanici__user', 'ders'
        ).order_by('-olusturulma_tarihi')

class EgitmenBasvurulariView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = EgitmenBasvurusu # Kullanılacak model
    template_name = 'moderasyon/egitmen_basvurulari.html' # Kullanılacak şablon
    context_object_name = 'basvurular' # Şablonda kullanılacak nesne adı
    paginate_by = 15 # Sayfa başına başvuru sayısı

    def get_queryset(self):
        # Durumu 'BEKLEMEDE' olan eğitmen başvurularını al, ilgili eğitmen ve ders isteği bilgileriyle birlikte ve başvuru tarihine göre tersten sırala
        return EgitmenBasvurusu.objects.filter(
            basvuru_durumu='BEKLEMEDE'
        ).select_related(
            'basvuran_egitmen__user', 'ders_istegi__talep_eden_kullanici__user'
        ).order_by('-basvuru_tarihi')

class EngelliKullanicilarView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = KullaniciProfili # Kullanılacak model
    template_name = 'moderasyon/engelli_kullanicilar.html' # Kullanılacak şablon
    context_object_name = 'kullanicilar' # Şablonda kullanılacak nesne adı
    paginate_by = 15 # Sayfa başına kullanıcı sayısı

    def get_queryset(self):
        # Ban durumu True olan kullanıcı profillerini al, ilgili kullanıcı bilgileriyle birlikte ve ban bitiş tarihine göre sırala
        return KullaniciProfili.objects.filter(
            ban_durumu=True
        ).select_related('user').order_by('ban_bitis_tarihi')

@login_required
def ders_istegi_incele(request, ders_istegi_id):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu sayfaya erişim için moderatör yetkisi gerekmektedir.")
        return redirect('home')

    # İncelenecek ders isteğini veritabanından al
    ders_istegi = get_object_or_404(DersIstegi, id=ders_istegi_id)

    # İlgili ders isteği için yapılmış eğitmen başvurularını al
    egitmen_basvurulari = EgitmenBasvurusu.objects.filter(
        ders_istegi=ders_istegi
    ).select_related('basvuran_egitmen__user')

    # Şablona gönderilecek bağlam verilerini hazırla
    context = {
        'ders_istegi': ders_istegi,
        'egitmen_basvurulari': egitmen_basvurulari,
    }

    # Ders isteği inceleme şablonunu render et
    return render(request, 'moderasyon/ders_istegi_incele.html', context)

@login_required
def ders_istegi_kapat(request, ders_istegi_id):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu işlemi sadece moderatörler yapabilir.")
        return redirect('home')

    # Kapatılacak ders isteğini veritabanından al
    ders_istegi = get_object_or_404(DersIstegi, id=ders_istegi_id)

    # POST isteği geldiğinde kapatma işlemini gerçekleştir
    if request.method == 'POST':
        # Ders isteğinin durumunu 'KAPALI' olarak ayarla ve kaydet
        ders_istegi.talep_durumu = 'KAPALI'
        ders_istegi.save()

        # Başarı mesajı göster
        messages.success(request, f"{ders_istegi.talep_basligi} başlıklı ders isteği kapatıldı.")
        # Aktif ders istekleri listesine yönlendir
        return redirect('moderasyon:aktif_ders_istekleri')

    # GET isteği geldiyse inceleme sayfasına geri yönlendir
    return redirect('moderasyon:ders_istegi_incele', ders_istegi_id=ders_istegi_id)

class EgitmenRolBasvurulariListView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = EgitmenBasvuruFormu # Kullanılacak model
    template_name = 'moderasyon/egitmen_rol_basvurulari.html' # Kullanılacak şablon
    context_object_name = 'basvurular' # Şablonda kullanılacak nesne adı
    paginate_by = 15 # Sayfa başına başvuru sayısı

    def get_queryset(self):
        # Durumu 'BEKLEMEDE' olan eğitmen rolü başvurularını al, ilgili kullanıcı ve moderatör bilgileriyle birlikte ve başvuru tarihine göre tersten sırala
        queryset = EgitmenBasvuruFormu.objects.filter(
            basvuru_durumu='BEKLEMEDE'
        ).select_related(
            'kullanici__user', 'degerlendiren_moderator__user'
        ).order_by('-basvuru_tarihi')

        # Arama sorgusu varsa kullanıcı adı, ad, soyad veya uzmanlık alanlarında filtrele
        arama = self.request.GET.get('arama', '')
        if arama:
            queryset = queryset.filter(
                Q(kullanici__user__username__icontains=arama) |
                Q(kullanici__user__first_name__icontains=arama) |
                Q(kullanici__user__last_name__icontains=arama) |
                Q(uzmanlik_alanlari__icontains=arama)
            )

        return queryset

    def get_context_data(self, **kwargs):
        # Varsayılan bağlam verilerini al
        context = super().get_context_data(**kwargs)
        # Arama değerini bağlama ekle
        context['arama'] = self.request.GET.get('arama', '')

        # Başvuru istatistiklerini hesapla ve bağlama ekle
        context['bekleyen_basvuru_sayisi'] = EgitmenBasvuruFormu.objects.filter(
            basvuru_durumu='BEKLEMEDE'
        ).count()
        context['onaylanan_basvuru_sayisi'] = EgitmenBasvuruFormu.objects.filter(
            basvuru_durumu='ONAYLANDI'
        ).count()
        context['reddedilen_basvuru_sayisi'] = EgitmenBasvuruFormu.objects.filter(
            basvuru_durumu='REDDEDILDI'
        ).count()

        return context

@login_required
def egitmen_rol_basvurusu_degerlendir(request, basvuru_id):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu işlemi sadece moderatörler yapabilir.")
        return redirect('home')

    # Değerlendirilecek başvuruyu veritabanından al
    basvuru = get_object_or_404(EgitmenBasvuruFormu, id=basvuru_id)

    # Başvurunun zaten değerlendirilmiş olup olmadığını kontrol et
    if basvuru.basvuru_durumu != 'BEKLEMEDE':
        messages.info(request, "Bu başvuru zaten değerlendirilmiş.")
        return redirect('moderasyon:egitmen_rol_basvurulari')

    # POST isteği geldiğinde formu işle
    if request.method == 'POST':
        form = EgitmenBasvuruDegerlendirmeForm(request.POST, instance=basvuru)
        # Form geçerliyse
        if form.is_valid():
            # Formu kaydet ama henüz veritabanına commit etme
            basvuru = form.save(commit=False)
            # Değerlendiren moderatörü ve değerlendirilme tarihini ayarla
            basvuru.degerlendiren_moderator = request.user.profil
            basvuru.degerlendirilme_tarihi = timezone.now()

            # Başvuru onaylandıysa kullanıcının rolünü 'EGITMEN' olarak değiştir
            if basvuru.basvuru_durumu == 'ONAYLANDI':
                kullanici_profili = basvuru.kullanici
                kullanici_profili.kullanici_rolu = 'EGITMEN'
                kullanici_profili.save()

                # Başarı mesajı göster
                messages.success(request, f"{kullanici_profili.user.username} kullanıcısının rolü başarıyla eğitmen olarak değiştirildi.")

            # Başvuruyu veritabanına kaydet
            basvuru.save()

            # Eğitmen rolü başvuruları listesine yönlendir
            return redirect('moderasyon:egitmen_rol_basvurulari')
    else:
        # GET isteği geldiğinde formu başvurunun mevcut verileriyle oluştur
        form = EgitmenBasvuruDegerlendirmeForm(instance=basvuru)

    # Şablona gönderilecek bağlam verilerini hazırla
    context = {
        'form': form,
        'basvuru': basvuru
    }
    # Değerlendirme şablonunu render et
    return render(request, 'moderasyon/egitmen_rol_basvurusu_degerlendir.html', context)

@login_required
def egitmen_rol_basvurusu_onayla(request, basvuru_id):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu işlemi sadece moderatörler yapabilir.")
        return redirect('home')

    # Onaylanacak başvuruyu veritabanından al
    basvuru = get_object_or_404(EgitmenBasvuruFormu, id=basvuru_id)

    # Başvurunun zaten değerlendirilmiş olup olmadığını kontrol et
    if basvuru.basvuru_durumu != 'BEKLEMEDE':
        messages.info(request, "Bu başvuru zaten değerlendirilmiş.")
        return redirect('moderasyon:egitmen_rol_basvurulari')

    # POST isteği geldiğinde onaylama işlemini gerçekleştir
    if request.method == 'POST':
        # Başvurunun durumunu 'ONAYLANDI' olarak ayarla
        basvuru.basvuru_durumu = 'ONAYLANDI'
        # Değerlendiren moderatörü ve değerlendirilme tarihini ayarla
        basvuru.degerlendiren_moderator = request.user.profil
        basvuru.degerlendirilme_tarihi = timezone.now()
        # Başvuruyu kaydet
        basvuru.save()

        # Başvuru sahibinin kullanıcı rolünü 'EGITMEN' olarak değiştir
        kullanici_profili = basvuru.kullanici
        kullanici_profili.kullanici_rolu = 'EGITMEN'
        kullanici_profili.save()

        # Başarı mesajı göster
        messages.success(request, f"{kullanici_profili.user.username} kullanıcısının eğitmen başvurusu onaylandı ve rolü eğitmen olarak değiştirildi.")

    # Eğitmen rolü başvuruları listesine yönlendir
    return redirect('moderasyon:egitmen_rol_basvurulari')

@login_required
def egitmen_rol_basvurusu_reddet(request, basvuru_id):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu işlemi sadece moderatörler ve yöneticiler yapabilir.")
        return redirect('home')

    # Reddedilecek başvuruyu veritabanından al
    basvuru = get_object_or_404(EgitmenBasvuruFormu, id=basvuru_id)

    # Başvurunun zaten değerlendirilmiş olup olmadığını kontrol et
    if basvuru.basvuru_durumu != 'BEKLEMEDE':
        messages.info(request, "Bu başvuru zaten değerlendirilmiş.")
        return redirect('moderasyon:egitmen_rol_basvurulari')

    # POST isteği geldiğinde reddetme işlemini gerçekleştir
    if request.method == 'POST':
        # Formdan red sebebini al
        red_sebebi = request.POST.get('red_sebebi', '').strip()

        # Red sebebi boşsa hata mesajı göster ve değerlendirme sayfasına yönlendir
        if not red_sebebi:
            messages.error(request, "Ret sebebi belirtmeniz gerekmektedir.")
            return redirect('moderasyon:egitmen_rol_basvurusu_degerlendir', basvuru_id=basvuru.id)

        # Başvurunun durumunu 'REDDEDILDI' olarak ayarla
        basvuru.basvuru_durumu = 'REDDEDILDI'
        # Değerlendiren moderatörü, değerlendirilme tarihini ve red sebebini ayarla
        basvuru.degerlendiren_moderator = request.user.profil
        basvuru.degerlendirilme_tarihi = timezone.now()
        basvuru.red_sebebi = red_sebebi
        # Başvuruyu kaydet
        basvuru.save()

        # Başarı mesajı göster
        messages.success(request, f"{basvuru.kullanici.user.username} kullanıcısının eğitmen başvurusu reddedildi.")
        # Eğitmen rolü başvuruları listesine yönlendir
        return redirect('moderasyon:egitmen_rol_basvurulari')

    # GET isteği geldiyse değerlendirme sayfasına yönlendir (red sebebi POST ile alınır)
    return redirect('moderasyon:egitmen_rol_basvurusu_degerlendir', basvuru_id=basvuru.id)

@login_required
def veri_disari_aktar(request):
    import csv
    from django.http import HttpResponse
    from django.db.models import Model
    from django.apps import apps # Modelleri string isimlerinden almak için

    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu işlemi sadece moderatörler ve yöneticiler yapabilir.")
        return redirect('home')

    # POST isteği geldiğinde dışarı aktarma işlemini gerçekleştir
    if request.method == 'POST':
        # Formdan seçilen modelin adını al
        model_secimi = request.POST.get('model_secimi')

        # Dışarı aktarılabilecek modellerin listesi
        exportable_models = {
            'kullanici_profilleri': KullaniciProfili,
            'ders_istekleri': DersIstegi,
            'egitmen_basvurulari': EgitmenBasvurusu,
            'dersler': 'dersler.Ders', # String olarak belirtilen model
            'degerlendirmeler': Degerlendirme,
        }

        # Seçilen modelin dışarı aktarılabilir modeller listesinde olup olmadığını kontrol et
        if model_secimi not in exportable_models:
            messages.error(request, "Geçersiz model seçimi.")
            return redirect('moderasyon:veri_yonetimi')

        # Seçilen model nesnesini al
        model = exportable_models[model_secimi]
        # Eğer model string olarak belirtilmişse, apps modülünü kullanarak gerçek model nesnesini al
        if isinstance(model, str):
            app_label, model_name = model.split('.')
            model = apps.get_model(app_label, model_name)

        # Seçilen modelin tüm verilerini al
        queryset = model.objects.all()

        # CSV dosyası oluşturmak için HttpResponse nesnesi hazırla
        response = HttpResponse(content_type='text/csv')
        # Dosya adını ayarla
        response['Content-Disposition'] = f'attachment; filename="{model.__name__}.csv"'

        # CSV yazıcısı oluştur
        writer = csv.writer(response)

        # Modelin alan adlarını sütun başlıkları olarak belirle
        model_fields = [field.name for field in model._meta.fields]
        writer.writerow(model_fields)

        # Queryset'teki her nesne için verileri CSV'ye yaz
        for obj in queryset:
            row = []
            for field in model_fields:
                value = getattr(obj, field)
                # ForeignKey gibi ilişkili alanlar için sadece primary key (id) değerini al
                if isinstance(value, Model):
                    value = value.pk
                row.append(value)
            writer.writerow(row)

        return response

    # GET isteği geldiyse veri yönetimi sayfasına yönlendir
    return redirect('moderasyon:veri_yonetimi')

@login_required
def veri_iceri_aktar(request):
    import csv
    import io
    from django.db import transaction # Atomik işlemler için
    from django.db.models import Model
    from django.apps import apps # Modelleri string isimlerinden almak için

    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu işlemi sadece moderatörler ve yöneticiler yapabilir.")
        return redirect('home')

    # POST isteği geldiğinde içeri aktarma işlemini gerçekleştir
    if request.method == 'POST':
        # Formdan seçilen modelin adını ve yüklenen CSV dosyasını al
        model_secimi = request.POST.get('model_secimi')
        csv_dosyasi = request.FILES.get('csv_dosyasi')

        # CSV dosyası yüklenmemişse hata mesajı göster
        if not csv_dosyasi:
            messages.error(request, "Lütfen bir CSV dosyası seçin.")
            return redirect('moderasyon:veri_yonetimi')

        # İçeri aktarılabilecek modellerin listesi
        importable_models = {
            'kullanici_profilleri': KullaniciProfili,
            'ders_istekleri': DersIstegi,
            'egitmen_basvurulari': EgitmenBasvurusu,
            'dersler': 'dersler.Ders', # String olarak belirtilen model
            'degerlendirmeler': Degerlendirme,
        }

        # Seçilen modelin içeri aktarılabilir modeller listesinde olup olmadığını kontrol et
        if model_secimi not in importable_models:
            messages.error(request, "Geçersiz model seçimi.")
            return redirect('moderasyon:veri_yonetimi')

        # Seçilen model nesnesini al
        model = importable_models[model_secimi]
        # Eğer model string olarak belirtilmişse, apps modülünü kullanarak gerçek model nesnesini al
        if isinstance(model, str):
            app_label, model_name = model.split('.')
            model = apps.get_model(app_label, model_name)

        # Yüklenen CSV dosyasını oku (UTF-8 formatında)
        csv_data = csv_dosyasi.read().decode('utf-8')
        # CSV verisini satır satır okumak için StringIO ve csv.reader kullan
        csv_reader = csv.reader(io.StringIO(csv_data))

        # CSV dosyasının başlık satırını oku
        try:
            header = next(csv_reader)
        except StopIteration:
            messages.error(request, "CSV dosyası boş.")
            return redirect('moderasyon:veri_yonetimi')

        # Modelin alan adlarını al
        model_fields = [field.name for field in model._meta.fields]

        # CSV başlıklarının model alanlarıyla tam olarak eşleşip eşleşmediğini kontrol et
        # (Basit bir kontrol, daha gelişmiş eşleştirme gerekebilir)
        if not all(column in model_fields for column in header):
             messages.error(request, f"CSV dosyasındaki sütunlar {model.__name__} modeli ile tam uyumlu değil. Beklenen alanlar: {', '.join(model_fields)}")
             return redirect('moderasyon:veri_yonetimi')

        try:
            # Veritabanı işlemlerini atomik yap (hepsi başarılı olursa commit et, aksi halde rollback yap)
            with transaction.atomic():
                eklenen_kayit_sayisi = 0

                # CSV'deki her satırı işle
                for row in csv_reader:
                    # Satır uzunluğu başlık uzunluğu ile eşleşmiyorsa atla
                    if len(row) != len(header):
                        messages.warning(request, f"Hatalı satır atlandı: {row}")
                        continue

                    # Satır verilerini başlıklarla eşleştirerek bir sözlük oluştur
                    data = {header[i]: row[i] for i in range(len(header))}

                    # Eğer 'id' alanı varsa ve doluysa, mevcut kaydı güncellemeye çalış
                    if 'id' in data and data['id']:
                        try:
                            # Belirtilen ID'ye sahip nesneyi al
                            obj = model.objects.get(id=data['id'])
                            # ID dışındaki alanları güncelle
                            for key, value in data.items():
                                if key != 'id':
                                    # İlişkili alanlar için uygun dönüşüm gerekebilir (şimdilik ham değer atanıyor)
                                    setattr(obj, key, value)
                            # Nesneyi kaydet
                            obj.save()
                        except model.DoesNotExist:
                            # ID'si belirtilen kayıt bulunamazsa, ID'yi silip yeni kayıt oluştur
                            del data['id']
                            # İlişkili alanlar için uygun dönüşüm gerekebilir
                            model.objects.create(**data)
                    else:
                        # 'id' alanı yoksa veya boşsa yeni kayıt oluştur
                        # İlişkili alanlar için uygun dönüşüm gerekebilir
                        model.objects.create(**data)

                    eklenen_kayit_sayisi += 1

                # Başarı mesajı göster
                messages.success(request, f"{eklenen_kayit_sayisi} kayıt başarıyla içeri aktarıldı.")
        except Exception as e:
            # İçeri aktarma sırasında bir hata oluşursa hata mesajı göster
            messages.error(request, f"İçeri aktarma sırasında bir hata oluştu: {str(e)}")

        # Veri yönetimi sayfasına yönlendir
        return redirect('moderasyon:veri_yonetimi')

    # GET isteği geldiyse veri yönetimi sayfasına yönlendir
    return redirect('moderasyon:veri_yonetimi')

@login_required
def veri_yonetimi(request):
    # Kullanıcının moderatör yetkisini kontrol et
    if not request.user.profil.is_moderator():
        messages.error(request, "Bu sayfaya erişim için moderatör yetkisi gerekmektedir.")
        return redirect('home')

    # Dışarı ve içeri aktarılabilecek modellerin listesi (arayüzde göstermek için)
    exportable_models = [
        {'id': 'kullanici_profilleri', 'name': 'Kullanıcı Profilleri'},
        {'id': 'ders_istekleri', 'name': 'Ders İstekleri'},
        {'id': 'egitmen_basvurulari', 'name': 'Eğitmen Başvuruları'},
        {'id': 'dersler', 'name': 'Dersler'},
        {'id': 'degerlendirmeler', 'name': 'Değerlendirmeler'},
    ]

    # Şablona gönderilecek bağlam verilerini hazırla
    context = {
        'exportable_models': exportable_models,
        'panel_title': 'Veri Yönetimi',
    }

    # Veri yönetimi şablonunu render et
    return render(request, 'moderasyon/veri_yonetimi.html', context)
