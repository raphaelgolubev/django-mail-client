from dataclasses import dataclass
from email import message_from_bytes, policy
from email.header import decode_header
from email.message import EmailMessage
from email.parser import BytesParser

import aioimaplib

import core.utils.format_string as utils


class IMAPService:
    @dataclass
    class Message:
        id: int
        subject: str
        date_sent: str
        date_received: str
        contents: str
        attachments: list[str]

        def to_dict(self):
            return {
                "id": self.id,
                "subject": self.subject,
                "date_sent": self.date_sent,
                "date_received": self.date_received,
                "contents": self.contents,
                "attachments": self.attachments,
            }

    def __init__(self, email: str, password: str, imap_server: str, imap_port: int):
        self.email = email
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port

    async def __connect_imap(self) -> aioimaplib.IMAP4_SSL | None:
        """Выполняет соединение с IMAP сервером и возвращает объект `IMAP4_SSL`"""
        imap_client = aioimaplib.IMAP4_SSL(host=self.imap_server, port=self.imap_port)

        await imap_client.wait_hello_from_server()

        response = await imap_client.login(user=self.email, password=self.password)

        if response.result == "OK":
            print(f"{self.email} authenticated")
            return imap_client
        else:
            raise Exception(
                f"Login failed: {self.email=} {self.password=} {response.result}"
            )

    def __decode_mime_string(self, encoded_str):
        """Пытается декодировать заголовок письма"""
        if encoded_str:
            decoded_bytes, charset = decode_header(encoded_str)[0]
            if isinstance(decoded_bytes, bytes):
                return decoded_bytes.decode(charset or "utf-8")
            return utils.reduce_spaces(decoded_bytes)
        return encoded_str

    def __get_plain_text(self, message):
        """Пытается получить текст из письма"""
        msg = BytesParser(policy=policy.default).parsebytes(message)

        if msg.is_multipart():
            for part in msg.iter_parts():
                # Проверяем, является ли часть текстовой
                if part.get_content_type() == "text/plain":
                    return part.get_content()

        return None

    def __get_content(self, message, raw_email):
        """Получает содержание письма"""
        text = self.__get_plain_text(raw_email)

        if text:
            truncated = utils.truncate_text(text, max_length=100)
            return utils.reduce_spaces(truncated)

        return "Нет содержания"

    def __get_attachments(self, message):
        """Получает список вложений письма"""
        attachments = []
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue
            fileName = part.get_filename()
            if fileName:
                attachments.append(fileName)
        return attachments

    async def get_total_count(self, mailbox: str = "INBOX") -> int:
        """Получает общее количество писем в папке"""
        _, data = await self.client.select(mailbox=mailbox)

        data_list = [d.decode() for d in data]
        count_str = list(filter(lambda x: x.endswith("EXISTS"), data_list))[0]
        count = count_str.split(" ")[0]

        return int(count)

    async def get_message(self, id: str):
        """Формирует и возвращает объект `Message` из "сырого" письма"""
        _, fetched_data = await self.client.fetch(id, "(RFC822)")
        raw_email = None

        for data in fetched_data:
            if isinstance(data, bytearray):
                raw_email = data

        if raw_email:
            email_message = message_from_bytes(raw_email, _class=EmailMessage)

            # Получаем необходимые данные
            subject = self.__decode_mime_string(email_message["subject"])
            date_sent = utils.extract_datetime(email_message["date"])
            date_received = utils.extract_datetime(email_message["received"])
            content = self.__get_content(email_message, raw_email)
            attachments = self.__get_attachments(email_message)

            return IMAPService.Message(
                id, subject, date_sent, date_received, content, attachments
            )

    async def connect(self):
        self.client = await self.__connect_imap()
        return self

    async def logout(self):
        print("Closing IMAP connection")
        await self.client.logout()
