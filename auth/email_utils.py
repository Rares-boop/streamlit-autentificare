import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_confirmation_email(to_email, confirmation_token):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    confirm_url = f"{os.getenv('APP_URL')}/confirm?token={confirmation_token}"

    msg = MIMEMultipart()
    msg["From"] = smtp_email
    msg["To"] = to_email
    msg["Subject"] = "Confirm your account"

    body = f"Click here to confirm your account: {confirm_url}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, to_email, msg.as_string())
