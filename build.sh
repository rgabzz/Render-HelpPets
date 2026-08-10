#!/usr/bin/env bash
# Script de build usado pelo Render.
set -o errexit

pip install -r requirements.txt

echo "----- Diagnóstico da conexão com o banco -----"
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()
from django.conf import settings
db = settings.DATABASES['default']
print('ENGINE:', db['ENGINE'])
print('HOST:', repr(db['HOST']))
print('PORT:', repr(db['PORT']))
print('NAME:', repr(db['NAME']))
print('USER:', repr(db['USER']))
print('PASSWORD length:', len(db['PASSWORD']) if db['PASSWORD'] else 0)
"
echo "-----------------------------------------------"

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_data
