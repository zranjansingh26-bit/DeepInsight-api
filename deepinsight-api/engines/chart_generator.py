"""
DeepInsight Starter Suite — Chart Generator Engine.

Generates Plotly JSON charts for various analysis types.
All functions return serializable dict representations of Plotly figures.
"""

import json
import logging
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

logger = logging.getLogger(__name__)


def _fig_to_dict(fig: go.Figure) -> dict[str, Any]:
    """Convert a Plotly figure to a JSON-serializable dict."""
    return json.loads(pio.to_json(fig))


def generate_histogram(
    df: pd.DataFrame, column: str, title: str | None = None
) -> dict[str, Any]:
    """Generate a histogram for a numeric column."""
    fig = px.histogram(
        df, x=column,
        title=title or f"Distribution of {column}",
        template="plotly_dark",
        color_discrete_sequence=["#6366f1"],
        nbins=30,
    )
    fig.update_layout(xaxis_title=column, yaxis_title="Count", bargap=0.05)
    return _fig_to_dict(fig)


def generate_distribution_charts(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Generate distribution charts for all numeric columns."""
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols[:10]:
        chart = generate_histogram(df, col)
        charts.append({"chart_type": "histogram", "title": f"Distribution of {col}", "data": chart})
    logger.info("Generated %d distribution charts", len(charts))
    return charts


def generate_box_plots(df: pd.DataFrame) -> dict[str, Any]:
    """Generate box plots for all numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return {}
    fig = go.Figure()
    for col in numeric_cols[:10]:
        fig.add_trace(go.Box(y=df[col].dropna(), name=col))
    fig.update_layout(title="Box Plots — Numeric Columns", template="plotly_dark", yaxis_title="Values")
    return _fig_to_dict(fig)


def generate_correlation_heatmap(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a correlation heatmap for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return {}
    corr = numeric_df.corr()
    fig = px.imshow(
        corr, text_auto=".2f", title="Correlation Heatmap",
        template="plotly_dark", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
    )
    fig.update_layout(width=700, height=600)
    return _fig_to_dict(fig)


def generate_scatter_matrix(df: pd.DataFrame, max_cols: int = 5) -> dict[str, Any]:
    """Generate a scatter matrix for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return {}
    cols = numeric_cols[:max_cols]
    fig = px.scatter_matrix(df[cols], title="Scatter Matrix", template="plotly_dark")
    fig.update_traces(diagonal_visible=True)
    fig.update_layout(width=800, height=800)
    return _fig_to_dict(fig)


def generate_trend_chart(
    dates: list[str], values: list[float],
    rolling_mean: list[float], value_col: str,
) -> dict[str, Any]:
    """Generate a trend line chart with rolling mean overlay."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=values, mode="lines", name=value_col, line=dict(color="#6366f1", width=1), opacity=0.7))
    fig.add_trace(go.Scatter(x=dates, y=rolling_mean, mode="lines", name="Rolling Mean", line=dict(color="#f59e0b", width=2)))
    fig.update_layout(title=f"Trend Analysis — {value_col}", template="plotly_dark", xaxis_title="Date", yaxis_title=value_col)
    return _fig_to_dict(fig)


def generate_bar_chart(categories: list[str], values: list[int], title: str) -> dict[str, Any]:
    """Generate a vertical bar chart."""
    fig = px.bar(
        x=categories, y=values, title=title,
        template="plotly_dark",
        color_discrete_sequence=["#10b981"],
        labels={"x": "Category", "y": "Count"}
    )
    return _fig_to_dict(fig)


def generate_pie_chart(categories: list[str], values: list[int], title: str) -> dict[str, Any]:
    """Generate a pie chart."""
    fig = px.pie(
        names=categories, values=values, title=title,
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _fig_to_dict(fig)


def generate_anomaly_chart(df: pd.DataFrame, column: str, anomaly_indices: list[int]) -> dict[str, Any]:
    """Generate a chart highlighting anomalies."""
    fig = go.Figure()
    normal_mask = ~df.index.isin(anomaly_indices)
    fig.add_trace(go.Scatter(x=df.index[normal_mask].tolist(), y=df.loc[normal_mask, column].tolist(), mode="markers", name="Normal", marker=dict(color="#6366f1", size=5)))
    if anomaly_indices:
        fig.add_trace(go.Scatter(x=anomaly_indices, y=df.loc[anomaly_indices, column].tolist(), mode="markers", name="Anomaly", marker=dict(color="#ef4444", size=8, symbol="x")))
    fig.update_layout(title=f"Anomaly Detection — {column}", template="plotly_dark", xaxis_title="Index", yaxis_title=column)
    return _fig_to_dict(fig)


def generate_cluster_chart(components: list[list[float]], labels: list[int], centroids: list[list[float]] | None = None) -> dict[str, Any]:
    """Generate a 2D scatter plot of clusters using PCA components."""
    fig = go.Figure()
    x_vals = [c[0] for c in components]
    y_vals = [c[1] for c in components]
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="markers", marker=dict(color=labels, colorscale="Viridis", size=6, showscale=True, colorbar=dict(title="Cluster")), name="Data Points"))
    if centroids:
        cx = [c[0] for c in centroids]
        cy = [c[1] for c in centroids]
        fig.add_trace(go.Scatter(x=cx, y=cy, mode="markers", marker=dict(color="red", size=14, symbol="diamond"), name="Centroids"))
    fig.update_layout(title="KMeans Clustering (PCA Projection)", template="plotly_dark", xaxis_title="PC 1", yaxis_title="PC 2")
    return _fig_to_dict(fig)


def generate_forecast_chart(
    historical_dates: list[str], historical_values: list[float],
    forecast_dates: list[str], forecast_values: list[float],
    conf_lower: list[float], conf_upper: list[float], value_col: str,
    title: str | None = None,
) -> dict[str, Any]:
    """Generate a forecast chart with confidence interval."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historical_dates, y=historical_values, mode="lines", name="Historical", line=dict(color="#6366f1")))
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_values, mode="lines", name="Forecast", line=dict(color="#f59e0b", dash="dash")))
    fig.add_trace(go.Scatter(x=forecast_dates + forecast_dates[::-1], y=conf_upper + conf_lower[::-1], fill="toself", fillcolor="rgba(245,158,11,0.15)", line=dict(color="rgba(255,255,255,0)"), name="95% Confidence"))
    fig.update_layout(title=title or f"Forecast — {value_col}", template="plotly_dark", xaxis_title="Date", yaxis_title=value_col)
    return _fig_to_dict(fig)
