"""
DeepInsight Starter Suite — Pydantic v2 Schemas.

All request/response models used across API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, AliasChoices


# ── Enums ────────────────────────────────────────────────────


class AnalysisType(str, Enum):
    """Supported analysis types."""
    QUALITY = "quality"
    DESCRIPTIVE_STATS = "descriptive_stats"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    TREND = "trend"
    ANOMALY = "anomaly"
    FORECAST = "forecast"
    CLUSTERING = "clustering"
    BAR = "bar"
    PIE = "pie"


class ReportFormat(str, Enum):
    """Supported report output formats."""
    JSON = "json"
    PDF = "pdf"
    HTML = "html"


# ── Column Metadata ─────────────────────────────────────────


class ColumnMetadata(BaseModel):
    """Metadata for a single dataset column."""
    name: str
    dtype: str
    null_count: int = 0
    null_percentage: float = 0.0
    unique_count: int = 0
    sample_values: list[Any] = Field(default_factory=list)


# ── Dataset Schemas ──────────────────────────────────────────


class DatasetUploadResponse(BaseModel):
    """Response returned after a successful dataset upload."""
    id: str
    file_name: str
    file_type: str
    row_count: int
    column_count: int
    null_percentage: float
    quality_score: int
    columns: list[ColumnMetadata]
    created_at: datetime


class DatasetDetail(BaseModel):
    """Full dataset metadata detail."""
    id: str
    user_id: str
    file_name: str
    file_type: str
    storage_path: str
    row_count: int
    column_count: int
    null_percentage: float
    quality_score: int
    columns: list[ColumnMetadata]
    created_at: datetime


class DatasetListItem(BaseModel):
    """Summary item for dataset listing."""
    id: str
    file_name: str
    file_type: str
    row_count: int
    column_count: int
    quality_score: int
    created_at: datetime


# ── Analysis Schemas ─────────────────────────────────────────


class AnalysisRequest(BaseModel):
    """Request to run an analysis on a dataset."""
    analysis_types: list[AnalysisType] = Field(
        default=[AnalysisType.QUALITY],
        description="List of analysis types to run",
    )


class ForecastRequest(BaseModel):
    """Request to run forecasting."""
    model: str = Field(default="sarima", validation_alias=AliasChoices("model", "model_type"))
    target_column: Optional[str] = Field(default=None, validation_alias=AliasChoices("target_column", "value_column"))
    date_column: Optional[str] = None
    forecast_horizon: int = Field(default=30, validation_alias=AliasChoices("forecast_horizon", "periods"))

    @property
    def model_type(self) -> str:
        return self.model

    @property
    def value_column(self) -> Optional[str]:
        return self.target_column

    @property
    def periods(self) -> int:
        return self.forecast_horizon


class AnomalyRequest(BaseModel):
    """Request to run anomaly detection."""
    method: str = "iqr"
    threshold: float = 1.5


class ChartData(BaseModel):
    """Plotly chart in JSON format."""
    chart_type: str
    title: str
    data: dict[str, Any]


class AnalysisResult(BaseModel):
    """Result of a single analysis run."""
    analysis_type: str
    results: dict[str, Any] = Field(default_factory=dict)
    charts: list[ChartData] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResponse(BaseModel):
    """Full response containing all analysis results for a dataset."""
    dataset_id: str
    analyses: list[AnalysisResult]


# ── Chat Schemas ─────────────────────────────────────────────


class ChatSessionCreate(BaseModel):
    """Request to create a new chat session."""
    dataset_id: str
    title: Optional[str] = None


class ChatSessionResponse(BaseModel):
    """Response after creating a chat session."""
    id: str
    dataset_id: str
    user_id: str
    title: str
    created_at: datetime


class ChatMessageRequest(BaseModel):
    """User message sent to the chat."""
    message: str


class ChatMessageResponse(BaseModel):
    """AI response to a chat message."""
    id: str
    session_id: str
    role: str
    content: str
    follow_up_questions: list[str] = Field(default_factory=list)
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """Full chat history for a session."""
    session_id: str
    dataset_id: str
    title: str
    messages: list[ChatMessageResponse]


# ── Report Schemas ───────────────────────────────────────────


class ReportRequest(BaseModel):
    """Request to generate a report."""
    dataset_id: str
    format: ReportFormat = ReportFormat.JSON
    analysis_types: Optional[list[AnalysisType]] = None


class ReportResponse(BaseModel):
    """Response with the generated report."""
    dataset_id: str
    format: str
    content: Optional[dict[str, Any]] = None
    download_url: Optional[str] = None
    html_content: Optional[str] = None


# ── Auth Schemas ─────────────────────────────────────────────


class UserContext(BaseModel):
    """Authenticated user context extracted from JWT."""
    user_id: str
    email: Optional[str] = None
