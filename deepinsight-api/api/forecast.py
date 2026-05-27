"""
DeepInsight Starter Suite — Forecast API Routes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from api.auth import get_current_user
from models.schemas import (
    ForecastRequest,
    AnalysisResult,
    UserContext,
    JobResponse,
)
from services import forecasting_service, dataset_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/run/{dataset_id}",
    summary="Run forecasting",
)
async def run_forecast(
    dataset_id: str,
    request: ForecastRequest,
    mode: Optional[str] = "sync",
    user: UserContext = Depends(get_current_user),
):
    """
    Trigger forecasting on a dataset.
    
    Use mode=sync (default) for direct results, or mode=async to queue via Celery.
    """
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    if mode == "async":
        try:
            from tasks.ml_tasks import run_forecast_async
            task = run_forecast_async.delay(
                dataset_id=dataset_id,
                date_col=request.date_column,
                value_col=request.target_column,
                periods=request.forecast_horizon,
                model_type=request.model,
            )
            return JobResponse(
                job_id=task.id,
                status="accepted",
                message="Forecasting task has been queued."
            )
        except Exception as e:
            logger.error(f"Async forecast dispatch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Synchronous — run directly
        try:
            result = await forecasting_service.run_forecasting(
                dataset_id=dataset_id,
                date_col=request.date_column,
                value_col=request.target_column,
                periods=request.forecast_horizon,
                model_type=request.model,
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("Forecasting failed for dataset %s", dataset_id)
            raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")


@router.get(
    "/{dataset_id}",
    response_model=AnalysisResult,
    summary="Get forecast result",
)
async def get_forecast(
    dataset_id: str,
    user: UserContext = Depends(get_current_user),
):
    """Fetch previously computed forecast result."""
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    result = forecasting_service.get_cached_forecast(dataset_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No forecast found. Run it first via POST /api/forecast/run/{dataset_id}",
        )

    return {
        "analysis_type": result["analysis_type"],
        "results": result["results"],
        "charts": result.get("charts", []),
        "created_at": result["created_at"],
    }
