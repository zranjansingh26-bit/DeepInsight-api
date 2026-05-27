"""
DeepInsight Starter Suite — Celery Worker.

Configuration and initialization for Celery background tasks.
"""

import os
from celery import Celery

# Default to local redis if not in env
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "deepinsight_tasks",
    broker=redis_url,
    backend=redis_url,
    include=["tasks.ml_tasks", "tasks.report_tasks", "tasks.dataset_tasks", "tasks.document_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # 1 hour max for long ML tasks
    
    # Retry configs
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Task routing
    task_routes={
        "tasks.ml_tasks.*": {"queue": "ml_queue"},
        "tasks.report_tasks.*": {"queue": "report_queue"},
        "tasks.dataset_tasks.*": {"queue": "data_queue"},
        "tasks.document_tasks.*": {"queue": "data_queue"},
    }
)

# Scheduled Tasks (Celery Beat)
from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    'daily-scheduled-analysis': {
        'task': 'tasks.ml_tasks.run_scheduled_analyses',
        'schedule': crontab(hour=2, minute=0), # Run daily at 2:00 AM UTC
    },
}

if __name__ == "__main__":
    celery_app.start()
