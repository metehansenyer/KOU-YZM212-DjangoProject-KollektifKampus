from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Avg, Count, Q, F
from django.db import IntegrityError
from django.http import JsonResponse

from .models import Degerlendirme
from talepler.models import DersIstegi
from kullanicilar.models import KullaniciProfili

@login_required
def degerlendirme_olustur(request, ders_istegi_id):
    # İlgili ders isteğini veya 404 hatasını al
    ders_istegi = get_object_or_404(DersIstegi, pk=ders_istegi_id)
    # Mevcut kullanıcının profilini veya 404 hatasını al
    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)

    # Kullanıcının ders isteğinin talep sahibi mi yoksa atanan eğitmeni mi olduğunu kontrol et
    is_talep_sahibi = (ders_istegi.talep_eden_kullanici == kullanici_profili)
    is_atanan_egitmen = (ders_istegi.atanan_egitmen == kullanici_profili)

    # Kullanıcı ders isteğiyle ilgili değilse veya ders henüz tamamlanmamışsa değerlendirme yapmasına izin verme
    if not (is_talep_sahibi or is_atanan_egitmen):
        # Hata mesajı göster ve ders detay sayfasına yönlendir
        messages.error(request, "Bu ders için değerlendirme yapma yetkiniz yok.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

    # Ders isteğinin durumunun 'TAMAMLANDI' olup olmadığını kontrol et
    if ders_istegi.talep_durumu != 'TAMAMLANDI':
        # Hata mesajı göster ve ders detay sayfasına yönlendir
        messages.error(request, "Sadece tamamlanan dersler için değerlendirme yapabilirsiniz.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

    # Değerlendirilecek kullanıcıyı belirle (talep sahibi eğitmeni, eğitmen talep sahibini değerlendirir)
    if is_talep_sahibi:
        degerlendirilen_kullanici = ders_istegi.atanan_egitmen
    else:  # is_atanan_egitmen
        degerlendirilen_kullanici = ders_istegi.talep_eden_kullanici

    # Mevcut kullanıcının, bu ders isteği için, belirlenen kullanıcıyı daha önce değerlendirip değerlendirmediğini kontrol et
    has_previous_review = Degerlendirme.objects.filter(
        ders_istegi=ders_istegi,
        degerlendiren_kullanici=kullanici_profili,
        degerlendirilen_kullanici=degerlendirilen_kullanici
    ).exists()

    # Daha önce değerlendirme yapılmışsa uyarı göster ve ders detay sayfasına yönlendir
    if has_previous_review:
        messages.warning(request, "Bu ders için zaten bir değerlendirme yapmışsınız.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

    # İstek POST ise (form gönderilmişse)
    if request.method == 'POST':
        # Formdan puan ve yorumu al
        puan = request.POST.get('puan')
        yorum = request.POST.get('yorum', '') # Yorum boş bırakılabilir

        # Puanın geçerli olup olmadığını kontrol et (sayısal, 1-5 arası)
        if not puan or not puan.isdigit() or int(puan) < 1 or int(puan) > 5:
            # Geçersiz puan durumunda hata mesajı göster ve formu tekrar göster
            messages.error(request, "Geçerli bir puan vermelisiniz (1-5 arası).")
            return render(request, 'geribildirim/degerlendirme_form.html', {
                'ders_istegi': ders_istegi,
                'degerlendirilen_kullanici': degerlendirilen_kullanici
            })

        try:
            # Yeni değerlendirme nesnesi oluştur
            degerlendirme = Degerlendirme(
                ders_istegi=ders_istegi,
                degerlendiren_kullanici=kullanici_profili,
                degerlendirilen_kullanici=degerlendirilen_kullanici,
                puan=int(puan),
                yorum=yorum
            )
            # Modelin clean metodunu çağırarak ek doğrulamaları yap (örn: kendini değerlendirmeme)
            degerlendirme.full_clean()
            # Değerlendirmeyi veritabanına kaydet
            degerlendirme.save()

            # Başarı mesajı göster ve ders detay sayfasına yönlendir
            messages.success(request, "Değerlendirmeniz başarıyla kaydedildi.")
            return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

        # unique_together kısıtlaması ihlal edilirse (zaten değerlendirme varsa)
        except IntegrityError:
            messages.error(request, "Bu ders için zaten bir değerlendirme yapmışsınız.")
            return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)
        # Diğer olası hataları yakala
        except Exception as e:
            # Hata mesajı göster ve formu tekrar göster
            messages.error(request, f"Değerlendirme kaydedilirken bir hata oluştu: {str(e)}")
            return render(request, 'geribildirim/degerlendirme_form.html', {
                'ders_istegi': ders_istegi,
                'degerlendirilen_kullanici': degerlendirilen_kullanici
            })

    # İstek GET ise (formu göstermek için)
    # Değerlendirme formunu render et
    return render(request, 'geribildirim/degerlendirme_form.html', {
        'ders_istegi': ders_istegi,
        'degerlendirilen_kullanici': degerlendirilen_kullanici
    })

@login_required
def kullanici_degerlendirmeleri(request, username):
    # Kullanıcı adına göre kullanıcı profilini veya 404 hatasını al
    kullanici_profili = get_object_or_404(KullaniciProfili, user__username=username)

    # Belirtilen kullanıcının aldığı tüm değerlendirmeleri getir
    # İlgili ders isteği ve değerlendiren kullanıcının user bilgisini önceden yükle (performans için)
    alinan_degerlendirmeler = Degerlendirme.objects.filter(
        degerlendirilen_kullanici=kullanici_profili
    ).select_related('ders_istegi', 'degerlendiren_kullanici__user')

    # Alınan değerlendirmelerin ortalama puanını hesapla
    ortalama_puan = alinan_degerlendirmeler.aggregate(Avg('puan'))['puan__avg']

    # Kullanıcının değerlendirmelerini gösteren sayfayı render et
    return render(request, 'geribildirim/kullanici_degerlendirmeleri.html', {
        'kullanici_profili': kullanici_profili, # Profili görüntülenen kullanıcı
        'alinan_degerlendirmeler': alinan_degerlendirmeler, # Aldığı değerlendirmeler listesi
        # Ortalama puanı bir ondalık basamağa yuvarla, yoksa None yap
        'ortalama_puan': round(ortalama_puan, 1) if ortalama_puan else None
    })

def en_iyi_egitmenler(request):
    # En az bir değerlendirme almış ve aktif olan kullanıcı profillerini (eğitmenleri) filtrele
    egitmenler = KullaniciProfili.objects.filter(
        aldigi_degerlendirmeler__isnull=False, # Aldığı değerlendirmesi olanlar
        aldigi_degerlendirmeler__degerlendiren_kullanici__user__is_active=True # Değerlendiren kullanıcı aktif mi?
    ).annotate(
        # Aldığı değerlendirmelerin ortalama puanını hesapla
        ortalama_puan=Avg('aldigi_degerlendirmeler__puan'),
        # Aldığı değerlendirme sayısını hesapla
        degerlendirme_sayisi=Count('aldigi_degerlendirmeler')
    ).order_by('-ortalama_puan')[:10] # Ortalama puana göre azalan sırada sırala ve ilk 10'u al

    # JSON yanıtı için eğitmen verilerini içeren bir liste oluştur
    egitmen_listesi = []
    # Sıralanmış eğitmenler üzerinde döngü yap
    for egitmen in egitmenler:
        # Her eğitmen için gerekli bilgileri bir sözlük olarak listeye ekle
        egitmen_listesi.append({
            'username': egitmen.user.username, # Kullanıcı adı
            'ad_soyad': egitmen.user.get_full_name(), # Ad Soyad
            # Ortalama puanı float'a çevir, yoksa 0 yap
            'ortalama_puan': float(egitmen.ortalama_puan) if egitmen.ortalama_puan else 0,
            'verilen_ders_sayisi': egitmen.degerlendirme_sayisi # Değiştirildi: Değerlendirme sayısı
        })

    # Oluşturulan listeyi JSON yanıtı olarak döndür
    # safe=False, listenin doğrudan JSON'a dönüştürülmesine izin verir
    return JsonResponse(egitmen_listesi, safe=False)
