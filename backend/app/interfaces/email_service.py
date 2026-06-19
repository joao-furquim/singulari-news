"""Interface for transactional email delivery.

Defines the contract for sending system-generated emails such as
password-reset messages. Implementations may use an external provider
(e.g., Resend) or fall back to logging when no API key is configured.
"""

from abc import ABC, abstractmethod


class IEmailService(ABC):
    """Abstract base class defining the email delivery contract."""

    @abstractmethod
    async def send_password_reset(self, recipient_email: str, reset_token: str) -> None:
        """Send a password-reset email containing a one-time token link.

        :param recipient_email: Destination email address.
        :param reset_token: Signed JWT reset token to embed in the reset URL.
        """
