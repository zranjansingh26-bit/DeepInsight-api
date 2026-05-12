"""
DeepInsight Starter Suite — Data Quality Checker Engine.

Evaluates dataset quality across multiple dimensions:
completeness, duplicates, type consistency, and per-column stats.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def check_quality(df: pd.DataFrame) -> dict[str, Any]:
    """
    Run a comprehensive quality check on a DataFrame.

    Returns:
        Dictionary with quality_score, row_count, column_count,
        null_percentage, duplicate_rows, and column_metadata.
    """
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    # Completeness: percentage of non-null cells
    completeness = 1 - (missing_cells / total_cells) if total_cells else 0

    # Duplicate penalty: reduce score based on duplicate ratio
    dup_ratio = duplicate_rows / len(df) if len(df) > 0 else 0
    dup_penalty = dup_ratio * 10  # max 10-point penalty

    # Type consistency: penalise object columns with mixed types
    type_penalty = 0
    for col in df.columns:
        if df[col].dtype == object:
            non_null = df[col].dropna()
            if len(non_null) > 0:
                types = non_null.apply(type).nunique()
                if types > 1:
                    type_penalty += 2  # 2-point penalty per inconsistent column

    # Final score
    raw_score = completeness * 100 - dup_penalty - type_penalty
    quality_score = max(0, min(100, round(raw_score)))

    # Null percentage across entire dataset
    null_pct = round((missing_cells / total_cells * 100) if total_cells else 0, 2)

    # Per-column metadata
    columns = build_column_metadata(df)

    result = {
        "quality_score": quality_score,
        "row_count": len(df),
        "column_count": len(df.columns),
        "null_percentage": null_pct,
        "missing_cells": missing_cells,
        "duplicate_rows": duplicate_rows,
        "columns": columns,
    }
    logger.info(
        "Quality check: score=%d, rows=%d, cols=%d",
        quality_score,
        len(df),
        len(df.columns),
    )
    return result


def build_column_metadata(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Generate metadata for each column."""
    columns = []
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = round(null_count / len(df) * 100, 2) if len(df) > 0 else 0.0
        unique_count = int(df[col].nunique())

        # Sample up to 5 non-null values
        non_null = df[col].dropna()
        sample_values = (
            non_null.head(5).tolist() if len(non_null) > 0 else []
        )
        # Convert numpy types to native Python for JSON serialisation
        sample_values = [
            v.item() if isinstance(v, (np.integer, np.floating)) else v
            for v in sample_values
        ]

        columns.append(
            {
                "name": str(col),
                "dtype": str(df[col].dtype),
                "null_count": null_count,
                "null_percentage": null_pct,
                "unique_count": unique_count,
                "sample_values": sample_values,
            }
        )
    return columns