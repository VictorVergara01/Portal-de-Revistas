import os
from django.contrib.auth.models import User

# Datos del superusuario
USERNAME = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f"Superuser '{USERNAME}' created successfully.")
else:
    print(f"Superuser '{USERNAME}' already exists.")
