from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q, Count, Max, F
from django.utils import timezone

from kullanicilar.models import KullaniciProfili
from talepler.models import DersIstegi
from .models import Sohbet, Mesaj

@login_required
def kullanici_sohbetleri(request):
    # Kullanıcının katıldığı sohbetleri listeler.
    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)

    # Kullanıcının katıldığı sohbetleri getir, son mesaj tarihini ve okunmayan mesaj sayısını hesapla.
    sohbetler = Sohbet.objects.filter(
        katilimcilar=kullanici_profili
    ).annotate(
        son_mesaj_tarihi=Max('mesajlar__gonderilme_tarihi'),
        okunmayan_mesaj_sayisi=Count(
            'mesajlar',
            filter=Q(
                mesajlar__okundu_bilgisi=False,
                mesajlar__gonderen_kullanici__isnull=False # Sistem mesajlarını sayma
            ) & ~Q(mesajlar__gonderen_kullanici=kullanici_profili) # Kendi gönderdiği mesajları sayma
        )
    ).order_by('-son_mesaj_tarihi', '-olusturulma_tarihi') # Son mesaja göre veya oluşturulma tarihine göre sırala

    return render(request, 'iletisim/sohbetler.html', {
        'sohbetler': sohbetler,
        'kullanici_profili': kullanici_profili
    })

@login_required
def sohbet_detay(request, sohbet_id):
    # Belirli bir sohbetin detayını ve mesajlarını gösterir.
    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)
    sohbet = get_object_or_404(Sohbet, id=sohbet_id)

    # Kullanıcının sohbete erişimini kontrol et.
    if kullanici_profili not in sohbet.katilimcilar.all():
        messages.error(request, "Bu sohbete erişim yetkiniz bulunmamaktadır.")
        return redirect('iletisim:kullanici_sohbetleri')

    # Kullanıcı sohbete girdiğinde, kendi göndermediği okunmamış mesajları okundu olarak işaretle.
    Mesaj.objects.filter(
        sohbet=sohbet,
        okundu_bilgisi=False
    ).filter(
        ~Q(gonderen_kullanici=kullanici_profili)
    ).update(okundu_bilgisi=True)

    # Sohbetin mesajlarını gönderen kullanıcı bilgisiyle birlikte getir.
    mesajlar = sohbet.mesajlar.select_related('gonderen_kullanici__user').all()

    # Karşı tarafı belirle (genellikle 2 kişilik sohbetler için).
    diger_katilimcilar = sohbet.katilimcilar.exclude(id=kullanici_profili.id)
    karsi_taraf = diger_katilimcilar.first() if diger_katilimcilar.exists() else None

    return render(request, 'iletisim/sohbet_detay.html', {
        'sohbet': sohbet,
        'mesajlar': mesajlar,
        'kullanici_profili': kullanici_profili,
        'karsi_taraf': karsi_taraf
    })

@login_required
def mesaj_gonder(request, sohbet_id):
    # Yeni bir mesaj gönderir (AJAX endpoint).
    # Sadece POST isteklerine izin ver.
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Geçersiz istek metodu.'})

    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)
    sohbet = get_object_or_404(Sohbet, id=sohbet_id)

    # Kullanıcının sohbete erişimini kontrol et.
    if kullanici_profili not in sohbet.katilimcilar.all():
        return JsonResponse({'success': False, 'error': 'Bu sohbete erişim yetkiniz bulunmamaktadır.'})

    # Mesaj içeriğini al ve boş olup olmadığını kontrol et.
    icerik = request.POST.get('icerik', '').strip()
    if not icerik:
        return JsonResponse({'success': False, 'error': 'Boş mesaj gönderilemez.'})

    # Yeni mesajı veritabanına kaydet.
    mesaj = Mesaj.objects.create(
        sohbet=sohbet,
        gonderen_kullanici=kullanici_profili,
        icerik=icerik
    )

    # Başarılı yanıt döndür.
    return JsonResponse({
        'success': True,
        'mesaj_id': mesaj.id,
        'gonderen': kullanici_profili.user.username,
        'icerik': mesaj.icerik,
        'gonderilme_tarihi': mesaj.gonderilme_tarihi.strftime('%d.%m.%Y %H:%M')
    })

@login_required
def sohbet_baslat(request, ders_istegi_id):
    # Ders isteği kabul edildiğinde öğrenci ve eğitmen arasında otomatik olarak bir sohbet kanalı oluşturur.
    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)
    ders_istegi = get_object_or_404(DersIstegi, id=ders_istegi_id)

    # Kullanıcının sohbet başlatma yetkisini kontrol et (talep eden veya atanan eğitmen).
    if kullanici_profili != ders_istegi.talep_eden_kullanici and kullanici_profili != ders_istegi.atanan_egitmen:
        messages.error(request, "Bu ders isteği için sohbet başlatma yetkiniz bulunmamaktadır.")
        return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

    # Ders isteği için zaten bir sohbet kanalı var mı kontrol et.
    try:
        sohbet = Sohbet.objects.get(ders_istegi=ders_istegi)
        messages.info(request, "Bu ders isteği için zaten bir sohbet başlatılmış.")
    except Sohbet.DoesNotExist:
        # Ders isteği için eğitmen atanmış mı kontrol et.
        if not ders_istegi.atanan_egitmen:
            messages.error(request, "Bu ders isteği için henüz bir eğitmen atanmamış.")
            return redirect('talepler:ders_istegi_detay', pk=ders_istegi_id)

        # Yeni sohbet kanalını oluştur.
        sohbet = Sohbet.objects.create(ders_istegi=ders_istegi)

        # Sohbete katılımcıları ekle (ders isteği sahibi ve atanan eğitmen).
        sohbet.katilimcilar.add(ders_istegi.talep_eden_kullanici, ders_istegi.atanan_egitmen)

        # Hoş geldiniz sistem mesajı oluştur.
        Mesaj.objects.create(
            sohbet=sohbet,
            gonderen_kullanici=None,  # Sistem mesajı olduğu için gönderen kullanıcı yok
            icerik="Hoş geldiniz! Bu sohbet kanalı ders isteğiyle ilgili iletişim kurmanız için oluşturulmuştur."
        )

        messages.success(request, "Sohbet başarıyla oluşturuldu.")

    # Oluşturulan veya var olan sohbetin detay sayfasına yönlendir.
    return redirect('iletisim:sohbet_detay', sohbet_id=sohbet.id)

@login_required
def okunmayan_mesaj_sayisi(request):
    # Kullanıcının okunmayan mesaj sayısını JSON olarak döndürür.
    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)

    # Kullanıcının katıldığı sohbetlerdeki, kendi göndermediği okunmamış mesajları say.
    okunmayan_mesaj_sayisi = Mesaj.objects.filter(
        sohbet__katilimcilar=kullanici_profili,  # Kullanıcının katıldığı sohbetlerdeki
        okundu_bilgisi=False  # Okunmamış
    ).filter(
        ~Q(gonderen_kullanici=kullanici_profili)  # Kendisinin göndermediği
    ).count()

    return JsonResponse({'okunmayan_mesaj_sayisi': okunmayan_mesaj_sayisi})

@login_required
def son_mesajlar(request):
    # Kullanıcının son sohbetlerini ve her sohbetin son mesajını JSON olarak döndürür.
    kullanici_profili = get_object_or_404(KullaniciProfili, user=request.user)

    # Kullanıcının katıldığı sohbetleri son mesaj tarihine göre sırala ve ilk 5'ini al.
    son_sohbetler = Sohbet.objects.filter(
        katilimcilar=kullanici_profili
    ).annotate(
        son_mesaj_tarihi=Max('mesajlar__gonderilme_tarihi')
    ).order_by('-son_mesaj_tarihi')[:5]

    sohbetler_listesi = []
    for sohbet in son_sohbetler:
        # Her sohbetin en son mesajını getir.
        son_mesaj = sohbet.mesajlar.order_by('-gonderilme_tarihi').first()
        if son_mesaj:
            # Karşı tarafı belirle (kullanıcının dışındaki katılımcı).
            karsi_taraf = sohbet.katilimcilar.exclude(id=kullanici_profili.id).first()
            # Eğer karşı taraf yoksa (örn. tek kişilik sohbet veya hata), bu sohbeti atla.
            if not karsi_taraf:
                continue

            # Karşı tarafın adını veya kullanıcı adını al.
            karsi_taraf_adi = karsi_taraf.user.get_full_name() or karsi_taraf.user.username

            # Mesaj içeriğini formatla (kullanıcı kendi gönderdiyse "Sen: " ekle).
            mesaj_metni = son_mesaj.icerik
            if son_mesaj.gonderen_kullanici == kullanici_profili:
                mesaj_metni = f"Sen: {mesaj_metni}"

            # Sohbet bilgilerini listeye ekle.
            sohbetler_listesi.append({
                'sohbet_id': sohbet.id,
                'karsi_taraf_adi': karsi_taraf_adi,
                'karsi_taraf_username': karsi_taraf.user.username,
                'son_mesaj': mesaj_metni,
                'tarih': son_mesaj.gonderilme_tarihi.strftime('%d.%m.%Y %H:%M')
            })

    # Sohbetler listesini JSON olarak döndür.
    return JsonResponse(sohbetler_listesi, safe=False)
