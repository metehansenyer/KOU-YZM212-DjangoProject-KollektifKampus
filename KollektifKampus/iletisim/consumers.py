import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Sohbet, Mesaj
from kullanicilar.models import KullaniciProfili

class SohbetConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # WebSocket bağlantısı kurulduğunda çalışır
        self.user = self.scope["user"]

        # Kullanıcının kimliği doğrulanmamışsa bağlantıyı kapat
        if not self.user.is_authenticated:
            await self.close()
            return

        # URL'den sohbet kimliğini (ID) al
        self.sohbet_id = self.scope['url_route']['kwargs']['sohbet_id']
        # Channels grup adını sohbet ID'sine göre oluştur
        self.sohbet_group_name = f'sohbet_{self.sohbet_id}'

        # Kullanıcının bu sohbete (grup) erişim yetkisini veritabanından kontrol et
        if not await self.kullanici_sohbete_erisebilir(self.sohbet_id, self.user.id):
            # Erişim yoksa bağlantıyı kapat
            await self.close()
            return

        # Kullanıcıyı Channels grubuna ekle
        await self.channel_layer.group_add(
            self.sohbet_group_name,
            self.channel_name
        )

        # WebSocket bağlantısını kabul et
        await self.accept()

        # Bağlantı başarılı olduğunda istemciye bilgi mesajı gönder
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket bağlantısı başarılı',
            'user_id': self.user.id,
            'username': self.user.username
        }))

    async def disconnect(self, close_code):
        # WebSocket bağlantısı kesildiğinde çalışır
        # Eğer grup adı tanımlanmışsa, kullanıcıyı Channels grubundan çıkar
        if hasattr(self, 'sohbet_group_name'):
            await self.channel_layer.group_discard(
                self.sohbet_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # İstemciden WebSocket üzerinden mesaj alındığında çalışır
        text_data_json = json.loads(text_data)
        # Mesajın tipini al (örn: 'sohbet_mesaji', 'yaziyor')
        mesaj_tipi = text_data_json.get('type')

        # Eğer mesaj tipi 'sohbet_mesaji' ise
        if mesaj_tipi == 'sohbet_mesaji':
            # Mesaj içeriğini al
            icerik = text_data_json.get('mesaj')

            # Mesaj içeriği boş değilse işleme devam et
            if icerik:
                # Mesajı veritabanına kaydet (asenkron veritabanı işlemi)
                mesaj = await self.mesaj_olustur(self.sohbet_id, self.user.id, icerik)

                # Sohbet grubundaki tüm bağlı istemcilere mesajı ilet
                await self.channel_layer.group_send(
                    self.sohbet_group_name,
                    {
                        'type': 'sohbet_mesaji', # İstemcide hangi handler'ın çalışacağını belirtir
                        'mesaj_id': mesaj.id,
                        'kullanici_id': self.user.id,
                        'kullanici_adi': self.user.username,
                        'mesaj': mesaj.icerik,
                        'gonderilme_tarihi': mesaj.gonderilme_tarihi.strftime('%d.%m.%Y %H:%M'), # Tarihi formatla
                    }
                )

        # Eğer mesaj tipi 'yaziyor' ise
        elif mesaj_tipi == 'yaziyor':
            # "Yazıyor..." durum bilgisini al (True/False)
            yaziyor_durumu = text_data_json.get('yaziyor')
            # Sohbet grubundaki tüm bağlı istemcilere yazma durumunu bildir
            await self.channel_layer.group_send(
                self.sohbet_group_name,
                {
                    'type': 'yaziyor_bildirimi', # İstemcide hangi handler'ın çalışacağını belirtir
                    'kullanici_id': self.user.id,
                    'kullanici_adi': self.user.username,
                    'yaziyor': yaziyor_durumu
                }
            )

    async def sohbet_mesaji(self, event):
        # Channels grubundan 'sohbet_mesaji' tipinde bir mesaj alındığında çalışır
        # Mesajı WebSocket üzerinden istemciye gönder
        await self.send(text_data=json.dumps({
            'type': 'sohbet_mesaji',
            'mesaj_id': event['mesaj_id'],
            'kullanici_id': event['kullanici_id'],
            'kullanici_adi': event['kullanici_adi'],
            'mesaj': event['mesaj'],
            'gonderilme_tarihi': event['gonderilme_tarihi']
        }))

    async def yaziyor_bildirimi(self, event):
        # Channels grubundan 'yaziyor_bildirimi' tipinde bir mesaj alındığında çalışır
        # Yazma durumu bildirimini WebSocket üzerinden istemciye gönder
        await self.send(text_data=json.dumps({
            'type': 'yaziyor_bildirimi',
            'kullanici_id': event['kullanici_id'],
            'kullanici_adi': event['kullanici_adi'],
            'yaziyor': event['yaziyor']
        }))

    @database_sync_to_async
    def kullanici_sohbete_erisebilir(self, sohbet_id, kullanici_id):
        # Belirtilen kullanıcının belirtilen sohbete (grup) erişim yetkisini veritabanından kontrol eder
        try:
            # Kullanıcı profilini ve sohbeti veritabanından getir
            kullanici_profili = KullaniciProfili.objects.get(user_id=kullanici_id)
            sohbet = Sohbet.objects.get(id=sohbet_id)
            # Kullanıcı profilinin sohbetin katılımcıları arasında olup olmadığını kontrol et
            return kullanici_profili in sohbet.katilimcilar.all()
        except (Sohbet.DoesNotExist, KullaniciProfili.DoesNotExist):
            # Sohbet veya kullanıcı profili bulunamazsa erişim yok demektir
            return False

    @database_sync_to_async
    def mesaj_olustur(self, sohbet_id, kullanici_id, icerik):
        # Veritabanında yeni bir mesaj kaydı oluşturur
        # Mesajı gönderen kullanıcı profilini ve ait olduğu sohbeti getir
        kullanici_profili = KullaniciProfili.objects.get(user_id=kullanici_id)
        sohbet = Sohbet.objects.get(id=sohbet_id)

        # Mesaj nesnesini oluştur ve veritabanına kaydet
        return Mesaj.objects.create(
            sohbet=sohbet,
            gonderen_kullanici=kullanici_profili,
            icerik=icerik
        )