"""
DeepInsight Starter Suite — ML Pydantic Schemas.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

class MLTrainRequest(BaseModel):
    dataset_id: str
    target_column: Optional[str] = None

class MLModelSummary(BaseModel):
    id: str
    model_name: str
    problem_type: str
    accuracy_score: Optional[float]
    created_at: datetime

class MLTrainingResult(BaseModel):
    model_id: str
    model_name: str
    problem_type: str
    metrics: dict[str, Any]
    comparison: list[dict[str, Any]]
    charts: list[dict[str, Any]] = Field(default_factory=list)
    interpretation: Optional[str] = None

class PredictionRequest(BaseModel):
    model_id: str
    input_data: dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: Any
    latency_ms: float
    model_name: str

class TrainingHistoryItem(BaseModel):
    id: str
    dataset_id: Optional[str]
    run_details: list[dict[str, Any]]
    best_model_id: Optional[str]
    status: str
    created_at: datetime
