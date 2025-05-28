# KOÜ Yazılım Müh. Web Programlama Dersi Dönem Projesi

Kocaeli Üniversitesi Mühendislik Fakültesi Yazılım Mühendisliği 24-25 Web Programlama Dersi Projesi. KollektifKampus.

# İçerik

- [Kullanılan Araçlar](https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus?tab=readme-ov-file#kullanılan-araçlar)
- [Amaç](https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus?tab=readme-ov-file#amaç)
- [Projeden Beklenenler](https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus?tab=readme-ov-file#projeden-beklenenler)
- [Karşılanan Beklentiler](https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus?tab=readme-ov-file#karşılanan-beklentiler)
- [İndirme ve Çalıştırma](https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus?tab=readme-ov-file#i̇ndirme-ve-çalıştırma)
- [Teşekkürler](https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus?tab=readme-ov-file#teşekkürler)
- [Proje Ekibi](https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus?tab=readme-ov-file#proje-ekibi)

## Kullanılan Araçlar

<p align="center">
  <a href="https://html.spec.whatwg.org/multipage/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original.svg" alt="html" width="40" height="40"/> </a>
  <a href="https://www.w3.org/Style/CSS/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original.svg" alt="css" width="40" height="40"/> </a>
  <a href="https://www.python.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a>
  <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/django/django-plain.svg" alt="django" width="40" height="40"/> </a>
  <a href="https://www.sqlite.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/sqlite/sqlite-original.svg" alt="sqlite" width="40" height="40"/> </a>
  <a href="https://code.visualstudio.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/vscode/vscode-original.svg" alt="vscode" width="40" height="40"/> </a>
  <a href="https://github.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/github/github-original.svg" alt="github" width="40" height="40"/> </a>
</p>

- Site oluşturulurken Django Framework'ü, Python, HTML, CSS ve SQLite kullanılmıştır
- Tercih ettiğimiz kod editörü Visual Studio Code
- GitHub versiyon kontrol sistemi olarak kullanılmıştır

| Kullanılan Araç | Sürüm |
|:---:|:---:|
| Python | 3.10+ |
| Django | 5.0+ |
| SQLite | 3 |
| HTML | 5 |
| CSS | 3 |

## Amaç

KollektifKampus, üniversite öğrencilerinin birbirlerinden öğrenmesini ve bilgi paylaşımını kolaylaştırmayı amaçlayan bir akran öğrenme platformudur. Öğrenciler bu platformda ders talepleri oluşturabilir, eğitmen olarak kaydolabilir ve diğer öğrencilere yardımcı olabilir.

## Projeden Beklenenler

```json
{
  "Özgün Değer": "Projenin günlük yaşam problemlerine yazılım mühendisliği bakış açısıyla yenilikçi çözüm önermesi",
  "Ana Veri Modeli": "En az iki Django modeli ve her tabloda en az 5 alan bulunması",
  "İlişkisel Veri Modeli": "Many-to-One veya Many-to-Many ilişkiler içermesi",
  "CRUD İşlemleri": "Admin arayüzünden farklı olarak ana veri modeli üzerinde CRUD işlemleri için sayfalar",
  "Şablon Kullanımı": "Django şablon dili özellikleri (değişken, etiket, filtre)",
  "Kimlik Doğrulama": "Sisteme kayıtlı kullanıcıların erişimi, register, login, logout, reset password",
  "Yetkilendirme": "En az iki farklı kullanıcı tipi ve farklı yetkiler",
  "Arama": "Ana verilerde en az 3 alana göre arama yapılabilen sayfa",
  "İçeri/Dışarı Veri Aktarma": "Temel verilerin toplu olarak içeri ve dışarı aktarılabilmesi",
  "Admin Arayüzü": "Django admin arayüzünün veri modelleri üzerinde çalışması",
  "HTML ve CSS": "Belirli yapısal, içeriksel ve görsel kriterleri karşılama"
}
```

## Karşılanan Beklentiler

| Beklenti | Durum | Detay |
|:---:|:---:|:---:|
| Özgün Değer | ✅ | KollektifKampus, üniversite öğrencilerinin bilgi paylaşımı ve akran öğrenmeyi kolaylaştıran yenilikçi bir platform sunuyor. |
| Ana Veri Modeli | ✅ | Projede DersIstegi, KullaniciProfili, Ders gibi birden fazla model bulunmakta ve her biri 5'ten fazla alan içeriyor. |
| İlişkisel Veri Modeli | ✅ | KullaniciProfili-DersIstegi (One-to-Many), Ders-DersIstegi (One-to-Many) ve diğer modeller arasında ilişkiler tanımlanmıştır. |
| CRUD İşlemleri | ✅ | Ders talepleri için ekleme, görüntüleme, güncelleme ve silme işlemleri için özel sayfalar oluşturulmuştur. |
| Şablon Kullanımı | ✅ | Django template language kullanılarak dinamik içerik üretilmiştir. |
| Kimlik Doğrulama | ✅ | Kullanıcı kaydı, giriş, çıkış ve şifre sıfırlama özellikleri eklenmiştir. |
| Yetkilendirme | ✅ | Normal Kullanıcı, Eğitmen, Moderatör ve Admin rolleri tanımlanmış, her biri için farklı yetkiler belirlenmiştir. |
| Arama | ✅ | Ders talepleri için başlık, açıklama, kullanıcı adı, kategori ve seviye gibi alanlara göre arama yapılabilmektedir. |
| İçeri/Dışarı Veri Aktarma | ✅ | Ders, kullanıcı ve talep verilerinin import/export edilebilmesi için işlevler eklenmiştir. |
| Admin Arayüzü | ✅ | Django admin paneli özelleştirilmiş ve tüm modeller için CRUD işlemleri aktif edilmiştir. |
| HTML ve CSS | ✅ | İstenilen tüm HTML yapıları (başlıklar, listeler, tablolar, formlar, div'ler) ve CSS kuralları uygulanmıştır. |

## İndirme ve Çalıştırma

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1. Repoyu klonlayın:
```
git clone https://github.com/metehansenyer/KOU-YZM212-DjangoProject-KollektifKampus.git
cd KollektifKampus
```

2. Sanal ortam oluşturun ve aktifleştirin:
```
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```
pip install -r requirements.txt
```

4. Veritabanı migrasyonlarını uygulayın:
```
python manage.py migrate
```

5. Geliştirme sunucusunu başlatın:
```
python manage.py runserver
```

6. Tarayıcınızda http://127.0.0.1:8000/ adresine giderek uygulamaya erişebilirsiniz.

## Teşekkürler

Web Programlama alanındaki öğrenimimizde katkılarından dolayı Kocaeli Üniversitesi Yazılım Mühendisliği Bölümü'den Dr. Öğr. Üyesi Levent BAYINDIR hocamıza teşekkürlerimizi arz ederiz.

## Proje Ekibi

| İsim Soyisim | Öğrenci Numarası | Linkedin |
|:---:|:---:|:---:|
| Metehan Şenyer | 230229047 | [@Metehan Şenyer](https://www.linkedin.com/in/metehansenyer/) |
| Alperen Türk | 230229019 | [@Alperen Türk](https://www.linkedin.com/in/alperen-t%C3%BCrk-1508b6337/) |
| Asaf Erdem Kılıç | 230229070 | [@Asaf Kılıç](https://www.linkedin.com/in/asaf-k%C4%B1l%C4%B1%C3%A7-4b33bb308/) |
| Hilal Pınar | 230229030 | [@Hilal Pınar](https://www.linkedin.com/in/hilal-p%C4%B1nar-8856b62a0/) |
| Derya Hümeyra Mercan | 230229039 | [@Derya Hümeyra Mercan](https://www.linkedin.com/in/derya-mercan-987952296/) |
