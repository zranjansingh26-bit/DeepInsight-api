"""Tests for the forecaster engine."""

import pytest
import pandas as pd
import numpy as np

from engines.forecaster import run_forecast


class TestRunForecast:
    def test_basic_forecast(self, time_series_df):
        result = run_forecast(time_series_df, periods=14)
        assert "error" not in result
        assert len(result["forecast_values"]) == 14
        assert len(result["forecast_dates"]) == 14
        assert len(result["confidence_lower"]) == 14
        assert "aic" in result

    def test_no_date_column(self, numeric_only_df):
        result = run_forecast(numeric_only_df)
        assert "error" in result

    def test_too_few_points(self):
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "value": [1, 2, 3],
        })
        result = run_forecast(df)
        assert "error" in result

    def test_custom_columns(self, time_series_df):
        result = run_forecast(
            time_series_df,
            date_col="date",
            value_col="value",
            periods=7,
        )
        assert "error" not in result
        assert result["date_column"] == "date"
        assert result["value_column"] == "value"
