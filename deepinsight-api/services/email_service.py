"""
DeepInsight Starter Suite — Email Service.

Sends automated email notifications for system events (e.g., job completion, anomaly detection).
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import get_settings
import resend

logger = logging.getLogger(__name__)

settings = get_settings()
if settings.resend_api_key:
    resend.api_key = settings.resend_api_key

def send_notification_email(to_email: str, subject: str, html_content: str) -> None:
    """Send an email notification using Resend (preferred) or SMTP."""
    
    if settings.resend_api_key:
        try:
            r = resend.Emails.send({
                "from": f"{settings.app_name} <noreply@deepinsights.ai>",
                "to": to_email,
                "subject": subject,
                "html": html_content
            })
            logger.info(f"Successfully sent notification email to {to_email} via Resend")
            return
        except Exception as e:
            logger.error(f"Failed to send email via Resend to {to_email}: {e}")
            # Fall through to SMTP if possible
            
    user = settings.gmail_user
    password = settings.gmail_app_password
    
    if not user or not password:
        logger.warning(f"Email credentials not configured. Skipping email to {to_email}.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.app_name} <{user}>"
        msg["To"] = to_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        # Connect to SMTP server (using Gmail as default for starter suite)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(user, password)
        server.sendmail(user, to_email, msg.as_string())
        server.quit()
        logger.info(f"Successfully sent notification email to {to_email} via SMTP")
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        # We don't raise the error so it doesn't break the background jobs

def send_welcome_email(to: str, name: str) -> bool:
    html = f"<h1>Welcome to DeepInsights, {name}!</h1><p>Your 14-day Pro trial has started.</p>"
    send_notification_email(to, "Welcome to DeepInsights", html)
    return True

def send_trial_reminder(to: str, days_left: int) -> bool:
    html = f"<h1>Trial Ending Soon</h1><p>You have {days_left} days left in your trial.</p>"
    send_notification_email(to, "Your trial is ending soon", html)
    return True

def send_report_notification(to: str, report_name: str) -> bool:
    html = f"<h1>Report Ready</h1><p>Your report '{report_name}' is ready to view.</p>"
    send_notification_email(to, "Your report is ready", html)
    return True
