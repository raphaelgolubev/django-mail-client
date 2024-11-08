# create_superuser.py
import os
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_superuser(username, email, password):
    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Суперпользователь '{username}' успешно создан.")
    else:
        print(f"Суперпользователь '{username}' уже существует.")


def create_admin():
    password = os.environ.get("ADMIN_PASSWORD", 'admin')
    email = os.environ.get("ADMIN_EMAIL", 'admin@example.com')
    username = os.environ.get("ADMIN_USERNAME", 'admin')
    create_superuser(username, email, password)