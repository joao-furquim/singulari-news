"""Email delivery service backed by Resend.

Sends transactional emails such as password-reset links. When
``RESEND_API_KEY`` is empty the delivery is skipped and the reset URL
is logged at WARNING level so development workflows remain functional
without a live API key.
"""

import logging

import resend
from app.core.config import settings
from app.interfaces.email_service import IEmailService

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


class EmailService(IEmailService):
    """Resend-backed implementation of the email delivery service."""

    async def send_password_reset(self, recipient_email: str, reset_token: str) -> None:
        """Send a password-reset email with a one-time token link.

        Constructs an HTML email containing a clickable reset link valid for
        ``JWT_RESET_TOKEN_EXPIRE_MINUTES`` minutes. On delivery failure the
        exception is caught and the URL is logged so developers can use it
        directly without a live email provider.

        :param recipient_email: Destination email address.
        :param reset_token: Signed JWT reset token embedded in the reset URL.
        """
        reset_url = f"https://singulari.com.br/reset-password?token={reset_token}"
        try:
            resend.Emails.send(
                {
                    "from": settings.EMAIL_FROM,
                    "to": recipient_email,
                    "subject": "Password Reset — Singulari News",
                    "html": (
                        "<p>You requested a password reset.</p>"
                        f'<p><a href="{reset_url}">'
                        "Click here to reset your password</a></p>"
                        "<p>This link expires in "
                        f"{settings.JWT_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>"
                        "<p>If you did not request a password reset, "
                        "please ignore this email.</p>"
                    ),
                }
            )
        except Exception as error:
            logger.warning(
                f"Failed to send email via Resend (fallback: token logged): {error}\n"
                f"  → reset_url={reset_url}"
            )
