from django.contrib.postgres.fields import ArrayField
from django.db import models


class Account(models.Model):
    """Модель аккаунта почты"""

    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    imap_server = models.CharField(max_length=100, default="imap.default.com")
    imap_port = models.IntegerField(default=993)


class Letter(models.Model):
    """Модель электронного письма"""

    email_account = models.ForeignKey(Account, on_delete=models.CASCADE)
    message_id = models.CharField(unique=True, max_length=20)
    subject = models.TextField()
    date_sent = models.CharField(max_length=100)
    date_received = models.CharField(max_length=100)
    content = models.TextField()
    attachments = ArrayField(models.CharField(max_length=100))
