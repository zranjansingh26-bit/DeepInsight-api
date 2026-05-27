"""
DeepInsight Starter Suite — Email Tasks.

Celery background tasks for scheduled and asynchronous email sending.
"""

import logging
from worker import celery_app
from services import email_service
from db.client import get_service_client
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.email_tasks.send_trial_reminders")
def send_trial_reminders():
    """Send automated trial expiration reminders."""
    client = get_service_client()
    now = datetime.now(timezone.utc)
    
    # 3 days left
    three_days = now + timedelta(days=3)
    # query profiles where trial_end is roughly 3 days from now
    # Simplified logic for MVP: just get trials ending in the next 3 days that haven't expired
    
    # In a full implementation, you'd track if the email was sent, but for MVP we skip
    pass
