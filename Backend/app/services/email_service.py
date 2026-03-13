import smtplib
from email.mime.text import MIMEText

from app.core.config import settings


def send_reset_email(to_email: str, token: str) -> None:
    body = (
        f"You requested a password reset.\n\n"
        f"Use this token to reset your password: {token}\n\n"
        f"This token expires in {settings.reset_token_ttl_seconds} seconds."
    )
    msg = MIMEText(body)
    msg["Subject"] = "Password Reset"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.send_message(msg)
