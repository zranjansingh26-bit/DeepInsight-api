"""
Shared test fixtures for DeepInsight Starter Suite.
"""

import io
import os
import sys

import pandas as pd
import pytest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_df():
    """A simple numeric + categorical DataFrame for testing."""
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=100, freq="D"),
        "product": ["Widget A", "Widget B", "Gadget C", "Gadget D"] * 25,
        "category": ["Electronics", "Home", "Electronics", "Home"] * 25,
        "quantity": [int(x) for x in (10 + 5 * __import__("numpy").random.randn(100))],
        "revenue": [round(float(x), 2) for x in (500 + 200 * __import__("numpy").random.randn(100))],
        "region": ["North", "South", "East", "West"] * 25,
    })


@pytest.fixture
def sample_df_with_nulls():
    """DataFrame with missing values for quality testing."""
    df = pd.DataFrame({
        "a": [1, 2, None, 4, 5],
        "b": ["x", None, "z", None, "w"],
        "c": [10.0, 20.0, 30.0, 40.0, 50.0],
    })
    return df


@pytest.fixture
def empty_df():
    """Empty DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def numeric_only_df():
    """DataFrame with only numeric columns."""
    import numpy as np
    np.random.seed(42)
    return pd.DataFrame({
        "feature_1": np.random.randn(50),
        "feature_2": np.random.randn(50) * 2 + 1,
        "feature_3": np.random.randn(50) * 0.5 - 1,
        "feature_4": np.random.randn(50) * 3,
    })


@pytest.fixture
def time_series_df():
    """DataFrame suitable for time series / forecasting tests."""
    import numpy as np
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=120, freq="D")
    trend = np.linspace(100, 200, 120)
    noise = np.random.randn(120) * 10
    seasonal = 20 * np.sin(np.arange(120) * 2 * np.pi / 7)
    return pd.DataFrame({
        "date": dates,
        "value": trend + noise + seasonal,
    })


@pytest.fixture
def csv_bytes(sample_df):
    """CSV file as bytes (for file parser testing)."""
    return sample_df.to_csv(index=False).encode("utf-8")
