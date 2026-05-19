"""
DeepInsight Starter Suite — Forecaster Engine.

Time series forecasting using SARIMA, Exponential Smoothing, and Moving Average.
Auto-detects date/value columns and generates forecasts with confidence intervals.
"""

import logging
from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing

logger = logging.getLogger(__name__)


def run_forecast(
    df: pd.DataFrame,
    date_col: str | None = None,
    value_col: str | None = None,
    periods: int = 30,
    model_type: str = "sarima",
) -> dict[str, Any]:
    """
    Run time series forecasting.

    Args:
        df: Input DataFrame
        date_col: Date column name (auto-detected if None)
        value_col: Numeric value column (auto-detected if None)
        periods: Number of future periods to forecast
        model_type: 'sarima', 'exponential_smoothing', or 'moving_average'

    Returns:
        Dictionary with historical data, forecast, and confidence intervals.
    """
    # Auto-detect date column
    if date_col is None:
        # Step 1: Look for columns with date/time-like names first
        for col in df.columns:
            col_lower = str(col).lower()
            if any(k in col_lower for k in ["date", "time", "timestamp", "year", "month", "ds"]):
                try:
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    if parsed.notna().sum() > 0.5 * len(df):
                        date_col = col
                        break
                except Exception:
                    continue
        
        # Step 2: Fallback to scanning all columns (except float or boolean)
        if date_col is None:
            for col in df.columns:
                if df[col].dtype in ['float64', 'bool']:
                    continue
                try:
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    if parsed.notna().sum() > 0.5 * len(df):
                        date_col = col
                        break
                except Exception:
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
    ts_df = ts_df.dropna()
    
    # Aggregate duplicates by taking the mean value per date
    ts_df = ts_df.groupby(date_col, as_index=False)[value_col].mean()
    ts_df = ts_df.sort_values(date_col).reset_index(drop=True)

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
        "Forecasting %s: %d points, freq=%s, seasonal=%d, model=%s",
        value_col, len(series), freq, seasonal_period, model_type,
    )

    try:
        fc_values = []
        lower = []
        upper = []
        
        hist_dates = series.index.strftime("%Y-%m-%d").tolist()
        hist_values = series.values.tolist()

        if model_type == "sarima":
            order = (1, 1, 1)
            seasonal_order = (1, 1, 0, seasonal_period) if seasonal_period > 1 else (0, 0, 0, 0)
            model = SARIMAX(series, order=order, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
            fitted = model.fit(disp=False, maxiter=200)
            forecast_result = fitted.get_forecast(steps=periods)
            forecast_series = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int()
            
            fc_dates = forecast_series.index.strftime("%Y-%m-%d").tolist()
            fc_values = forecast_series.values.tolist()
            lower = conf_int.iloc[:, 0].values.tolist()
            upper = conf_int.iloc[:, 1].values.tolist()
            aic_val = round(float(fitted.aic), 2) if np.isfinite(fitted.aic) else None
            
        elif model_type == "exponential_smoothing":
            trend = "add"
            seasonal = "add" if seasonal_period > 1 and min(series) > 0 else None
            model = ExponentialSmoothing(series, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_period if seasonal else None)
            fitted = model.fit()
            forecast_series = fitted.forecast(periods)
            
            # Simple standard error based confidence interval for HW
            std_error = series.std() * 0.2
            
            fc_dates = forecast_series.index.strftime("%Y-%m-%d").tolist()
            fc_values = forecast_series.values.tolist()
            lower = [v - 1.96 * std_error for v in fc_values]
            upper = [v + 1.96 * std_error for v in fc_values]
            
        elif model_type == "moving_average":
            # Simple Moving Average extended forward
            window = min(len(series) // 4, 7)
            ma_val = series.rolling(window=window).mean().iloc[-1]
            if np.isnan(ma_val):
                ma_val = series.mean()
                
            std_error = series.std() * 0.5
            
            # Generate future dates based on freq
            last_date = series.index[-1]
            future_dates = pd.date_range(start=last_date, periods=periods + 1, freq=freq)[1:]
            
            fc_dates = future_dates.strftime("%Y-%m-%d").tolist()
            fc_values = [ma_val] * periods
            lower = [v - 1.96 * std_error for v in fc_values]
            upper = [v + 1.96 * std_error for v in fc_values]
            
        elif model_type == "prophet":
            from prophet import Prophet
            logging.getLogger('prophet').setLevel(logging.WARNING)
            
            df_p = pd.DataFrame({
                "ds": pd.to_datetime(series.index).tz_localize(None),
                "y": series.values
            })
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
            model.fit(df_p)
            future = model.make_future_dataframe(periods=periods, freq=freq)
            forecast = model.predict(future)
            
            fc_series = forecast.tail(periods)
            fc_dates = fc_series['ds'].dt.strftime("%Y-%m-%d").tolist()
            fc_values = fc_series['yhat'].tolist()
            lower = fc_series['yhat_lower'].tolist()
            upper = fc_series['yhat_upper'].tolist()
        else:
            return {"error": f"Unknown model type {model_type}"}

        # Clean NaN/Inf values
        fc_values = [float(v) if np.isfinite(v) else 0.0 for v in fc_values]
        lower = [float(v) if np.isfinite(v) else 0.0 for v in lower]
        upper = [float(v) if np.isfinite(v) else 0.0 for v in upper]
        hist_values = [float(v) if np.isfinite(v) else 0.0 for v in hist_values]

        result = {
            "model_type": model_type,
            "date_column": date_col,
            "value_column": value_col,
            "frequency": freq,
            "seasonal_period": seasonal_period,
            "historical_dates": hist_dates,
            "historical_values": hist_values,
            "forecast_dates": fc_dates,
            "forecast_values": fc_values,
            "confidence_lower": lower,
            "confidence_upper": upper,
            "periods": periods,
        }
        if model_type == "sarima":
            result["model_order"] = list(order)
            result["seasonal_order"] = list(seasonal_order)
            if aic_val is not None:
                result["aic"] = aic_val

        logger.info("Forecast complete: %d periods ahead", periods)
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
