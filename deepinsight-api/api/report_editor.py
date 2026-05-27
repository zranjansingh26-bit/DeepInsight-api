"""
DeepInsight Starter Suite — Report Editor API.

Endpoints for AI Report Co-Creation and version history.
"""

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth import get_current_user
from models.schemas import UserContext
from services import report_editor_service

logger = logging.getLogger(__name__)
router = APIRouter()

class CreateReportRequest(BaseModel):
    dataset_id: str
    title: str

class ReviseReportRequest(BaseModel):
    instruction: str


@router.post("/create")
async def create_report(
    request: CreateReportRequest,
    user: UserContext = Depends(get_current_user)
) -> dict[str, Any]:
    """Create an initial AI-generated report."""
    try:
        report = await report_editor_service.create_initial_report(
            user.user_id, request.dataset_id, request.title
        )
        return {"status": "success", "report": report}
    except Exception as e:
        logger.error(f"Failed to create report: {e}")
        raise HTTPException(status_code=500, detail="Failed to create report")


@router.post("/{report_id}/revise")
async def revise_report(
    report_id: str,
    request: ReviseReportRequest,
    user: UserContext = Depends(get_current_user)
) -> dict[str, Any]:
    """Apply an AI instruction to revise a report (e.g., 'make it more professional')."""
    try:
        report = await report_editor_service.revise_report(
            user.user_id, report_id, request.instruction
        )
        return {"status": "success", "report": report}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to revise report: {e}")
        raise HTTPException(status_code=500, detail="Failed to revise report")


@router.get("/{report_id}/versions")
async def get_report_versions(
    report_id: str,
    user: UserContext = Depends(get_current_user)
) -> list[dict[str, Any]]:
    """Retrieve version history for a report."""
    try:
        return report_editor_service.get_report_history(report_id)
    except Exception as e:
        logger.error(f"Failed to fetch report history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")
