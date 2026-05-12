"""
DeepInsight Starter Suite — SARIMA Forecaster Engine.

Time series forecasting using SARIMA (Seasonal ARIMA) from statsmodels.
Auto-detects date/value columns and generates forecasts with confidence intervals.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

logger = logging.getLogger(__name__)


def run_forecast(
    df: pd.DataFrame,
    date_col: str | None = None,
    value_col: str | None = None,
    periods: int = 30,
) -> dict[str, Any]:
    """
    Run SARIMA forecast on a time series.

    Args:
        df: Input DataFrame
        date_col: Date column name (auto-detected if None)
        value_col: Numeric value column (auto-detected if None)
        periods: Number of future periods to forecast

    Returns:
        Dictionary with historical data, forecast, and confidence intervals.
    """
    # Auto-detect date column
    if date_col is None:
        date_candidates = df.select_dtypes(include=["datetime64", "object"]).columns
        for col in date_candidates:
            try:
                pd.to_datetime(df[col])
                date_col = col
                break
            except (ValueError, TypeError):
                continue

    if date_col is None:
        return {"error": "No date column found for forecasting."}

    # Auto-detect value column
    if value_col is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return {"error": "No numeric column found for forecasting."}
        value_col = numeric_cols[0]

    # Prepare time series
    ts_df = df[[date_col, value_col]].copy()
    ts_df[date_col] = pd.to_datetime(ts_df[date_col], errors="coerce")
    ts_df = ts_df.dropna().sort_values(date_col).reset_index(drop=True)

    if len(ts_df) < 10:
        return {"error": "Need at least 10 data points for forecasting."}

    ts_df = ts_df.set_index(date_col)
    series = ts_df[value_col]

    # Infer frequency
    freq = pd.infer_freq(series.index)
    if freq is None:
        freq = "D"
    series = series.asfreq(freq, method="ffill")

    # Determine seasonal period
    seasonal_period = _detect_seasonality(freq)

    logger.info(
        "Forecasting %s: %d points, freq=%s, seasonal=%d",
        value_col, len(series), freq, seasonal_period,
    )

    try:
        # Fit SARIMA model
        order = (1, 1, 1)
        seasonal_order = (1, 1, 0, seasonal_period) if seasonal_period > 1 else (0, 0, 0, 0)

        model = SARIMAX(
            series,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fitted = model.fit(disp=False, maxiter=200)

        # Forecast
        forecast_result = fitted.get_forecast(steps=periods)
        forecast_values = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()

        # Build response
        hist_dates = series.index.strftime("%Y-%m-%d").tolist()
        hist_values = series.values.tolist()

        fc_dates = forecast_values.index.strftime("%Y-%m-%d").tolist()
        fc_values = forecast_values.values.tolist()
        lower = conf_int.iloc[:, 0].values.tolist()
        upper = conf_int.iloc[:, 1].values.tolist()

        # Clean NaN/Inf values
        fc_values = [float(v) if np.isfinite(v) else 0.0 for v in fc_values]
        lower = [float(v) if np.isfinite(v) else 0.0 for v in lower]
        upper = [float(v) if np.isfinite(v) else 0.0 for v in upper]
        hist_values = [float(v) if np.isfinite(v) else 0.0 for v in hist_values]

        result = {
            "date_column": date_col,
            "value_column": value_col,
            "frequency": freq,
            "seasonal_period": seasonal_period,
            "model_order": list(order),
            "seasonal_order": list(seasonal_order),
            "aic": round(float(fitted.aic), 2) if np.isfinite(fitted.aic) else None,
            "historical_dates": hist_dates,
            "historical_values": hist_values,
            "forecast_dates": fc_dates,
            "forecast_values": fc_values,
            "confidence_lower": lower,
            "confidence_upper": upper,
            "periods": periods,
        }
        logger.info("Forecast complete: %d periods ahead, AIC=%.2f", periods, fitted.aic)
        return result

    except Exception as e:
        logger.error("Forecasting failed: %s", str(e))
        return {"error": f"Forecasting failed: {str(e)}"}


def _detect_seasonality(freq: str) -> int:
    """Map frequency string to seasonal period."""
    freq_upper = freq.upper()
    if freq_upper.startswith("D"):
        return 7
    elif freq_upper.startswith("W"):
        return 52
    elif freq_upper.startswith("M"):
        return 12
    elif freq_upper.startswith("Q"):
        return 4
    elif freq_upper.startswith("H"):
        return 24
    return 1
