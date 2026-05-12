"""
DeepInsight Starter Suite — Reports API Routes.

Endpoint for generating reports in various formats.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from api.auth import get_current_user
from models.schemas import ReportRequest, ReportResponse, UserContext
from services import report_service, dataset_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/generate",
    response_model=ReportResponse,
    summary="Generate report",
    description="Generate a JSON, HTML, or PDF report for a dataset.",
)
async def generate_report(
    request: ReportRequest,
    user: UserContext = Depends(get_current_user),
):
    """Generate a comprehensive report from analysis results."""
    # Verify dataset ownership
    dataset = dataset_service.get_dataset(request.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

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