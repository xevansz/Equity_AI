from email.mime.text import MIMEText

import aiosmtplib

from app.config import settings

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_EMAIL = settings.SMTP_EMAIL
SMTP_PASSWORD = settings.SMTP_PASSWORD


async def send_email(to_email: str, subject: str, body: str):
    if not SMTP_HOST or not SMTP_EMAIL or not SMTP_PASSWORD:
        raise Exception("SMTP is not configured correctly in .env")

    msg = MIMEText(body)
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_EMAIL,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
