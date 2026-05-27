"""
DeepInsight Starter Suite — Reports API Routes.

Endpoint for generating reports in various formats.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from api.auth import get_current_user
from models.schemas import (
    ReportRequest, ReportResponse, UserContext, JobResponse,
    ExecutiveSummaryResponse,
)
from services import report_service, dataset_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    summary="Generate report",
    description="Generate a JSON, HTML, PDF, or PPTX report for a dataset.",
)
async def generate_report(
    request: ReportRequest,
    mode: Optional[str] = "sync",
    user: UserContext = Depends(get_current_user),
):
    """
    Generate a comprehensive report from analysis results.
    
    Use mode=sync (default) for direct results, or mode=async to queue via Celery.
    """
    # Verify dataset ownership
    dataset = dataset_service.get_dataset(request.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    if mode == "async":
        try:
            from tasks.report_tasks import generate_report_async
            analysis_type_strs = (
                [a.value for a in request.analysis_types]
                if request.analysis_types
                else None
            )
            task = generate_report_async.delay(
                dataset_id=request.dataset_id,
                report_format=request.format.value,
                analysis_types=analysis_type_strs,
            )
            return JobResponse(
                job_id=task.id,
                status="accepted",
                message="Report generation has been queued."
            )
        except Exception as e:
            logger.error(f"Async report dispatch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Synchronous — run directly
        try:
            analysis_type_strs = (
                [a.value for a in request.analysis_types]
                if request.analysis_types
                else None
            )
            result = await report_service.generate_report(
                dataset_id=request.dataset_id,
                report_format=request.format,
                analysis_types=analysis_type_strs,
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("Report generation failed")
            raise HTTPException(status_code=500, detail="Report generation failed.")


@router.post(
    "/{dataset_id}/executive-summary",
    response_model=ExecutiveSummaryResponse,
    summary="Generate executive summary",
    description="Generate a structured AI executive summary for a dataset.",
)
async def get_executive_summary(
    dataset_id: str,
    user: UserContext = Depends(get_current_user),
):
    """Generate a standalone AI-powered executive summary for the dataset."""
    from datetime import datetime, timezone
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    try:
        from db import repository
        analyses = repository.get_all_analyses(dataset_id)
        narrative, sections = await report_service._generate_executive_narrative(dataset, analyses)
        return ExecutiveSummaryResponse(
            dataset_id=dataset_id,
            dataset_name=dataset["file_name"],
            generated_at=datetime.now(timezone.utc),
            overview=sections.get("overview", ""),
            performance_insights=sections.get("performance_insights", ""),
            forecast_insights=sections.get("forecast_insights", ""),
            anomaly_insights=sections.get("anomaly_insights", ""),
            model_performance=sections.get("model_performance", ""),
            recommendations=sections.get("recommendations", ""),
            conclusion=sections.get("conclusion", ""),
            raw_narrative=narrative,
        )
    except Exception as e:
        logger.exception("Executive summary generation failed")
        raise HTTPException(status_code=500, detail=str(e))