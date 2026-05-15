"""
DeepInsight — Validation Engine.

Handles dataset validation, target detection, and quality warnings for classification.
"""

import logging
import pandas as pd
import numpy as np
from typing import Any, Optional

logger = logging.getLogger(__name__)

class ValidationEngine:
    """Validates dataset suitability for classification tasks."""

    @staticmethod
    def validate_classification(df: pd.DataFrame, target_col: str) -> dict[str, Any]:
        """
        Comprehensive validation for classification tasks.
        Returns a dict with 'is_valid', 'warnings', and 'diagnostics'.
        """
        warnings = []
        diagnostics = {
            "row_count": len(df),
            "col_count": len(df.columns),
            "target_col": target_col
        }

        if target_col not in df.columns:
            return {"is_valid": False, "error": f"Target column '{target_col}' not found in dataset.", "warnings": [], "diagnostics": diagnostics}

        target_series = df[target_col].dropna()
        
        # 1. Row count check
        if len(target_series) < 20:
            warnings.append("Insufficient data: Dataset has fewer than 20 non-null samples in target.")
        
        # 2. Unique values check
        unique_count = target_series.nunique()
        diagnostics["unique_classes"] = unique_count
        
        if unique_count < 2:
            return {"is_valid": False, "error": "Target column must have at least 2 unique classes.", "warnings": warnings, "diagnostics": diagnostics}
        
        if unique_count > 50:
             warnings.append(f"High cardinality: Target has {unique_count} unique values. This might be a regression problem or an ID column.")

        # 3. ID Column detection (simple heuristic)
        if unique_count == len(target_series) and len(target_series) > 10:
             return {"is_valid": False, "error": "Target column appears to be a unique ID or index.", "warnings": warnings, "diagnostics": diagnostics}

        # 4. Class Imbalance check
        class_counts = target_series.value_counts(normalize=True)
        imbalance_ratio = class_counts.max() / class_counts.min()
        diagnostics["class_distribution"] = class_counts.to_dict()
        
        if imbalance_ratio > 4.0:
            warnings.append(f"Class imbalance detected: Largest class is {imbalance_ratio:.1f}x larger than smallest.")

        return {
            "is_valid": True,
            "warnings": warnings,
            "diagnostics": diagnostics
        }

    @staticmethod
    def suggest_target(df: pd.DataFrame) -> Optional[str]:
        """Heuristically suggest the most likely target column."""
        # Avoid columns that look like IDs
        potential_targets = []
        for col in df.columns:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.9 and df[col].nunique() > 1:
                potential_targets.append(col)
        
        if not potential_targets:
            return df.columns[-1] if len(df.columns) > 0 else None
            
        # Priority 1: Common names
        common_names = ['target', 'label', 'class', 'category', 'type', 'output']
        for col in potential_targets:
            if col.lower() in common_names:
                return col
                
        # Priority 2: Last non-ID column
        return potential_targets[-1]
