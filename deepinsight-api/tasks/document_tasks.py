"""
DeepInsight Starter Suite — Document Tasks.

Celery tasks for background document processing.
"""

import logging
import asyncio

from worker import celery_app
from services.document_service import process_document_async

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.document_tasks.process_document")
def process_document_task(
    self,
    user_id: str,
    filename: str,
    file_bytes: bytes,
    mime_type: str,
    org_id: str = None
):
    """Background task to extract and analyze documents."""
    logger.info(f"Starting document processing task for {filename}")
    self.update_state(state="PROGRESS", meta={"message": "Extracting text..."})
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        process_document_async(user_id, filename, file_bytes, mime_type, org_id)
    )
    
    return result
