import os
import sys
import pandas as pd
import numpy as np
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.forecaster import run_forecast_comparison

def generate_dummy_time_series():
    # Create 100 days of data with a slight trend and weekly seasonality
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    trend = np.linspace(10, 50, 100)
    seasonality = np.sin(np.arange(100) * (2 * np.pi / 7)) * 10
    noise = np.random.normal(0, 2, 100)
    
    values = trend + seasonality + noise
    
    df = pd.DataFrame({
        "date": dates,
        "sales": values
    })
    return df

def test_forecasting():
    print("Generating dummy time-series data...")
    df = generate_dummy_time_series()
    
    print("Running forecast comparison (Prophet, SARIMA, ES, MA)...")
    result = run_forecast_comparison(df, date_col="date", value_col="sales", periods=14)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
        
    print(f"\n[BEST MODEL]: {result['best_model_name'].upper()}")
    print("-" * 50)
    print("LEADERBOARD (Ranked by RMSE):")
    
    for idx, r in enumerate(result["leaderboard"], 1):
        metrics = r["metrics"]
        print(f"{idx}. {r['model'].upper().ljust(25)} | RMSE: {metrics['rmse']:.2f} | MAE: {metrics['mae']:.2f} | R2: {metrics['r2']:.2f}")

if __name__ == "__main__":
    test_forecasting()
