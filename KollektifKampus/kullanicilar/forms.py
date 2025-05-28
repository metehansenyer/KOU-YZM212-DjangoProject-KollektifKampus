from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import KullaniciProfili, EgitmenBasvuruFormu

# Yeni kullanıcı kaydı için kullanılan form
class KullaniciKayitFormu(UserCreationForm):
    # E-posta alanı, .edu uzantısı zorunlu
    email = forms.EmailField(required=True, help_text=".edu uzantılı bir e-posta adresi giriniz.")
    # Ad alanı
    first_name = forms.CharField(max_length=30, required=True, label="Ad")
    # Soyad alanı
    last_name = forms.CharField(max_length=150, required=True, label="Soyad")

    class Meta(UserCreationForm.Meta):
        model = User
        # Varsayılan UserCreationForm alanlarına ad, soyad ve e-posta alanlarını ekle
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    # E-posta alanını temizleme ve doğrulama metodu
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # E-posta uzantısının .edu veya .edu.tr olup olmadığını kontrol et
        if not email.endswith(('.edu', '.edu.tr')):
            raise ValidationError("Lütfen geçerli bir .edu veya .edu.tr uzantılı e-posta adresi girin.", code='invalid_edu_email')
        # E-posta adresinin zaten kayıtlı olup olmadığını kontrol et
        if User.objects.filter(email=email).exists():
            raise ValidationError("Bu e-posta adresi zaten kayıtlı.", code='email_exists')
        return email

    # Formu kaydetme metodu
    def save(self, commit=True):
        # User nesnesini oluştur ama henüz veritabanına kaydetme
        user = super().save(commit=False)
        # Formdan gelen ad, soyad ve e-posta bilgilerini User nesnesine ata
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        # Eğer commit True ise User nesnesini veritabanına kaydet
        if commit:
            user.save()
        # Oluşturulan User nesnesini döndür
        return user

# Kullanıcı profilini güncellemek için kullanılan form
class KullaniciProfiliGuncelleForm(forms.ModelForm):
    # Kullanıcının adını güncellemek için alan
    first_name = forms.CharField(max_length=30, required=True, label="Ad")
    # Kullanıcının soyadını güncellemek için alan
    last_name = forms.CharField(max_length=150, required=True, label="Soyad")

    class Meta:
        model = KullaniciProfili
        # KullaniciProfili modelinden alınacak alanlar
        fields = ['universite', 'bolum', 'sinif', 'profil_fotografi_index', 'hakkinda']
        # Alanlar için özel widget tanımlamaları
        widgets = {
            'hakkinda': forms.Textarea(attrs={'rows': 4}),
        }
        # Alanlar için özel etiket tanımlamaları
        labels = {
            'profil_fotografi_index': 'Profil Fotoğrafı',
            'universite': 'Üniversite',
            'sinif': 'Sınıf',
            'bolum': 'Bölüm',
            'hakkinda': 'Hakkında',
        }

    # Form başlatılırken mevcut verileri yüklemek için __init__ metodu
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eğer form bir instance ile başlatıldıysa (yani mevcut bir profili güncelliyorsa)
        # User modelindeki ad ve soyad bilgilerini formun başlangıç değerlerine ata
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    # Formu kaydetme metodu
    def save(self, commit=True):
        # KullaniciProfili nesnesini kaydet (ModelForm'un varsayılan davranışı) ama henüz veritabanına kaydetme
        profil = super().save(commit=False)

        # İlişkili User nesnesini al
        user = profil.user
        # Formdan gelen ad ve soyad bilgilerini User nesnesine ata
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Eğer commit True ise User ve KullaniciProfili nesnelerini veritabanına kaydet
        if commit:
            user.save()
            profil.save()
        # Güncellenen KullaniciProfili nesnesini döndür
        return profil

# Kullanıcıların eğitmen rolüne başvuru yapmak için kullandıkları form
class EgitmenBasvuruForm(forms.ModelForm):
    class Meta:
        model = EgitmenBasvuruFormu
        # Formda gösterilecek alanlar
        fields = ['egitim_bilgileri', 'deneyim', 'uzmanlik_alanlari', 'motivasyon']
        # Alanlar için özel widget ve placeholder tanımlamaları
        widgets = {
            'egitim_bilgileri': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Eğitim geçmişiniz, mezun olduğunuz bölümler, devam ettiğiniz programlar...'}),
            'deneyim': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Eğitmenlik, öğretim, mentörlük alanındaki deneyimleriniz...'}),
            'uzmanlik_alanlari': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Hangi konularda/derslerde yetkinsiniz ve ders verebilirsiniz?'}),
            'motivasyon': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Neden eğitmen olmak istiyorsunuz? Kollektif Kampüs topluluğuna nasıl katkıda bulunmak istersiniz?'})
        }
        # Alanlar için özel etiket tanımlamaları
        labels = {
            'egitim_bilgileri': 'Eğitim Bilgileri',
            'deneyim': 'Deneyim',
            'uzmanlik_alanlari': 'Uzmanlık Alanları',
            'motivasyon': 'Motivasyon'
        }

# Moderatörlerin eğitmen başvurularını değerlendirmek için kullandıkları form
class EgitmenBasvuruDegerlendirmeForm(forms.ModelForm):
    class Meta:
        model = EgitmenBasvuruFormu
        # Formda gösterilecek alanlar
        fields = ['basvuru_durumu', 'red_sebebi']
        # Ret sebebi alanı için özel widget ve placeholder tanımlaması
        widgets = {
            'red_sebebi': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Başvuruyu reddetme sebebinizi açıklayın. Bu bilgi başvuru sahibine iletilecektir.'})
        }
        # Alanlar için özel etiket tanımlamaları
        labels = {
            'basvuru_durumu': 'Başvuru Durumu',
            'red_sebebi': 'Ret Sebebi (Sadece reddedildiğinde gerekli)'
        }

    # Formun genelini temizleme ve doğrulama metodu
    def clean(self):
        # Varsayılan temizleme işlemini yap
        cleaned_data = super().clean()
        # Başvuru durumu ve ret sebebi alanlarını al
        basvuru_durumu = cleaned_data.get('basvuru_durumu')
        red_sebebi = cleaned_data.get('red_sebebi')

        # Eğer başvuru durumu REDDEDILDI ise ve ret sebebi boşsa hata fırlat
        if basvuru_durumu == 'REDDEDILDI' and not red_sebebi:
            raise forms.ValidationError("Başvuruyu reddettiğinizde ret sebebi belirtmelisiniz.")

        # Temizlenmiş veriyi döndür
        return cleaned_data