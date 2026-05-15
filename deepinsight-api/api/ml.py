"""
DeepInsight Starter Suite — ML API Router.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional

from api.auth import get_current_user
from models.schemas import UserContext
from models.ml_schemas import (
    MLTrainRequest, MLTrainingResult, 
    MLModelSummary, PredictionRequest, 
    PredictionResponse, TrainingHistoryItem
)
from services import ml_service
from db import repository

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Machine Learning"])

@router.get("/available-models")
async def get_available_models(problem_type: str):
    """List all supported ML models for a given problem type."""
    return ml_service.list_available_models(problem_type)

@router.post("/train-specific")
async def train_specific(
    dataset_id: str,
    model_name: str,
    target_column: Optional[str] = None,
    user: UserContext = Depends(get_current_user)
):
    """Train a specific model chosen by the user."""
    try:
        result = await ml_service.train_selected_model(
            dataset_id=dataset_id,
            user_id=user.user_id,
            model_name=model_name,
            target_col=target_column
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparison/{dataset_id}")
async def get_comparison(
    dataset_id: str,
    user: UserContext = Depends(get_current_user)
):
    """Get comparison leaderboard for a specific dataset."""
    return await ml_service.get_dataset_comparison(user.user_id, dataset_id)

@router.get("/suggest-target/{dataset_id}")
async def suggest_target(
    dataset_id: str,
    user: UserContext = Depends(get_current_user)
):
    """Suggest an optimal target column and problem type."""
    try:
        return await ml_service.suggest_target(dataset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-task")
async def run_task(
    dataset_id: str,
    task_type: str,
    model_name: Optional[str] = None,
    target_column: Optional[str] = None,
    k: Optional[int] = 3,
    user: UserContext = Depends(get_current_user)
):
    """Run a specific ML task (regression, classification, clustering)."""
    try:
        result = await ml_service.run_ml_task(
            dataset_id=dataset_id,
            user_id=user.user_id,
            task_type=task_type,
            model_name=model_name,
            target_col=target_column,
            k=k
        )
        return result
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
