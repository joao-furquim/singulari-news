from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    async def send_password_reset(self, recipient_email: str, reset_token: str) -> None:
        pass
