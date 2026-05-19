"""
DeepInsight Starter Suite — Anomaly API Routes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from models.schemas import (
    AnomalyRequest,
    AnalysisResult,
    UserContext,
)
from services import anomaly_service, dataset_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/run/{dataset_id}",
    response_model=AnalysisResult,
    summary="Run anomaly detection",
)
async def run_anomaly(
    dataset_id: str,
    request: AnomalyRequest,
    user: UserContext = Depends(get_current_user),
):
    """Trigger anomaly detection on a dataset."""
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    try:
        result = await anomaly_service.run_anomaly_detection(
            dataset_id=dataset_id,
            method=request.method,
            threshold=request.threshold,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Anomaly detection failed for dataset %s", dataset_id)
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@router.get(
    "/{dataset_id}",
    response_model=AnalysisResult,
    summary="Get anomaly detection result",
)
async def get_anomaly(
    dataset_id: str,
    user: UserContext = Depends(get_current_user),
):
    """Fetch previously computed anomaly result."""
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    result = anomaly_service.get_cached_anomaly(dataset_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No anomaly analysis found. Run it first via POST /api/anomaly/run/{dataset_id}",
        )

    return {
        "analysis_type": result["analysis_type"],
        "results": result["results"],
        "charts": result.get("charts", []),
        "created_at": result["created_at"],
    }
