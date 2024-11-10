import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.forms.models import model_to_dict

from main.services import IMAPService
from main.models import Account, Letter

class EmailConsumer(AsyncWebsocketConsumer):
    def percentage(self, value: int, total: int):
        result = (int(value) / total) * 100
        return f"{result:.2f}%"

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            try:
                input_data = json.loads(text_data)
                await self.handle_action(input_data)
            except json.JSONDecodeError:
                print("Ошибка декодирования JSON")
            except Exception as e:
                print(f"Произошла ошибка: {e} {text_data=}")
                raise

    async def send_json(self, data: dict):
        print(__file__, f"send_email({data=})")
        await self.send(text_data=json.dumps(data))

    async def handle_action(self, data: dict):
        action_type = data.get('action')
        
        if action_type == 'start_imap_read':
            await self.get_messages()
    
    def get_id(self, letter):
        ids = letter.message_id.split('.')
        return int(ids[1])
    
    @sync_to_async
    def get_accounts(self):
        return list(
            Account.objects.all()
        )

    @sync_to_async
    def get_letters(self, account):
        return account.letter_set.all()
    
    @sync_to_async
    def get_range(self, account, length):
        letters = account.letter_set.all()
        last = min(letters, key=lambda ltr: self.get_id(ltr)) if letters else None # 2071
        
        start = self.get_id(last) - 1 if last else length # 2200
        r = range(start, -1, -1)
        
        if start <= 0:
            return None
        
        return r

    async def save(self, account):
        async def done():
            await imap.logout()
            await self.send_json({
                "status": "done",
                "total": total_emails,
                "percent": 100,
                "account_id": account.id,
                "email": account.email
            })
        
        imap = await IMAPService(
            email=account.email, 
            password=account.password, 
            imap_server=account.imap_server, 
            imap_port=account.imap_port,
        ).connect()
        
        total_emails = await imap.get_total_count()
        data_range = await self.get_range(account, total_emails)
        
        if data_range:
            await self.send_json({"status": f"{data_range=}"})
            for email_id in data_range:
                email_message = await imap.get_message(str(email_id))
                percentage = self.percentage(email_message.id, total_emails)
                
                message_id = f'{account.id}.{email_message.id}'
                
                letter = await Letter.objects.acreate(
                    email_account_id=account.id,
                    message_id=message_id,
                    subject=email_message.subject,
                    date_sent=email_message.date_sent,
                    date_received=email_message.date_received,
                    content=email_message.contents,
                    attachments=email_message.attachments,
                )
                
                send_data = {
                    "status": "load",
                    "total": total_emails, 
                    "percent": percentage, 
                    "email":model_to_dict(letter)
                }
                
                await self.send_json(send_data)
            await done()
        else:
            await done()
    
    async def get_messages(self):
        await self.send_json({"status": "pending..."})
        accounts = await self.get_accounts()
        
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(self.save(a)) for a in accounts]
        
        await asyncio.gather(*tasks)
        await self.close()
