from typing import Callable, Coroutine

from celery import shared_task
from main.services import IMAPService
from main.models import Account

import time

# async def fetch_and_save_message(account: Account):
#     imap = IMAPService(
#         email=account.email, 
#         password=account.password, 
#         imap_server=account.imap_server, 
#         imap_port=account.imap_port
#     )
#     async with imap as mail:
#         total_emails = await mail.get_total_count()

#         _, data = await mail.client.search('ALL')
#         email_ids = data[0].decode().split() # Получаем список ID писем

#         for email_id in email_ids:
#             email_message = await mail.get_message(email_id)
            
#             db_message = Letter(
#                 message_id=email_message.id,
#                 subject=email_message.subject,
#                 date_sent=email_message.date_sent,
#                 date_received=email_message.date_received,
#                 content=email_message.contents,
#                 attachments=email_message.attachments,
#             )
#             created_message = await account.letter_model_set.acreate(db_message)

#             print(f"ID: {email_message.id}")
#             print(f"Дата отправления: {email_message.date_sent}")
#             print(f"Дата получения: {email_message.date_received}")
#             print(f"Тема: {email_message.subject}")
#             print(f"Содержание: {email_message.contents}")
#             print(f"Приложения: {email_message.attachments}")
#             print("-" * 40)  # Разделитель между письмами

#         print('Done.')


@shared_task
def create_celery_task(task_type):
    time.sleep(int(task_type))
    return True


# @shared_task
# async def create_account_task(account: Account, func: Coroutine):
#     imap = IMAPService(
#         email=account.email, 
#         password=account.password, 
#         imap_server=account.imap_server, 
#         imap_port=account.imap_port
#     )
#     total_emails = await imap.get_total_count()
    
#     _, data = await imap.client.search('ALL')
#     email_ids = data[0].decode().split() # Получаем список ID писем
    
#     for email_id in email_ids:
#         email_message = await imap.get_message(email_id)
#         await func(email_message)
    
#     await imap.logout()
