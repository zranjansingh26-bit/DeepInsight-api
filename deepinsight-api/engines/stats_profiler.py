"""
DeepInsight Starter Suite — Statistical Profiler Engine.

Computes descriptive statistics, correlations, and trend analysis
for numeric and categorical columns.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_descriptive_stats(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute descriptive statistics for all columns.

    Returns:
        Dictionary with 'numeric' and 'categorical' keys.
    """
    numeric_stats = {}
    categorical_stats = {}

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    # ── Numeric columns ──────────────────────────────────────
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        stats = {
            "count": int(series.count()),
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "q1": round(float(series.quantile(0.25)), 4),
            "q3": round(float(series.quantile(0.75)), 4),
            "iqr": round(float(series.quantile(0.75) - series.quantile(0.25)), 4),
            "skewness": round(float(series.skew()), 4),
            "kurtosis": round(float(series.kurtosis()), 4),
            "variance": round(float(series.var()), 4),
        }
        numeric_stats[col] = stats

    # ── Categorical columns ──────────────────────────────────
    for col in categorical_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        value_counts = series.value_counts().head(20)
        categorical_stats[col] = {
            "count": int(series.count()),
            "unique_count": int(series.nunique()),
            "top_value": str(value_counts.index[0]) if len(value_counts) > 0 else None,
            "top_frequency": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            "value_counts": {
                str(k): int(v) for k, v in value_counts.items()
            },
        }

    logger.info(
        "Descriptive stats: %d numeric, %d categorical columns",
        len(numeric_stats),
        len(categorical_stats),
    )
    return {
        "numeric": numeric_stats,
        "categorical": categorical_stats,
        "total_rows": len(df),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
    }


def compute_correlation(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute correlation matrix for numeric columns.

    Returns:
        Dictionary with 'matrix', 'columns', and 'strong_correlations'.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return {
            "matrix": {},
            "columns": [],
            "strong_correlations": [],
            "message": "Need at least 2 numeric columns for correlation analysis.",
        }

    corr_matrix = numeric_df.corr()

    # Find strong correlations (|r| > 0.7, excluding self-correlation)
    strong = []
    cols = corr_matrix.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr_matrix.iloc[i, j]
            if abs(r) > 0.7:
                strong.append(
                    {
                        "column_1": cols[i],
                        "column_2": cols[j],
                        "correlation": round(float(r), 4),
                        "strength": "strong positive" if r > 0 else "strong negative",
                    }
                )

    # Convert matrix to serializable dict
    matrix_dict = {
        col: {row: round(float(corr_matrix.loc[row, col]), 4) for row in cols}
        for col in cols
    }

    logger.info(
        "Correlation analysis: %d columns, %d strong correlations",
        len(cols),
        len(strong),
    )
    return {
        "matrix": matrix_dict,
        "columns": cols,
        "strong_correlations": strong,
    }


def compute_trend_analysis(
    df: pd.DataFrame,
    date_col: str | None = None,
    value_col: str | None = None,
) -> dict[str, Any]:
    """
    Compute trend analysis with rolling means and percentage changes.

    Auto-detects date and value columns if not specified.
    """
    # Auto-detect date column
    if date_col is None:
        date_candidates = df.select_dtypes(
            include=["datetime64", "object"]
        ).columns
        for col in date_candidates:
            try:
                pd.to_datetime(df[col])
                date_col = col
                break
            except (ValueError, TypeError):
                continue

    if date_col is None:
        return {
            "message": "No date column detected. Trend analysis requires a time column.",
            "trends": {},
        }

    # Auto-detect value column (first numeric column)
    if value_col is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return {
                "message": "No numeric columns found for trend analysis.",
                "trends": {},
            }
        value_col = numeric_cols[0]

    # Prepare time series
    trend_df = df[[date_col, value_col]].copy()
    trend_df[date_col] = pd.to_datetime(trend_df[date_col], errors="coerce")
    trend_df = trend_df.dropna().sort_values(date_col)

    if len(trend_df) < 3:
        return {"message": "Not enough data points for trend analysis.", "trends": {}}

    # Rolling statistics
    window = max(3, len(trend_df) // 10)
    trend_df["rolling_mean"] = trend_df[value_col].rolling(window=window).mean()
    trend_df["rolling_std"] = trend_df[value_col].rolling(window=window).std()
    trend_df["pct_change"] = trend_df[value_col].pct_change() * 100

    # Overall trend direction
    first_half_mean = trend_df[value_col].iloc[: len(trend_df) // 2].mean()
    second_half_mean = trend_df[value_col].iloc[len(trend_df) // 2 :].mean()
    direction = "increasing" if second_half_mean > first_half_mean else "decreasing"

    result = {
        "date_column": date_col,
        "value_column": value_col,
        "direction": direction,
        "first_half_mean": round(float(first_half_mean), 4),
        "second_half_mean": round(float(second_half_mean), 4),
        "overall_mean": round(float(trend_df[value_col].mean()), 4),
        "overall_std": round(float(trend_df[value_col].std()), 4),
        "window_size": window,
        "data_points": len(trend_df),
        "dates": trend_df[date_col].dt.strftime("%Y-%m-%d").tolist(),
        "values": trend_df[value_col].round(4).tolist(),
        "rolling_mean": trend_df["rolling_mean"].round(4).tolist(),
    }

    logger.info("Trend analysis: %s is %s", value_col, direction)
    return result
