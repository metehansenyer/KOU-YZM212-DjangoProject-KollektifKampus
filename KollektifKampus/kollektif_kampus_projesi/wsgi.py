import os
from django.core.wsgi import get_wsgi_application

# Django ayarları için ortam değişkenini ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kollektif_kampus_projesi.settings')

# WSGI uygulamasını al
application = get_wsgi_application()
