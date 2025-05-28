from django import forms
from .models import DersIstegi, Ders, EgitmenBasvurusu

# Ders isteği oluşturmak veya güncellemek için kullanılan form
class DersIstegiForm(forms.ModelForm):
    # Ders seçimi için ModelChoiceField kullanılır.
    # Sadece aktif olan dersler listelenir ve seçim zorunludur.
    ders = forms.ModelChoiceField(
        queryset=Ders.objects.filter(aktif_mi=True),
        required=True,
        label="İlgili Standart Ders",
        help_text="Listeden bir ders seçmeniz gerekmektedir.",
        error_messages={'required': "Lütfen listeden ilgili bir ders seçiniz."}
    )

    # Talep başlığı alanı, maksimum uzunluk ve zorunluluk belirtilir.
    talep_basligi = forms.CharField(
        max_length=255,
        label="Talep Başlığı / Özel Konu",
        help_text="Örn: Python Fonksiyonlar, Diferansiyel Denklemler Giriş, Almanca A1 Konuşma Pratiği",
        error_messages={'required': "Talep başlığı boş bırakılamaz. Lütfen konunuzu belirtin."}
    )

    # Detaylı açıklama alanı, Textarea widget'ı ile satır sayısı belirtilir ve zorunludur.
    detayli_aciklama = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label="Açıklama (Ne öğrenmek istiyorsunuz?)",
        help_text="Öğrenmek istediğiniz konular, mevcut bilgi seviyeniz, dersten beklentileriniz ve eğer varsa ders için ayırabileceğiniz bütçe veya zaman gibi detayları belirtiniz.",
        error_messages={'required': "Lütfen talebinizle ilgili detaylı bir açıklama ekleyin."}
    )

    # Teklif edilen karşılık alanı, Textarea widget'ı ile satır sayısı belirtilir ve zorunludur.
    teklif_edilen_karsilik = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        label="Ders Karşılığında Teklifiniz",
        help_text="Ders karşılığında ne teklif ediyorsunuz? (Örn: bir kahve, cüzi bir ücret, tatlı, başka bir konuda ders vb.)",
        error_messages={'required': "Lütfen ders karşılığında teklifinizi belirtin."}
    )

    # Formun model ve alan ayarları
    class Meta:
        model = DersIstegi
        fields = [
            'ders',
            'talep_basligi',
            'detayli_aciklama',
            'beklenen_seviye',
            'teklif_edilen_karsilik',
            'mekan_tercihi',
            'zaman_tercihi'
        ]

        # Alanlar için özel etiketler
        labels = {
            'beklenen_seviye': 'Aradığınız Bilgi Seviyesi',
            'mekan_tercihi': 'Tercih Ettiğiniz Buluşma Yeri/Yöntemi',
            'zaman_tercihi': 'Uygun Olduğunuz Zamanlar (Genel)',
        }

        # Alanlar için özel yardım metinleri
        help_texts = {
            'beklenen_seviye': 'Dersi verecek kişiden beklediğiniz bilgi seviyesini seçiniz.',
            'mekan_tercihi': 'Kampüs kütüphanesi, X Kafe, online (Zoom/Discord), fakülte binası vb.',
            'zaman_tercihi': 'Hafta içi akşamları, Cumartesi öğleden sonra, belirli günler vb.'
        }

        # Alanlar için özel hata mesajları
        error_messages = {
            'beklenen_seviye': {'required': "Lütfen beklediğiniz bilgi seviyesini seçin."},
            'mekan_tercihi': {'required': "Lütfen tercih ettiğiniz buluşma yerini belirtin."},
            'zaman_tercihi': {'required': "Lütfen uygun olduğunuz zamanları belirtin."}
        }

        # Alanlar için özel widget ayarları (örn: satır sayısı, zorunluluk)
        widgets = {
            'mekan_tercihi': forms.Textarea(attrs={'rows': 2, 'required': True}),
            'zaman_tercihi': forms.Textarea(attrs={'rows': 2, 'required': True}),
        }

    # Form genelinde ek doğrulama yapmak için clean metodu
    def clean(self):
        cleaned_data = super().clean()
        # Ek doğrulamalar buraya eklenebilir
        return cleaned_data

# Eğitmen başvurusu yapmak için kullanılan form
class EgitmenBasvurusuForm(forms.ModelForm):
    # Formun model ve alan ayarları
    class Meta:
        model = EgitmenBasvurusu
        fields = ['basvuru_mesaji']
        # Başvuru mesajı alanı için widget ayarları (satır sayısı, placeholder)
        widgets = {
            'basvuru_mesaji': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Ders isteği sahibine iletmek istediğiniz ek bir mesajınız varsa buraya yazabilirsiniz (isteğe bağlı).'
                }
            )
        }
        # Başvuru mesajı alanı için özel etiket
        labels = {
            'basvuru_mesaji': 'Başvuru Mesajınız (İsteğe Bağlı)'
        }