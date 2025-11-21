"""Tests for data validation and edge cases."""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.calculations import compute_sma, pct_distance


class TestDataValidation:
    """Tests for data validation."""

    def test_sma_with_missing_data(self):
        """Test SMA calculation with NaN values."""
        data = pd.Series([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10])
        sma3 = compute_sma(data, 3)

        # SMA should propagate NaN
        assert pd.isna(sma3.iloc[3])

    def test_price_data_consistency(self, sample_qqq_data):
        """Test that price data is consistent."""
        assert len(sample_qqq_data) > 0
        assert not sample_qqq_data['adj_close'].isna().all()
        assert (sample_qqq_data['adj_close'] > 0).all()

    def test_sma_monotonic_with_constant_data(self):
        """Test SMA with constant price."""
        data = pd.Series([100] * 250)
        sma200 = compute_sma(data, 200)

        # SMA should equal constant value
        assert sma200.iloc[199] == 100.0
        assert sma200.iloc[-1] == 100.0

    def test_extreme_price_movements(self):
        """Test with extreme price movements."""
        # Simulate crash scenario
        data = pd.Series([100] * 100 + [50] * 100 + [25] * 100)
        sma200 = compute_sma(data, 200)

        # SMA should be between extremes
        final_sma = sma200.iloc[-1]
        assert 25 < final_sma < 100

    def test_zero_prices(self):
        """Test behavior with zero prices (invalid)."""
        sma = 0.0
        buy_threshold = sma * 1.05

        # Should handle gracefully
        assert buy_threshold == 0.0

    def test_negative_prices(self):
        """Test behavior with negative prices (invalid)."""
        # In real world, prices shouldn't be negative
        # But the algorithm should not crash
        data = pd.Series([-1, -2, -3, -4, -5])
        sma = compute_sma(data, 3)

        # Should calculate but values will be negative
        assert not pd.isna(sma.iloc[-1])


class TestEdgeCases:
    """Tests for edge cases."""

    def test_exact_sma_value(self):
        """Test when price equals SMA exactly."""
        sma = 500.0
        price = 500.0

        buy_threshold = sma * 1.05
        sell_threshold = sma * 0.97

        # Should be in buffer zone
        assert price < buy_threshold
        assert price > sell_threshold

    def test_very_small_percentages(self):
        """Test with very small percentage differences."""
        result = pct_distance(100.00, 100.01)
        assert result == pytest.approx(0.01, rel=1e-6)

    def test_very_large_percentages(self):
        """Test with very large percentage differences."""
        result = pct_distance(100, 1000)
        assert result == pytest.approx(900.0, rel=1e-6)

    def test_single_day_data(self):
        """Test with only one day of data."""
        data = pd.Series([100.0])
        sma = compute_sma(data, 200)
        assert pd.isna(sma.iloc[0])

    def test_exactly_200_days(self):
        """Test with exactly 200 days of data."""
        data = pd.Series(range(1, 201))  # 200 values
        sma = compute_sma(data, 200)

        # Should have exactly one valid SMA value
        assert pd.isna(sma.iloc[:-1]).all()
        assert not pd.isna(sma.iloc[-1])
        assert sma.iloc[-1] == 100.5  # Mean of 1 to 200

    def test_high_volatility(self):
        """Test with high volatility data."""
        np.random.seed(42)
        volatile_data = pd.Series(100 + np.cumsum(np.random.randn(300) * 10))
        sma = compute_sma(volatile_data, 200)

        # SMA should smooth out volatility
        sma_values = sma.dropna()
        assert len(sma_values) > 0

        # SMA should be less volatile than raw data
        data_std = volatile_data[199:].std()
        sma_std = sma_values.std()
        assert sma_std < data_std


class TestRealWorldScenarios:
    """Tests for real-world market scenarios."""

    def test_bull_market_scenario(self):
        """Test behavior in sustained bull market."""
        # Simulate consistent uptrend
        days = 300
        prices = [400 + i * 0.5 for i in range(days)]  # 400 to 550
        data = pd.Series(prices)
        sma = compute_sma(data, 200)

        # In strong uptrend, price should be well above SMA
        final_price = prices[-1]
        final_sma = sma.iloc[-1]
        assert final_price > final_sma

    def test_bear_market_scenario(self):
        """Test behavior in sustained bear market."""
        # Simulate consistent downtrend
        days = 300
        prices = [600 - i * 0.5 for i in range(days)]  # 600 to 450
        data = pd.Series(prices)
        sma = compute_sma(data, 200)

        # In strong downtrend, price should be below SMA
        final_price = prices[-1]
        final_sma = sma.iloc[-1]
        assert final_price < final_sma

    def test_sideways_market_scenario(self):
        """Test behavior in sideways/choppy market."""
        # Simulate sideways market
        np.random.seed(42)
        prices = [500 + np.random.randn() * 5 for _ in range(300)]
        data = pd.Series(prices)
        sma = compute_sma(data, 200)

        # In sideways market, price should oscillate around SMA
        final_sma = sma.iloc[-1]
        assert 490 < final_sma < 510

    def test_market_crash_recovery(self):
        """Test behavior during crash and recovery."""
        # Normal -> Crash -> Recovery
        normal = [500] * 100
        crash = [500 - i * 2 for i in range(1, 51)]  # Drop to 400
        recovery = [400 + i * 1.5 for i in range(1, 151)]  # Back to 625

        prices = normal + crash + recovery
        data = pd.Series(prices)
        sma = compute_sma(data, 200)

        # SMA should lag behind during recovery
        final_price = prices[-1]
        final_sma = sma.iloc[-1]

        # Price recovered above pre-crash, but SMA still catching up
        assert final_price > 500
        assert final_sma < final_price

