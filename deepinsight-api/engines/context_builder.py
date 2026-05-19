"""
DeepInsight Starter Suite — Context Builder Engine.

Builds structured LLM context from dataset metadata, sample rows,
and statistical summaries for the GenAI chat pipeline.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

from db import repository
from models.schemas import AnalysisType
from engines.stats_profiler import compute_descriptive_stats

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHARS = 12000


def build_context(df: pd.DataFrame, dataset_meta: dict | None = None) -> str:
    """
    Build a comprehensive context string for LLM consumption.

    Args:
        df: The dataset as a DataFrame
        dataset_meta: Optional dataset metadata from the database

    Returns:
        Formatted context string with schema, samples, and stats.
    """
    parts: list[str] = []

    # ── Dataset overview ─────────────────────────────────────
    parts.append("## Dataset Overview")
    if dataset_meta:
        parts.append(f"- **File**: {dataset_meta.get('file_name', 'unknown')}")
    parts.append(f"- **Rows**: {len(df):,}")
    parts.append(f"- **Columns**: {len(df.columns)}")
    null_pct = round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2) if df.size > 0 else 0
    parts.append(f"- **Overall Null %**: {null_pct}%")
    parts.append("")

    # ── Schema ───────────────────────────────────────────────
    parts.append("## Column Schema")
    parts.append("| Column | Type | Nulls | Unique |")
    parts.append("|--------|------|-------|--------|")
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = int(df[col].isnull().sum())
        uniq = int(df[col].nunique())
        parts.append(f"| {col} | {dtype} | {nulls} | {uniq} |")
    parts.append("")

    # ── Sample rows ──────────────────────────────────────────
    parts.append("## Sample Data (first 5 rows)")
    sample = df.head(5)
    sample_str = sample.to_markdown(index=False)
    if sample_str:
        parts.append(sample_str)
    parts.append("")

    # ── Summary statistics ───────────────────────────────────
    stats = compute_descriptive_stats(df)
    numeric = stats.get("numeric", {})
    categorical = stats.get("categorical", {})

    if numeric:
        parts.append("## Numeric Column Statistics")
        for col, s in list(numeric.items())[:10]:
            parts.append(
                f"- **{col}**: mean={s['mean']}, median={s['median']}, "
                f"std={s['std']}, min={s['min']}, max={s['max']}"
            )
        parts.append("")

    if categorical:
        parts.append("## Categorical Column Statistics")
        for col, s in list(categorical.items())[:10]:
            top_vals = list(s.get("value_counts", {}).items())[:5]
            top_str = ", ".join(f"{k}({v})" for k, v in top_vals)
            parts.append(f"- **{col}**: {s['unique_count']} unique — top: {top_str}")
        parts.append("")

    # ── Inject recent Advanced Analytics (Forecast / Anomaly) ──
    if dataset_meta and "id" in dataset_meta:
        dataset_id = dataset_meta["id"]
        
        # Check for Anomaly
        anomaly = repository.get_analysis(dataset_id, AnalysisType.ANOMALY.value)
        if anomaly:
            parts.append("## Recent Anomaly Detection")
            res = anomaly.get("results", {})
            parts.append(f"- **Method used**: {res.get('method', 'Unknown')}")
            parts.append(f"- **Total anomalies detected**: {res.get('total_anomalies', 0)}")
            anom_by_col = res.get("anomalies_by_column", {})
            for col, info in list(anom_by_col.items())[:5]:
                if info.get("count", 0) > 0:
                    parts.append(f"- **{col}**: {info.get('count')} anomalies ({info.get('percentage')}%)")
            parts.append("")

        # Check for Forecast
        forecast = repository.get_analysis(dataset_id, AnalysisType.FORECAST.value)
        if forecast:
            parts.append("## Recent Time Series Forecast")
            res = forecast.get("results", {})
            parts.append(f"- **Model**: {res.get('model_type', 'Unknown')}")
            parts.append(f"- **Target Column**: {res.get('value_column', 'Unknown')}")
            parts.append(f"- **Date Column**: {res.get('date_column', 'Unknown')}")
            parts.append(f"- **Periods forecasted**: {res.get('periods', 0)}")
            
            fc_dates = res.get("forecast_dates", [])
            fc_vals = res.get("forecast_values", [])
            if fc_dates and fc_vals:
                parts.append("### Forecasted Values (first 5 steps)")
                for d, v in zip(fc_dates[:5], fc_vals[:5]):
                    parts.append(f"- {d}: {round(v, 2) if isinstance(v, (int, float)) else v}")
            parts.append("")

    context = "\n".join(parts)

    # Truncate if too long
    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS] + "\n\n[... truncated for length]"

    logger.info("Built context: %d chars", len(context))
    return context


def build_system_prompt(context: str) -> str:
    """Build the system prompt for the LLM."""
    return (
        "You are DeepInsight AI, a data analytics assistant. "
        "You help users understand their datasets by answering questions about the data, "
        "identifying patterns, suggesting analyses, and providing actionable insights.\n\n"
        "Below is the dataset context. Use this information to answer user questions accurately.\n"
        "Always reference specific columns, values, and statistics when possible.\n"
        "If you're unsure about something, say so rather than guessing.\n\n"
        "After your answer, suggest 2-3 follow-up questions the user might want to ask.\n"
        "Format follow-up questions as a JSON array under the key 'follow_up_questions'.\n\n"
        f"---\n\n{context}"
    )
