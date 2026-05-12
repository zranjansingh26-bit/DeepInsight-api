"""Tests for the stats profiler engine."""

import numpy as np
import pandas as pd
import pytest

from engines.stats_profiler import (
    compute_descriptive_stats,
    compute_correlation,
    compute_trend_analysis,
)


class TestDescriptiveStats:
    def test_numeric_stats(self, numeric_only_df):
        result = compute_descriptive_stats(numeric_only_df)
        assert "numeric" in result
        assert len(result["numeric"]) == 4
        for col, stats in result["numeric"].items():
            assert "mean" in stats
            assert "median" in stats
            assert "std" in stats
            assert "skewness" in stats

    def test_categorical_stats(self, sample_df):
        result = compute_descriptive_stats(sample_df)
        assert "categorical" in result
        assert len(result["categorical"]) > 0

    def test_empty_df(self, empty_df):
        result = compute_descriptive_stats(empty_df)
        assert result["total_rows"] == 0


class TestCorrelation:
    def test_correlation_matrix(self, numeric_only_df):
        result = compute_correlation(numeric_only_df)
        assert "matrix" in result
        assert "columns" in result
        assert len(result["columns"]) == 4

    def test_single_column(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = compute_correlation(df)
        assert "message" in result

    def test_strong_correlations(self):
        df = pd.DataFrame({
            "a": range(100),
            "b": range(100),  # perfectly correlated with a
            "c": np.random.randn(100),
        })
        result = compute_correlation(df)
        strong = result["strong_correlations"]
        assert any(s["column_1"] == "a" and s["column_2"] == "b" for s in strong)


class TestTrendAnalysis:
    def test_auto_detect(self, time_series_df):
        result = compute_trend_analysis(time_series_df)
        assert "direction" in result
        assert result["direction"] in ("increasing", "decreasing")
        assert result["data_points"] > 0

    def test_no_date_column(self, numeric_only_df):
        result = compute_trend_analysis(numeric_only_df)
        assert "message" in result
