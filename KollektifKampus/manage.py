# Django yönetim görevleri için komut satırı aracı.
# Bu dosya, Django projesinin yönetim komutlarını çalıştırmak için kullanılır.

import os
import sys

def main():
    # Ana fonksiyon: Yönetim görevlerini çalıştırır.
    # Yönetim görevlerini çalıştırır.

    # Django ayarları için ortam değişkenini ayarlar.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kollektif_kampus_projesi.settings')
    try:
        # Django'nun komut satırı aracını içe aktarır.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Django içe aktarılamazsa hata fırlatır.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
        # Django'nun içe aktarılamaması durumunda gösterilecek hata mesajı.

    # Komut satırı argümanları ile yönetim komutunu çalıştırır.
    execute_from_command_line(sys.argv)


# Eğer bu dosya doğrudan çalıştırılırsa main() fonksiyonunu çağır.
if __name__ == '__main__':
    # Ana fonksiyonu çalıştır.
    main()
