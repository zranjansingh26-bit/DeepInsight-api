"""
DeepInsight Starter Suite — Analysis Service.

Dispatches analysis requests to the appropriate engine and
caches results in the database.
"""

import logging
from typing import Any

import pandas as pd

from db import repository
from engines.quality_checker import check_quality
from engines.stats_profiler import (
    compute_descriptive_stats,
    compute_correlation,
    compute_trend_analysis,
)
from engines.chart_generator import (
    generate_distribution_charts,
    generate_correlation_heatmap,
    generate_box_plots,
    generate_trend_chart,
    generate_anomaly_chart,
    generate_forecast_chart,
    generate_cluster_chart,
    generate_bar_chart,
    generate_pie_chart,
)
from engines.forecaster import run_forecast
from engines.clusterer import run_clustering
from engines.anomaly_detector import detect_anomalies
from models.schemas import AnalysisType
from services.dataset_service import get_dataset, get_dataframe

logger = logging.getLogger(__name__)


async def run_analysis(
    dataset_id: str,
    analysis_types: list[AnalysisType],
) -> list[dict[str, Any]]:
    """
    Run one or more analyses on a dataset.

    Dispatches to the correct engine, generates charts,
    and saves results to the database.
    """
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found.")

    df = get_dataframe(dataset)
    results = []

    for analysis_type in analysis_types:
        logger.info("Running %s on dataset %s", analysis_type.value, dataset_id)

        result = _dispatch_analysis(df, analysis_type)
        charts = _generate_charts(df, analysis_type, result)

        # Generate summary and insights if missing
        if "summary" not in result or "insights" not in result:
            summary, insights = _generate_summary_and_insights(df, analysis_type, result)
            result["summary"] = summary
            result["insights"] = insights

        # Save to DB
        chart_dicts = [
            {"chart_type": c["chart_type"], "title": c["title"], "data": c["data"]}
            for c in charts
        ]
        saved = repository.save_analysis(
            dataset_id=dataset_id,
            analysis_type=analysis_type.value,
            results=result,
            charts=chart_dicts,
        )

        results.append({
            "analysis_type": analysis_type.value,
            "results": result,
            "charts": chart_dicts,
            "created_at": saved["created_at"],
        })

    return results


def get_cached_analysis(
    dataset_id: str, analysis_type: str
) -> dict[str, Any] | None:
    """Fetch a previously computed analysis from the database."""
    return repository.get_analysis(dataset_id, analysis_type)


def get_all_dataset_analyses(dataset_id: str) -> list[dict]:
    """Fetch all analyses for a dataset."""
    return repository.get_all_analyses(dataset_id)


def _dispatch_analysis(
    df: pd.DataFrame, analysis_type: AnalysisType
) -> dict[str, Any]:
    """Route to the correct analysis engine."""
    match analysis_type:
        case AnalysisType.QUALITY:
            return check_quality(df)
        case AnalysisType.DESCRIPTIVE_STATS:
            return compute_descriptive_stats(df)
        case AnalysisType.CORRELATION:
            return compute_correlation(df)
        case AnalysisType.TREND:
            return compute_trend_analysis(df)
        case AnalysisType.DISTRIBUTION:
            return compute_descriptive_stats(df)
        case AnalysisType.ANOMALY:
            return detect_anomalies(df)
        case AnalysisType.FORECAST:
            return run_forecast(df)
        case AnalysisType.CLUSTERING:
            return run_clustering(df)
        case AnalysisType.BAR | AnalysisType.PIE:
            return compute_descriptive_stats(df)
        case _:
            raise ValueError(f"Unknown analysis type: {analysis_type}")


def _generate_charts(
    df: pd.DataFrame,
    analysis_type: AnalysisType,
    result: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate appropriate charts for the analysis type."""
    charts: list[dict[str, Any]] = []

    try:
        match analysis_type:
            case AnalysisType.DISTRIBUTION:
                charts = generate_distribution_charts(df)
            case AnalysisType.CORRELATION:
                heatmap = generate_correlation_heatmap(df)
                if heatmap:
                    charts.append({
                        "chart_type": "heatmap",
                        "title": "Correlation Heatmap",
                        "data": heatmap,
                    })
            case AnalysisType.TREND:
                if "dates" in result and "values" in result:
                    trend = generate_trend_chart(
                        dates=result["dates"],
                        values=result["values"],
                        rolling_mean=result.get("rolling_mean", []),
                        value_col=result.get("value_column", "value"),
                    )
                    charts.append({
                        "chart_type": "line",
                        "title": f"Trend — {result.get('value_column', '')}",
                        "data": trend,
                    })
            case AnalysisType.ANOMALY:
                anomalies = result.get("anomalies_by_column", {})
                for col, info in list(anomalies.items())[:3]:
                    chart = generate_anomaly_chart(df, col, info["indices"])
                    charts.append({
                        "chart_type": "scatter",
                        "title": f"Anomalies — {col}",
                        "data": chart,
                    })
            case AnalysisType.FORECAST:
                if "forecast_values" in result:
                    chart = generate_forecast_chart(
                        historical_dates=result["historical_dates"],
                        historical_values=result["historical_values"],
                        forecast_dates=result["forecast_dates"],
                        forecast_values=result["forecast_values"],
                        conf_lower=result["confidence_lower"],
                        conf_upper=result["confidence_upper"],
                        value_col=result.get("value_column", "value"),
                    )
                    charts.append({
                        "chart_type": "line",
                        "title": "SARIMA Forecast",
                        "data": chart,
                    })
            case AnalysisType.CLUSTERING:
                if "pca_components" in result:
                    chart = generate_cluster_chart(
                        components=result["pca_components"],
                        labels=result["labels"],
                        centroids=result.get("pca_centroids"),
                    )
                    charts.append({
                        "chart_type": "scatter",
                        "title": "KMeans Clustering",
                        "data": chart,
                    })
            case AnalysisType.QUALITY:
                box = generate_box_plots(df)
                if box:
                    charts.append({
                        "chart_type": "box",
                        "title": "Box Plots",
                        "data": box,
                    })
            case AnalysisType.BAR:
                # Generate bar charts for categorical columns
                for col, stats in list(result.get("categorical", {}).items())[:5]:
                    counts = stats.get("value_counts", {})
                    if counts:
                        charts.append({
                            "chart_type": "bar",
                            "title": f"Category Counts — {col}",
                            "data": generate_bar_chart(list(counts.keys()), list(counts.values()), f"Top 20 Categories in {col}"),
                        })
            case AnalysisType.PIE:
                # Generate pie charts for categorical columns
                for col, stats in list(result.get("categorical", {}).items())[:3]:
                    counts = stats.get("value_counts", {})
                    if counts:
                        charts.append({
                            "chart_type": "pie",
                            "title": f"Distribution of {col}",
                            "data": generate_pie_chart(list(counts.keys()), list(counts.values()), f"Proportions for {col}"),
                        })
    except Exception as e:
        logger.warning("Chart generation failed for %s: %s", analysis_type.value, e)

    return charts


def _generate_summary_and_insights(
    df: pd.DataFrame,
    analysis_type: AnalysisType,
    result: dict[str, Any],
) -> tuple[str, list[str]]:
    """Generate human-readable summary and insights for the analysis."""
    summary = ""
    insights = []

    match analysis_type:
        case AnalysisType.QUALITY:
            score = result.get("quality_score", 0)
            summary = f"The dataset has an overall quality score of {score}/100."
            insights = [
                f"Found {result.get('row_count', 0)} rows and {result.get('column_count', 0)} columns.",
                f"Missing values: {result.get('null_percentage', 0)}% across all cells.",
                f"Duplicate rows detected: {result.get('duplicate_rows', 0)}."
            ]
        case AnalysisType.DESCRIPTIVE_STATS:
            summary = "Statistical overview of numeric columns in the dataset."
            insights = [
                f"Total numeric columns analyzed: {len(result.get('numeric_stats', {}))}.",
                "Key metrics like mean, median, and variance calculated for all features."
            ]
        case AnalysisType.CORRELATION:
            summary = "Analysis of relationships between different numeric variables."
            insights = [
                "Identified strong correlations that could indicate predictive relationships.",
                "Multicollinearity check performed to detect redundant features."
            ]
        case AnalysisType.TREND:
            summary = f"Time-series trend detected for the selected value column."
            insights = [
                "Detected overall direction (increasing/decreasing) of the data over time.",
                "Calculated rolling averages to smooth out short-term fluctuations."
            ]
        case AnalysisType.ANOMALY:
            anom_count = sum(len(v.get("indices", [])) for v in result.get("anomalies_by_column", {}).values())
            summary = f"Detected {anom_count} statistical anomalies across the dataset."
            insights = [
                "Outliers identified using IQR and Z-score methods.",
                "Potential data entry errors or extreme events highlighted for review."
            ]
        case AnalysisType.FORECAST:
            summary = "Future projections generated using SARIMA time-series modeling."
            insights = [
                "Predicted values for the next 30 steps with 95% confidence intervals.",
                "Model accounts for seasonal patterns and historical trends."
            ]
        case AnalysisType.CLUSTERING:
            summary = "Unsupervised grouping of data points based on feature similarity."
            insights = [
                f"Identified {result.get('n_clusters', 0)} distinct segments in the data.",
                "PCA projection used to visualize high-dimensional clusters in 2D."
            ]
        case _:
            summary = f"Detailed {analysis_type.value} analysis completed."
            insights = ["Automated patterns and statistical significance calculated."]

    return summary, insights
