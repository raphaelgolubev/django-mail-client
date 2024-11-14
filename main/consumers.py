import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms.models import model_to_dict

from main.models import Account, Letter
from main.services import IMAPService


class ConsumerUtils:
    @staticmethod
    def get_id(letter):
        return int(letter.message_id)

    @staticmethod
    def percentage(value: int, total: int):
        result = (int(value) / total) * 100
        return f"{result:.2f}%"

    @staticmethod
    async def get_account(id: int):
        return await Account.objects.aget(id=id)

    @staticmethod
    def get_letters(account):
        return account.letter_set.filter(email_account_id=account.id)

    @staticmethod
    @sync_to_async
    def get_range(account, length):
        letters = ConsumerUtils.get_letters(account)
        last = (
            min(letters, key=lambda ltr: ConsumerUtils.get_id(ltr)) if letters else None
        )

        start = ConsumerUtils.get_id(last) - 1 if last else length
        r = range(start, -1, -1)

        if start <= 0:
            return None

        return r


class EmailConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loop = asyncio.get_event_loop()
        self.tasks: set[asyncio.Task] = set()

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

    async def disconnect(self, code):
        print("Отменяю задачи...")
        for task in self.tasks:
            task.cancel()

    async def send_json(self, data: dict):
        try:
            encoded = json.dumps(data)
        except Exception as e:
            print(f"Произошла ошибка: {e} {data=}")
            raise
        else:
            await self.send(text_data=encoded)
            print(f"Отправлено: {encoded}")

    async def handle_action(self, data: dict):
        action_type = data.get("action")

        if action_type == "start_imap_read":
            id = data.get("account_id")
            await self.get_messages(account_id=id)

    async def connect_to_imap(self, account):
        self.send_json({"status": "connecting", "human_status": "Подключение..."})

        imap = await IMAPService(
            email=account.email,
            password=account.password,
            imap_server=account.imap_server,
            imap_port=account.imap_port,
        ).connect()

        if imap:
            self.send_json({"status": "connected", "human_status": "Подключено"})
            return imap
        else:
            self.send_json(
                {
                    "status": "error",
                    "human_status": "Ошибка",
                    "details": f"Не удалось подключиться к {account.email}",
                }
            )

    async def save(self, account):
        async def done():
            await imap.logout()
            await self.send_json(
                {
                    "status": "done",
                    "human_status": "Все письма загружены",
                    "total": total_emails,
                    "percent": 100,
                    "account_id": account.id,
                    "email": account.email,
                }
            )

        imap = await self.connect_to_imap(account)
        total_emails = await imap.get_total_count()

        await self.send_json({"status": "reading", "human_status": "Чтение..."})
        data_range = await ConsumerUtils.get_range(account, total_emails)

        if data_range:
            await self.send_json(
                {
                    "status": "importing",
                    "human_status": "Импортируем",
                    "data_range": list(data_range),
                }
            )
            for email_id in data_range:
                email_message = await imap.get_message(str(email_id))
                if email_message:
                    percentage = ConsumerUtils.percentage(
                        email_message.id, total_emails
                    )

                    letter = await Letter.objects.acreate(
                        email_account_id=account.id,
                        message_id=email_id,
                        subject=email_message.subject,
                        date_sent=email_message.date_sent,
                        date_received=email_message.date_received,
                        content=email_message.contents,
                        attachments=email_message.attachments,
                    )

                    send_data = {
                        "status": "load",
                        "human_status": "Загрузка...",
                        "total": total_emails,
                        "percent": percentage,
                        "email": model_to_dict(letter),
                    }
                    await self.send_json(send_data)

        await done()

    async def get_messages(self, account_id):
        await self.send_json(
            {
                "status": "started",
                "human_status": "Подготовка...",
            }
        )
        account = await ConsumerUtils.get_account(account_id)

        task = self.loop.create_task(self.save(account))
        self.tasks.add(task)

        await asyncio.gather(*self.tasks)
        await self.close()
