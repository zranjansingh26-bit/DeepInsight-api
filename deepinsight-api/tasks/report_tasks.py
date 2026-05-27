"""
DeepInsight Starter Suite — Celery Report Tasks.
"""

import asyncio
from celery import shared_task
from services import report_service

@shared_task(bind=True)
def generate_report_async(self, dataset_id: str, report_format: str, analysis_types: list[str]):
    """Generate reports in the background."""
    self.update_state(state="PROGRESS", meta={"status": "Generating report..."})
    
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    try:
        # report_service expects an Enum, but we passed string from API to Celery
        from models.schemas import ReportFormat
        fmt_enum = ReportFormat(report_format)
        
        result = loop.run_until_complete(report_service.generate_report(
            dataset_id=dataset_id,
            report_format=fmt_enum,
            analysis_types=analysis_types
        ))
        return result
    except Exception as e:
        raise Exception(f"Report generation failed: {str(e)}")
