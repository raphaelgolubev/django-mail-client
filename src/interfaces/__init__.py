from abc import ABC, abstractmethod


class IEmailAccount(ABC):
    @abstractmethod
    def __init__(self, email: str, password: str, imap_server: str, port: int):
        raise NotImplementedError()
    
    @abstractmethod
    async def read_mail_box(self):
        raise NotImplementedError()