"""
DeepInsight Starter Suite — Analysis API Routes.

Endpoints for running and retrieving data analyses.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisResult,
    UserContext,
)
from services import analysis_service, dataset_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/run/{dataset_id}",
    response_model=AnalysisResponse,
    summary="Run analysis",
    description="Run one or more analysis types on a dataset.",
)
async def run_analysis(
    dataset_id: str,
    request: AnalysisRequest,
    user: UserContext = Depends(get_current_user),
):
    """Trigger analysis pipeline on a dataset."""
    # Verify dataset exists and belongs to user
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    try:
        results = await analysis_service.run_analysis(
            dataset_id=dataset_id,
            analysis_types=request.analysis_types,
        )
        return {"dataset_id": dataset_id, "analyses": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Analysis failed for dataset %s", dataset_id)
        # In development, return the actual error message for easier debugging
        detail = f"Analysis failed: {str(e)}"
        raise HTTPException(status_code=500, detail=detail)


@router.get(
    "/{dataset_id}/{analysis_type}",
    response_model=AnalysisResult,
    summary="Get analysis result",
    description="Retrieve a cached analysis result by type.",
)
async def get_analysis(
    dataset_id: str,
    analysis_type: str,
    user: UserContext = Depends(get_current_user),
):
    """Fetch a previously computed analysis result."""
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    result = analysis_service.get_cached_analysis(dataset_id, analysis_type)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No {analysis_type} analysis found. Run it first via POST /api/analysis/run/{dataset_id}",
        )

    return {
        "analysis_type": result["analysis_type"],
        "results": result["results"],
        "charts": result.get("charts", []),
        "created_at": result["created_at"],
    }