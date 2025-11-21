"""Pytest configuration and fixtures."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import os
import tempfile


@pytest.fixture
def sample_price_data():
    """Generate sample price data for testing."""
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    # Generate synthetic price data with trend
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 2)
    df = pd.DataFrame({'adj_close': prices}, index=dates)
    return df


@pytest.fixture
def sample_qqq_data():
    """Generate sample QQQ data with known SMA."""
    dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
    # Create data where price crosses SMA
    prices = []
    for i in range(250):
        if i < 100:
            prices.append(500 + i * 0.5)  # Uptrend
        elif i < 150:
            prices.append(550 - (i - 100) * 0.3)  # Downtrend
        else:
            prices.append(535 + (i - 150) * 0.4)  # Uptrend again
    
    df = pd.DataFrame({'adj_close': prices}, index=dates)
    return df


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def mock_state_file(tmp_path):
    """Create a temporary state file."""
    return str(tmp_path / "data" / "position_state.json")


@pytest.fixture
def mock_cache_file(tmp_path):
    """Create a temporary cache file."""
    return str(tmp_path / "data" / "market_data_cache.pkl")


@pytest.fixture
def mock_log_file(tmp_path):
    """Create a temporary log file."""
    return str(tmp_path / "data" / "signals_log.csv")

