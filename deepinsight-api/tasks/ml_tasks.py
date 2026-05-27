"""
DeepInsight Starter Suite — Celery ML Tasks.
"""

import asyncio
from celery import shared_task
from services import ml_service, forecasting_service

@shared_task(bind=True)
def run_ml_task_async(self, dataset_id: str, user_id: str, task_type: str, model_name: str, target_col: str, k: int):
    """Run an ML task in the background."""
    self.update_state(state="PROGRESS", meta={"status": "Starting ML training..."})
    
    # We must run the async service method in a synchronous Celery task
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        result = loop.run_until_complete(ml_service.run_ml_task(
            dataset_id=dataset_id,
            user_id=user_id,
            task_type=task_type,
            model_name=model_name,
            target_col=target_col,
            k=k
        ))
        return result
    except Exception as e:
        raise Exception(f"ML task failed: {str(e)}")


@shared_task(bind=True)
def run_forecast_async(self, dataset_id: str, date_col: str, value_col: str, periods: int, model_type: str):
    """Run time-series forecasting in the background."""
    self.update_state(state="PROGRESS", meta={"status": "Starting forecasting..."})
    
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        result = loop.run_until_complete(forecasting_service.run_forecasting(
            dataset_id=dataset_id,
            date_col=date_col,
            value_col=value_col,
            periods=periods,
            model_type=model_type
        ))
        return result
    except Exception as e:
        raise Exception(f"Forecasting task failed: {str(e)}")

@shared_task(bind=True)
def run_scheduled_analyses(self):
    """Run all scheduled recurring ML and anomaly tasks for premium users."""
    # In a real app, you would query the DB for active scheduled jobs
    # For MVP, this is a placeholder task triggered by Celery Beat
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Executing daily scheduled analyses for all workspaces...")
    return "Scheduled analyses completed successfully."
