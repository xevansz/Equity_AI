import smtplib
from email.mime.text import MIMEText
from app.config import settings


SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_EMAIL = settings.SMTP_EMAIL
SMTP_PASSWORD = settings.SMTP_PASSWORD


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
