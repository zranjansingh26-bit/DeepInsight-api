"""
DeepInsight Starter Suite — Anomaly Detector Engine.

Detects anomalies using IQR, Z-score, Isolation Forest, Local Outlier Factor, and DBSCAN on numeric columns.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def detect_anomalies(
    df: pd.DataFrame,
    method: str = "iqr",
    threshold: float = 1.5,
) -> dict[str, Any]:
    """
    Detect anomalies in numeric columns.

    Args:
        df: Input DataFrame
        method: Detection method — 'iqr', 'zscore', 'isolation_forest', 'lof', or 'dbscan'
        threshold: Method-specific sensitivity/threshold.

    Returns:
        Dictionary with anomaly counts, indices, and values.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return {"error": "No numeric columns found for anomaly detection."}

    all_anomalies = {}
    total_anomalies = 0

    # Multivariate methods run on the whole numeric dataset at once
    if method in ["isolation_forest", "lof", "dbscan"]:
        # Drop rows with NaNs across numeric columns for sklearn models
        valid_df = df[numeric_cols].dropna()
        if len(valid_df) < 10:
            return {"error": f"Need at least 10 valid data points for {method}."}
            
        # Normalize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(valid_df)
        
        indices = []
        if method == "isolation_forest":
            contamination = threshold if 0 < threshold <= 0.5 else 0.05
            model = IsolationForest(contamination=contamination, random_state=42)
            preds = model.fit_predict(scaled_data)
            indices = valid_df.index[preds == -1].tolist()
        elif method == "lof":
            contamination = threshold if 0 < threshold <= 0.5 else 0.05
            model = LocalOutlierFactor(contamination=contamination)
            preds = model.fit_predict(scaled_data)
            indices = valid_df.index[preds == -1].tolist()
        elif method == "dbscan":
            eps = threshold if threshold > 0 else 0.5
            model = DBSCAN(eps=eps, min_samples=5)
            preds = model.fit_predict(scaled_data)
            indices = valid_df.index[preds == -1].tolist()

        total_anomalies = len(indices)
        
        # Format output similar to column-wise methods for frontend compatibility, 
        # or we can attach the global anomalies to all numeric columns.
        for col in numeric_cols:
            anomaly_values = df.loc[indices, col].tolist() if indices else []
            anomaly_values = [
                float(v) if np.isfinite(v) else 0.0 for v in anomaly_values
            ]
            all_anomalies[col] = {
                "count": total_anomalies,
                "percentage": round(total_anomalies / len(df) * 100, 2),
                "indices": indices,
                "values": anomaly_values[:50],  # Limit to 50
            }
            
    else:
        # Univariate methods
        if method == "zscore":
            threshold = threshold if threshold != 1.5 else 3.0

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 4:
                continue

            if method == "iqr":
                indices = _iqr_anomalies(series, threshold)
            else:
                indices = _zscore_anomalies(series, threshold)

            anomaly_values = df.loc[indices, col].tolist() if indices else []
            anomaly_values = [
                float(v) if np.isfinite(v) else 0.0 for v in anomaly_values
            ]

            all_anomalies[col] = {
                "count": len(indices),
                "percentage": round(len(indices) / len(series) * 100, 2),
                "indices": indices,
                "values": anomaly_values[:50],  # Limit to 50
            }
            total_anomalies += len(indices)

    result = {
        "method": method,
        "threshold": threshold,
        "total_anomalies": total_anomalies,
        "columns_analyzed": len(numeric_cols),
        "anomalies_by_column": all_anomalies,
    }

    logger.info(
        "Anomaly detection (%s): %d anomalies across %d columns",
        method, total_anomalies, len(numeric_cols),
    )
    return result


def _iqr_anomalies(series: pd.Series, multiplier: float) -> list[int]:
    """Detect anomalies using the IQR method."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr

    mask = (series < lower) | (series > upper)
    return series.index[mask].tolist()


def _zscore_anomalies(series: pd.Series, cutoff: float) -> list[int]:
    """Detect anomalies using the Z-score method."""
    mean = series.mean()
    std = series.std()
    if std == 0:
        return []
    z_scores = ((series - mean) / std).abs()
    mask = z_scores > cutoff
    return series.index[mask].tolist()
