"""
DeepInsight Starter Suite — Forecasting Service.

Orchestrates time series forecasting execution and caching.
"""

import logging
from typing import Any

from db import repository
from engines.forecaster import run_forecast
from engines.chart_generator import generate_forecast_chart
from models.schemas import AnalysisType
from services.dataset_service import get_dataset, get_dataframe

logger = logging.getLogger(__name__)


async def run_forecasting(
    dataset_id: str,
    date_col: str | None = None,
    value_col: str | None = None,
    periods: int = 30,
    model_type: str = "sarima",
) -> dict[str, Any]:
    """
    Run forecast on a dataset and cache the result.
    """
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found.")

    df = get_dataframe(dataset)

    logger.info("Running forecast (%s) on dataset %s", model_type, dataset_id)

    # Normalize model_type to match internal identifiers (e.g., "moving_average", "exponential_smoothing", "sarima", "prophet")
    normalized_model = model_type.strip().lower().replace(" ", "_")
    # Accept common aliases
    alias_map = {
        "ma": "moving_average",
        "movingaverage": "moving_average",
        "expsmooth": "exponential_smoothing",
        "exp_smoothing": "exponential_smoothing",
        "sarima": "sarima",
        "prophet": "prophet",
    }
    model_key = alias_map.get(normalized_model, normalized_model)
    # Validate model_key
    if model_key not in {"moving_average", "exponential_smoothing", "sarima", "prophet"}:
        raise ValueError(f"Unsupported model type: {model_type}")
    result = run_forecast(df, date_col=date_col, value_col=value_col, periods=periods, model_type=model_key)
    
    if "error" in result:
        raise ValueError(result["error"])

    charts = []
    if "forecast_values" in result:
        model_name_title = {
            "sarima": "SARIMA",
            "exponential_smoothing": "Exponential Smoothing",
            "moving_average": "Moving Average",
            "prophet": "Prophet"
        }.get(model_key, model_key.upper().replace('_', ' '))
        
        chart = generate_forecast_chart(
            historical_dates=result["historical_dates"],
            historical_values=result["historical_values"],
            forecast_dates=result["forecast_dates"],
            forecast_values=result["forecast_values"],
            conf_lower=result["confidence_lower"],
            conf_upper=result["confidence_upper"],
            value_col=result.get("value_column", "value"),
            title=f"{model_name_title} Forecast — {result.get('value_column', 'value')}"
        )
        charts.append({
            "chart_type": "line",
            "title": f"{model_name_title} Forecast",
            "data": chart,
        })

    # Save to DB
    saved = repository.save_analysis(
        dataset_id=dataset_id,
        analysis_type=AnalysisType.FORECAST.value,
        results=result,
        charts=charts,
    )

    return {
        "analysis_type": AnalysisType.FORECAST.value,
        "results": result,
        "charts": charts,
        "created_at": saved["created_at"],
    }


def get_cached_forecast(dataset_id: str) -> dict[str, Any] | None:
    """Fetch previously computed forecast."""
    return repository.get_analysis(dataset_id, AnalysisType.FORECAST.value)
