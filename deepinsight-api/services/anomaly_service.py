"""
DeepInsight Starter Suite — Anomaly Service.

Orchestrates anomaly detection execution and caching.
"""

import logging
from typing import Any

from db import repository
from engines.anomaly_detector import detect_anomalies
from engines.chart_generator import generate_anomaly_chart
from models.schemas import AnalysisType
from services.dataset_service import get_dataset, get_dataframe

logger = logging.getLogger(__name__)


async def run_anomaly_detection(
    dataset_id: str,
    method: str = "iqr",
    threshold: float = 1.5,
) -> dict[str, Any]:
    """
    Run anomaly detection on a dataset and cache the result.
    """
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found.")

    df = get_dataframe(dataset)

    logger.info("Running anomaly detection (%s) on dataset %s", method, dataset_id)

    result = detect_anomalies(df, method=method, threshold=threshold)
    
    if "error" in result:
        raise ValueError(result["error"])

    charts = []
    anomalies = result.get("anomalies_by_column", {})
    # Generate scatter plot for top 3 columns with most anomalies
    sorted_cols = sorted(anomalies.keys(), key=lambda k: anomalies[k]["count"], reverse=True)
    
    for col in sorted_cols[:3]:
        if anomalies[col]["count"] > 0:
            chart = generate_anomaly_chart(df, col, anomalies[col]["indices"])
            charts.append({
                "chart_type": "scatter",
                "title": f"Anomalies — {col}",
                "data": chart,
            })

    # Save to DB
    saved = repository.save_analysis(
        dataset_id=dataset_id,
        analysis_type=AnalysisType.ANOMALY.value,
        results=result,
        charts=charts,
    )

    return {
        "analysis_type": AnalysisType.ANOMALY.value,
        "results": result,
        "charts": charts,
        "created_at": saved["created_at"],
    }


def get_cached_anomaly(dataset_id: str) -> dict[str, Any] | None:
    """Fetch previously computed anomalies."""
    return repository.get_analysis(dataset_id, AnalysisType.ANOMALY.value)
