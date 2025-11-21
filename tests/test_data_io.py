"""
Tests for data fetching and CSV logging functionality.
"""
import pytest
import pandas as pd
import csv
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import data_fetcher, logger, config


class TestYahooFinanceDataFetching:
    """Test Yahoo Finance data fetching."""
    
    def test_fetch_adj_close_success(self, monkeypatch, tmp_path):
        """Test successful data fetch from Yahoo Finance."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(config, 'CACHE_FILE', cache_file)
        
        # Mock the fetch_data_with_retry function
        mock_data = pd.DataFrame({
            'adj_close': [100.0, 101.0, 102.0, 103.0, 104.0],
            'close': [99.5, 100.5, 101.5, 102.5, 103.5]
        }, index=pd.date_range('2024-01-01', periods=5, freq='D'))
        
        def mock_fetch(*args, **kwargs):
            return mock_data
        
        monkeypatch.setattr(data_fetcher, 'fetch_data_with_retry', mock_fetch)
        
        result = data_fetcher.fetch_adj_close('TEST', 3, use_cache=False)
        
        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert 'adj_close' in result.columns
        assert result['adj_close'].iloc[0] == 100.0
        assert result['adj_close'].iloc[-1] == 104.0
    
    def test_fetch_adj_close_with_cache_hit(self, monkeypatch, tmp_path):
        """Test fetch with cache hit."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(config, 'CACHE_FILE', cache_file)
        
        # Prepare cached data
        cached_df = pd.DataFrame({'adj_close': [100.0, 101.0, 102.0]})
        cache_data = {
            'TEST_3y': cached_df
        }
        
        # Mock load_cache to return cached data
        monkeypatch.setattr(data_fetcher, 'load_cache', lambda: cache_data)
        
        # Mock fetch_data_with_retry (should not be called)
        fetch_called = [False]
        def mock_fetch(*args, **kwargs):
            fetch_called[0] = True
            return pd.DataFrame()
        
        monkeypatch.setattr(data_fetcher, 'fetch_data_with_retry', mock_fetch)
        
        result = data_fetcher.fetch_adj_close('TEST', 3, use_cache=True)
        
        # Verify fetch was NOT called (cache hit)
        assert not fetch_called[0]
        
        # Verify cached data was returned
        assert result.equals(cached_df)
    
    def test_fetch_adj_close_with_cache_miss(self, monkeypatch, tmp_path):
        """Test fetch with cache miss (stale or no cache)."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(config, 'CACHE_FILE', cache_file)
        
        # Mock load_cache to return None (cache miss)
        monkeypatch.setattr(data_fetcher, 'load_cache', lambda: None)
        
        # Mock fetch_data_with_retry
        mock_data = pd.DataFrame({
            'adj_close': [100.0, 101.0, 102.0],
            'close': [99.0, 100.0, 101.0]
        }, index=pd.date_range('2024-01-01', periods=3, freq='D'))
        
        def mock_fetch(*args, **kwargs):
            return mock_data
        
        monkeypatch.setattr(data_fetcher, 'fetch_data_with_retry', mock_fetch)
        
        # Mock save_cache to track if it was called
        save_cache_called = []
        def mock_save_cache(data):
            save_cache_called.append(data)
        
        monkeypatch.setattr(data_fetcher, 'save_cache', mock_save_cache)
        
        result = data_fetcher.fetch_adj_close('TEST', 3, use_cache=True)
        
        # Verify data was fetched
        assert len(result) == 3
        assert 'adj_close' in result.columns
        
        # Verify cache was saved
        assert len(save_cache_called) == 1
        assert 'TEST_3y' in save_cache_called[0]
    
    def test_fetch_adj_close_empty_data_raises_error(self, monkeypatch, tmp_path):
        """Test handling of empty data from Yahoo Finance."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(config, 'CACHE_FILE', cache_file)
        monkeypatch.setattr(data_fetcher, 'load_cache', lambda: None)
        
        # Mock fetch_data_with_retry to return empty DataFrame
        def mock_fetch(*args, **kwargs):
            return pd.DataFrame()
        
        monkeypatch.setattr(data_fetcher, 'fetch_data_with_retry', mock_fetch)
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Failed to fetch any valid data"):
            data_fetcher.fetch_adj_close('INVALID', 3, use_cache=False)
    
    def test_fetch_data_with_retry_success(self, monkeypatch):
        """Test fetch_data_with_retry with successful response."""
        # Mock yfinance download
        mock_data = pd.DataFrame({
            'Adj Close': [100.0, 101.0, 102.0],
            'Close': [99.5, 100.5, 101.5]
        }, index=pd.date_range('2024-01-01', periods=3, freq='D'))
        
        with patch('yfinance.download') as mock_download:
            mock_download.return_value = mock_data
            
            result = data_fetcher.fetch_data_with_retry('TEST', interval='1d', period='3y', retries=1, delay=0)
            
            # Verify result is properly formatted
            assert isinstance(result, pd.DataFrame)
            assert 'adj_close' in result.columns
            assert 'close' in result.columns
            assert len(result) == 3
    
    def test_fetch_data_with_retry_empty_response(self, monkeypatch):
        """Test fetch_data_with_retry with empty response."""
        # Mock yfinance to return empty DataFrame
        with patch('yfinance.download') as mock_download:
            mock_download.return_value = pd.DataFrame()
            
            result = data_fetcher.fetch_data_with_retry('INVALID', interval='1d', period='3y', retries=1, delay=0)
            
            # Should return empty DataFrame
            assert isinstance(result, pd.DataFrame)
            assert result.empty
    
    def test_fetch_data_with_retry_network_error(self, monkeypatch):
        """Test fetch_data_with_retry handles network errors."""
        # Mock yfinance to raise exception
        with patch('yfinance.download') as mock_download:
            mock_download.side_effect = Exception("Network error")
            
            result = data_fetcher.fetch_data_with_retry('TEST', interval='1d', period='3y', retries=2, delay=0)
            
            # Should return empty DataFrame after retries
            assert isinstance(result, pd.DataFrame)
            assert result.empty
    
    def test_fetch_multiple_symbols(self, monkeypatch, tmp_path):
        """Test fetching data for multiple symbols."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(config, 'CACHE_FILE', cache_file)
        monkeypatch.setattr(data_fetcher, 'load_cache', lambda: None)
        
        call_count = {'QQQ': 0, 'TQQQ': 0}
        
        def mock_fetch(symbol, **kwargs):
            call_count[symbol] = call_count.get(symbol, 0) + 1
            if symbol == 'QQQ':
                return pd.DataFrame({
                    'adj_close': [400.0, 401.0, 402.0],
                    'close': [399.0, 400.0, 401.0]
                })
            elif symbol == 'TQQQ':
                return pd.DataFrame({
                    'adj_close': [50.0, 51.0, 52.0],
                    'close': [49.5, 50.5, 51.5]
                })
            return pd.DataFrame()
        
        monkeypatch.setattr(data_fetcher, 'fetch_data_with_retry', mock_fetch)
        monkeypatch.setattr(data_fetcher, 'save_cache', lambda x: None)
        
        qqq_result = data_fetcher.fetch_adj_close('QQQ', 3, use_cache=False)
        tqqq_result = data_fetcher.fetch_adj_close('TQQQ', 5, use_cache=False)
        
        assert len(qqq_result) == 3
        assert len(tqqq_result) == 3
        assert qqq_result['adj_close'].iloc[0] == 400.0
        assert tqqq_result['adj_close'].iloc[0] == 50.0


class TestCSVLogging:
    """Test CSV signal logging functionality."""
    
    def test_append_signal_log_new_file(self, monkeypatch, tmp_path):
        """Test logging signal to new CSV file."""
        log_file = str(tmp_path / "test_signals.csv")
        monkeypatch.setattr(config, 'SIGNAL_LOG_CSV', log_file)
        
        # Log a row
        row = {
            'date': '2024-01-15',
            'action': 'BUY',
            'qqq_close': 420.50,
            'sma200': 400.00,
            'tqqq_close': 52.30,
            'pct_vs_sma': 5.125,
            'position': 'TQQQ'
        }
        
        logger.append_signal_log(row)
        
        # Verify file was created
        assert tmp_path.joinpath("test_signals.csv").exists()
        
        # Read and verify contents
        df = pd.read_csv(log_file)
        assert len(df) == 1
        assert df['action'].iloc[0] == 'BUY'
        assert df['qqq_close'].iloc[0] == 420.50
        assert df['sma200'].iloc[0] == 400.00
    
    def test_append_signal_log_append_to_existing(self, monkeypatch, tmp_path):
        """Test appending signal to existing CSV file."""
        log_file = str(tmp_path / "test_signals.csv")
        monkeypatch.setattr(config, 'SIGNAL_LOG_CSV', log_file)
        
        # Log first row
        row1 = {
            'date': '2024-01-15',
            'action': 'BUY',
            'qqq_close': 420.00,
            'sma200': 400.00,
            'tqqq_close': 52.00,
            'pct_vs_sma': 5.0,
            'position': 'TQQQ'
        }
        logger.append_signal_log(row1)
        
        # Log second row
        row2 = {
            'date': '2024-01-20',
            'action': 'SELL',
            'qqq_close': 388.00,
            'sma200': 400.00,
            'tqqq_close': 48.00,
            'pct_vs_sma': -3.0,
            'position': 'CASH'
        }
        logger.append_signal_log(row2)
        
        # Read and verify contents
        df = pd.read_csv(log_file)
        assert len(df) == 2
        assert df['action'].iloc[0] == 'BUY'
        assert df['action'].iloc[1] == 'SELL'
    
    def test_append_signal_log_csv_headers(self, monkeypatch, tmp_path):
        """Test CSV file has correct headers."""
        log_file = str(tmp_path / "test_signals.csv")
        monkeypatch.setattr(config, 'SIGNAL_LOG_CSV', log_file)
        
        row = {
            'date': '2024-01-15',
            'action': 'BUY',
            'qqq_close': 420.00,
            'sma200': 400.00,
            'tqqq_close': 52.00,
            'pct_vs_sma': 5.0,
            'position': 'TQQQ'
        }
        logger.append_signal_log(row)
        
        # Read headers
        with open(log_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Verify key columns exist
            assert 'date' in headers
            assert 'action' in headers
            assert 'qqq_close' in headers
            assert 'sma200' in headers
            assert 'tqqq_close' in headers
            assert 'pct_vs_sma' in headers
            assert 'position' in headers
    
    def test_append_signal_log_multiple_sessions(self, monkeypatch, tmp_path):
        """Test logging across multiple sessions (file persistence)."""
        log_file = str(tmp_path / "test_signals.csv")
        monkeypatch.setattr(config, 'SIGNAL_LOG_CSV', log_file)
        
        # Session 1: Log BUY
        row1 = {'date': '2024-01-15', 'action': 'BUY', 'qqq_close': 420.00, 'sma200': 400.00, 'tqqq_close': 52.00, 'pct_vs_sma': 5.0, 'position': 'TQQQ'}
        logger.append_signal_log(row1)
        
        # Session 2: Log HOLD
        row2 = {'date': '2024-01-16', 'action': 'HOLD', 'qqq_close': 415.00, 'sma200': 400.00, 'tqqq_close': 51.50, 'pct_vs_sma': 3.75, 'position': 'TQQQ'}
        logger.append_signal_log(row2)
        
        # Session 3: Log SELL
        row3 = {'date': '2024-01-17', 'action': 'SELL', 'qqq_close': 388.00, 'sma200': 400.00, 'tqqq_close': 48.00, 'pct_vs_sma': -3.0, 'position': 'CASH'}
        logger.append_signal_log(row3)
        
        df = pd.read_csv(log_file)
        assert len(df) == 3
        assert df['action'].iloc[0] == 'BUY'
        assert df['action'].iloc[1] == 'HOLD'
        assert df['action'].iloc[2] == 'SELL'
    
    def test_append_signal_log_precision(self, monkeypatch, tmp_path):
        """Test price and percentage precision in logs."""
        log_file = str(tmp_path / "test_signals.csv")
        monkeypatch.setattr(config, 'SIGNAL_LOG_CSV', log_file)
        
        row = {
            'date': '2024-01-15',
            'action': 'BUY',
            'qqq_close': 420.123456,
            'sma200': 400.987654,
            'tqqq_close': 52.666666,
            'pct_vs_sma': 5.123456789,
            'position': 'TQQQ'
        }
        logger.append_signal_log(row)
        
        df = pd.read_csv(log_file)
        # Values should be stored as provided (pandas maintains precision)
        assert abs(df['qqq_close'].iloc[0] - 420.123456) < 0.0001
        assert abs(df['pct_vs_sma'].iloc[0] - 5.123456789) < 0.0001
    
    def test_append_signal_log_negative_percentage(self, monkeypatch, tmp_path):
        """Test logging with negative percentage."""
        log_file = str(tmp_path / "test_signals.csv")
        monkeypatch.setattr(config, 'SIGNAL_LOG_CSV', log_file)
        
        row = {
            'date': '2024-01-15',
            'action': 'SELL',
            'qqq_close': 385.00,
            'sma200': 400.00,
            'tqqq_close': 47.50,
            'pct_vs_sma': -3.75,
            'position': 'CASH'
        }
        logger.append_signal_log(row)
        
        df = pd.read_csv(log_file)
        assert len(df) == 1
        assert df['pct_vs_sma'].iloc[0] == -3.75


class TestDataIntegration:
    """Integration tests for data fetching and caching."""
    
    def test_fetch_and_cache_workflow(self, monkeypatch, tmp_path):
        """Test complete workflow of fetch, cache, and retrieve."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(config, 'CACHE_FILE', cache_file)
        
        # Mock fetch_data_with_retry
        mock_data = pd.DataFrame({
            'adj_close': [100.0, 101.0, 102.0],
            'close': [99.0, 100.0, 101.0]
        }, index=pd.date_range('2024-01-01', periods=3, freq='D'))
        
        call_count = [0]
        def mock_fetch(*args, **kwargs):
            call_count[0] += 1
            return mock_data.copy()
        
        monkeypatch.setattr(data_fetcher, 'fetch_data_with_retry', mock_fetch)
        
        # First call: fetch from source and cache
        result1 = data_fetcher.fetch_adj_close('QQQ', 3, use_cache=True)
        assert call_count[0] == 1
        assert len(result1) == 3
        
        # Verify cache file was created
        assert tmp_path.joinpath("cache.pkl").exists()
        
        # Second call: should use cache (no new fetch)
        result2 = data_fetcher.fetch_adj_close('QQQ', 3, use_cache=True)
        assert call_count[0] == 1  # No additional fetch
        assert len(result2) == 3
        
        # Verify both results are equivalent
        assert result1.equals(result2)
    
    def test_cache_invalidation(self, monkeypatch, tmp_path):
        """Test cache can be bypassed when needed."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(config, 'CACHE_FILE', cache_file)
        
        mock_data = pd.DataFrame({
            'adj_close': [100.0, 101.0],
            'close': [99.0, 100.0]
        })
        
        call_count = [0]
        def mock_fetch(*args, **kwargs):
            call_count[0] += 1
            return mock_data.copy()
        
        monkeypatch.setattr(data_fetcher, 'fetch_data_with_retry', mock_fetch)
        
        # Fetch with cache
        result1 = data_fetcher.fetch_adj_close('TEST', 3, use_cache=True)
        assert call_count[0] == 1
        
        # Fetch without cache (should fetch again)
        result2 = data_fetcher.fetch_adj_close('TEST', 3, use_cache=False)
        assert call_count[0] == 2
