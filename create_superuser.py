import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_community_hub.settings')
django.setup()

from api.models import User

# Criar superusuário se não existir
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        is_active=True,
        date_joined=timezone.now()
    )
    print("Superusuário 'admin' criado com sucesso!")
else:
    print("Superusuário 'admin' já existe.")
