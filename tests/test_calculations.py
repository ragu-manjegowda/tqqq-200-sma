"""Tests for calculation functions (SMA, percentages, etc.)."""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.calculations import compute_sma, pct_distance, format_pct


class TestComputeSMA:
    """Tests for SMA calculation."""

    def test_sma_basic(self):
        """Test basic SMA calculation."""
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        sma3 = compute_sma(data, 3)

        # First two should be NaN
        assert pd.isna(sma3.iloc[0])
        assert pd.isna(sma3.iloc[1])

        # Third should be average of first 3
        assert sma3.iloc[2] == 2.0
        assert sma3.iloc[3] == 3.0
        assert sma3.iloc[9] == 9.0

    def test_sma_200(self, sample_price_data):
        """Test 200-day SMA calculation."""
        sma200 = compute_sma(sample_price_data['adj_close'], 200)

        # First 199 should be NaN
        assert sma200.iloc[:199].isna().all()

        # 200th onwards should have values
        assert not pd.isna(sma200.iloc[199])

        # Verify calculation
        manual_sma = sample_price_data['adj_close'].iloc[:200].mean()
        assert abs(sma200.iloc[199] - manual_sma) < 0.01

    def test_sma_empty_series(self):
        """Test SMA with empty series."""
        data = pd.Series([])
        sma = compute_sma(data, 5)
        assert len(sma) == 0

    def test_sma_insufficient_data(self):
        """Test SMA when data length < period."""
        data = pd.Series([1, 2, 3])
        sma = compute_sma(data, 5)
        assert sma.isna().all()


class TestPctDistance:
    """Tests for percentage distance calculation."""

    def test_basic_positive_distance(self):
        """Test when current < target (positive distance)."""
        result = pct_distance(100, 110)
        assert result == pytest.approx(10.0, rel=1e-6)

    def test_basic_negative_distance(self):
        """Test when current > target (negative distance)."""
        result = pct_distance(110, 100)
        assert result == pytest.approx(-9.0909, rel=1e-3)

    def test_same_values(self):
        """Test when current == target."""
        result = pct_distance(100, 100)
        assert result == 0.0

    def test_zero_current(self):
        """Test when current is 0."""
        result = pct_distance(0, 100)
        assert result is None

    def test_nan_values(self):
        """Test with NaN values."""
        result = pct_distance(float('nan'), 100)
        assert result is None

        result = pct_distance(100, float('nan'))
        assert result is None

    def test_buy_threshold_5_percent(self):
        """Test typical buy threshold calculation."""
        sma = 500
        buy_level = sma * 1.05  # 525
        current = 525
        result = pct_distance(current, buy_level)
        assert result == pytest.approx(0.0, abs=1e-6)

    def test_sell_threshold_3_percent(self):
        """Test typical sell threshold calculation."""
        sma = 500
        sell_level = sma * 0.97  # 485
        current = 485
        result = pct_distance(current, sell_level)
        assert result == pytest.approx(0.0, abs=1e-6)


class TestFormatPct:
    """Tests for percentage formatting."""

    def test_positive_percentage(self):
        """Test formatting positive percentage."""
        assert format_pct(5.5) == "+5.50%"
        assert format_pct(10.0) == "+10.00%"

    def test_negative_percentage(self):
        """Test formatting negative percentage."""
        assert format_pct(-3.25) == "-3.25%"
        assert format_pct(-10.5) == "-10.50%"

    def test_zero(self):
        """Test formatting zero."""
        assert format_pct(0.0) == "+0.00%"

    def test_none_value(self):
        """Test formatting None."""
        assert format_pct(None) == "N/A"

    def test_nan_value(self):
        """Test formatting NaN."""
        assert format_pct(float('nan')) == "N/A"

    def test_precision(self):
        """Test decimal precision."""
        assert format_pct(1.234567) == "+1.23%"
        assert format_pct(-9.876543) == "-9.88%"

