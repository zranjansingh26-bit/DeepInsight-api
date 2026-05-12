"""Tests for the anomaly detector engine."""

import pytest
import pandas as pd
import numpy as np

from engines.anomaly_detector import detect_anomalies


class TestDetectAnomalies:
    def test_iqr_method(self, numeric_only_df):
        result = detect_anomalies(numeric_only_df, method="iqr")
        assert "error" not in result
        assert result["method"] == "iqr"
        assert result["columns_analyzed"] > 0
        assert "anomalies_by_column" in result

    def test_zscore_method(self, numeric_only_df):
        result = detect_anomalies(numeric_only_df, method="zscore")
        assert result["method"] == "zscore"
        assert result["threshold"] == 3.0

    def test_detects_outliers(self):
        """Known outliers should be detected."""
        df = pd.DataFrame({
            "values": [1, 2, 3, 2, 1, 3, 2, 1, 100, 2],  # 100 is outlier
        })
        result = detect_anomalies(df, method="iqr")
        anomalies = result["anomalies_by_column"]["values"]
        assert anomalies["count"] > 0
        assert 8 in anomalies["indices"]  # index of 100

    def test_no_numeric_columns(self):
        df = pd.DataFrame({"a": ["x", "y", "z"]})
        result = detect_anomalies(df)
        assert "error" in result
