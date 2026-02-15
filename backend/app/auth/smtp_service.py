import os
import smtplib
from email.mime.text import MIMEText


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError("No environment variable")
    return value


SMTP_HOST = require_env("SMTP_HOST")
SMTP_PORT = 587
SMTP_EMAIL = require_env("SMTP_EMAIL")
SMTP_PASSWORD = require_env("SMTP_PASSWORD")


def send_email(to_email: str, subject: str, body: str):
    if not SMTP_HOST or not SMTP_EMAIL or not SMTP_PASSWORD:
        raise Exception("SMTP is not configured correctly in .env")

    msg = MIMEText(body)
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
