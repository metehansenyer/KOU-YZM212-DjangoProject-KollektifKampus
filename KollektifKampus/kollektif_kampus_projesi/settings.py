from pathlib import Path
import os
from dotenv import load_dotenv

# Proje ana dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# .env dosyasını yükle
load_dotenv(BASE_DIR / '.env')

# Güvenlik ayarları
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Uygulama listesi
INSTALLED_APPS = [
    # Django temel uygulamaları
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Harici uygulamalar
    'channels',
    'daphne',
    
    'django.contrib.staticfiles',

    # Proje uygulamaları
    'kullanicilar.apps.KullanicilarConfig',
    'dersler.apps.DerslerConfig',
    'talepler.apps.TaleplerConfig',
    'iletisim.apps.IletisimConfig',
    'geribildirim.apps.GeribildirimConfig',
    'moderasyon.apps.ModerasyonConfig',
]

# Ara yazılım ayarları
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'kullanicilar.middleware.KullaniciEngelKontrolMiddleware',
]

# URL yapılandırması
ROOT_URLCONF = 'kollektif_kampus_projesi.urls'

# Şablon ayarları
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI uygulama tanımı
WSGI_APPLICATION = 'kollektif_kampus_projesi.wsgi.application'

# Veritabanı ayarları
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.path.join(BASE_DIR, os.getenv('DB_NAME', 'db.sqlite3')),
    }
}

# Şifre doğrulama kuralları
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Dil ve saat dilimi ayarları
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Statik dosya ayarları
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Varsayılan birincil anahtar türü
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Giriş ve çıkış yönlendirme ayarları
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Channels ayarları
ASGI_APPLICATION = 'kollektif_kampus_projesi.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': os.getenv('CHANNEL_LAYER_BACKEND', 'channels.layers.InMemoryChannelLayer')
    },
}

# E-posta ayarları
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
