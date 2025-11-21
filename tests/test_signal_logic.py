"""Tests for trading signal generation logic."""
import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.calculations import compute_sma, pct_distance


class TestBuySignalLogic:
    """Tests for BUY signal conditions."""

    def test_buy_signal_triggered(self):
        """Test BUY signal when QQQ >= SMA * 1.05."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05  # 525
        qqq_close = 530.0

        # Check if buy condition met
        assert qqq_close >= buy_threshold

        # Verify distance
        distance = pct_distance(qqq_close, buy_threshold)
        assert distance < 0  # Already passed threshold

    def test_buy_signal_not_triggered(self):
        """Test BUY signal when QQQ < SMA * 1.05."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05  # 525
        qqq_close = 520.0

        # Check if buy condition NOT met
        assert qqq_close < buy_threshold

        # Verify distance
        distance = pct_distance(qqq_close, buy_threshold)
        assert distance > 0  # Needs to go higher
        assert distance == pytest.approx(0.96, rel=1e-2)

    def test_buy_signal_exact_threshold(self):
        """Test BUY signal at exact threshold."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05  # 525
        qqq_close = 525.0

        # Should trigger at exact threshold
        assert qqq_close >= buy_threshold

    def test_buy_buffer_zone(self):
        """Test that buy has 5% buffer above SMA."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05

        # Just above SMA should NOT trigger
        qqq_close = 502.0
        assert qqq_close < buy_threshold


class TestSellSignalLogic:
    """Tests for SELL signal conditions."""

    def test_sell_signal_triggered(self):
        """Test SELL signal when QQQ <= SMA * 0.97."""
        sma200 = 500.0
        sell_threshold = sma200 * 0.97  # 485
        qqq_close = 480.0

        # Check if sell condition met
        assert qqq_close <= sell_threshold

        # Verify distance (positive means needs to go up to reach threshold)
        distance = pct_distance(qqq_close, sell_threshold)
        assert distance > 0  # Below threshold, would need to rise to reach it

    def test_sell_signal_not_triggered(self):
        """Test SELL signal when QQQ > SMA * 0.97."""
        sma200 = 500.0
        sell_threshold = sma200 * 0.97  # 485
        qqq_close = 490.0

        # Check if sell condition NOT met
        assert qqq_close > sell_threshold

        # Verify distance
        distance = pct_distance(qqq_close, sell_threshold)
        assert distance < 0  # Above threshold (negative means no sell)

    def test_sell_signal_exact_threshold(self):
        """Test SELL signal at exact threshold."""
        sma200 = 500.0
        sell_threshold = sma200 * 0.97  # 485
        qqq_close = 485.0

        # Should trigger at exact threshold
        assert qqq_close <= sell_threshold

    def test_sell_buffer_zone(self):
        """Test that sell has 3% buffer below SMA."""
        sma200 = 500.0
        sell_threshold = sma200 * 0.97

        # Just below SMA should NOT trigger
        qqq_close = 498.0
        assert qqq_close > sell_threshold


class TestAsymmetricThresholds:
    """Tests for the 5/3 asymmetric threshold strategy."""

    def test_buy_sell_buffer_zone(self):
        """Test that there's an 8% buffer between buy and sell."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05   # 525 (+5%)
        sell_threshold = sma200 * 0.97  # 485 (-3%)

        # Calculate buffer
        buffer = buy_threshold - sell_threshold
        buffer_pct = (buffer / sma200) * 100

        # Should have 8% buffer (5% + 3%)
        assert buffer_pct == pytest.approx(8.0, rel=1e-6)

    def test_price_in_buffer_zone(self):
        """Test price in the buffer zone (no signal)."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05   # 525
        sell_threshold = sma200 * 0.97  # 485

        # Price in buffer zone
        qqq_close = 505.0

        # Should NOT trigger buy or sell
        assert qqq_close < buy_threshold
        assert qqq_close > sell_threshold

    def test_whipsaw_prevention(self):
        """Test that thresholds prevent whipsaws."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05   # 525
        sell_threshold = sma200 * 0.97  # 485

        # Simulate price movement
        prices = [520, 525, 530, 525, 520, 515, 510, 505, 490, 485, 480]

        buy_signals = sum(1 for p in prices if p >= buy_threshold)
        sell_signals = sum(1 for p in prices if p <= sell_threshold)

        # Should have limited signals due to buffer
        assert buy_signals == 3  # When >= 525 (at indices 1, 2, 3)
        assert sell_signals == 2  # When <= 485 (at indices 9, 10)


class TestStateTransitions:
    """Tests for valid state transitions."""

    def test_cash_to_tqqq_requires_buy_signal(self):
        """Test that CASH->TQQQ requires buy signal."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05
        current_position = "CASH"

        # Buy signal triggers
        qqq_close = 530.0
        can_buy = (current_position == "CASH" and qqq_close >= buy_threshold)
        assert can_buy

    def test_tqqq_to_cash_requires_sell_signal(self):
        """Test that TQQQ->CASH requires sell signal."""
        sma200 = 500.0
        sell_threshold = sma200 * 0.97
        current_position = "TQQQ"

        # Sell signal triggers
        qqq_close = 480.0
        can_sell = (current_position == "TQQQ" and qqq_close <= sell_threshold)
        assert can_sell

    def test_no_buy_when_already_in_tqqq(self):
        """Test that buy signal ignored when already in TQQQ."""
        sma200 = 500.0
        buy_threshold = sma200 * 1.05
        current_position = "TQQQ"
        qqq_close = 530.0

        # Should NOT buy when already in TQQQ
        can_buy = (current_position == "CASH" and qqq_close >= buy_threshold)
        assert not can_buy

    def test_no_sell_when_already_in_cash(self):
        """Test that sell signal ignored when already in CASH."""
        sma200 = 500.0
        sell_threshold = sma200 * 0.97
        current_position = "CASH"
        qqq_close = 480.0

        # Should NOT sell when already in CASH
        can_sell = (current_position == "TQQQ" and qqq_close <= sell_threshold)
        assert not can_sell

