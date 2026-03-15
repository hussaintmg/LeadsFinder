import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def send_outreach_email(to_email, subject, body):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_pass:
        logger.error("SMTP credentials missing in .env. Remember to use a Google App Password (16 characters) for SMTP_PASSWORD.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_pass)
            server.send_message(msg)
            
        return True
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False
