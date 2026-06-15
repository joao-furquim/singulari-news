import logging

import resend

from app.core.config import settings
from app.interfaces.email_service import IEmailService

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


class EmailService(IEmailService):
    async def send_password_reset(self, recipient_email: str, reset_token: str) -> None:
        reset_url = f"https://singulari.com.br/reset-password?token={reset_token}"
        try:
            resend.Emails.send({
                "from": settings.EMAIL_FROM,
                "to": recipient_email,
                "subject": "Password Reset — Singulari News",
                "html": f"""
                    <p>You requested a password reset.</p>
                    <p><a href="{reset_url}">Click here to reset your password</a></p>
                    <p>This link expires in {settings.JWT_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
                    <p>If you did not request a password reset, please ignore this email.</p>
                """,
            })
        except Exception as error:
            logger.warning(
                f"Failed to send email via Resend (fallback: token logged): {error}\n"
                f"  → reset_url={reset_url}"
            )
