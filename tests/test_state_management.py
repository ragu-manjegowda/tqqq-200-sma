"""Tests for state management (load/save state, cache)."""
import pytest
import json
import pickle
import os
from datetime import datetime, timezone, timedelta
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import main


class TestStateManagement:
    """Tests for position state management."""
    
    def test_load_state_new_file(self, monkeypatch, tmp_path):
        """Test loading state when file doesn't exist."""
        state_file = str(tmp_path / "position_state.json")
        monkeypatch.setattr(main, 'STATE_FILE', state_file)
        
        state = main.load_state()
        assert state['position'] == 'CASH'
        assert state['last_signal_date'] is None
        assert 'created' in state
    
    def test_save_and_load_state(self, monkeypatch, tmp_path):
        """Test saving and loading state."""
        state_file = str(tmp_path / "position_state.json")
        monkeypatch.setattr(main, 'STATE_FILE', state_file)
        
        # Save state
        test_state = {
            'position': 'TQQQ',
            'last_signal_date': '2025-11-20',
            'created': datetime.now(timezone.utc).isoformat()
        }
        main.save_state(test_state)
        
        # Verify file exists
        assert os.path.exists(state_file)
        
        # Load and verify
        loaded_state = main.load_state()
        assert loaded_state['position'] == 'TQQQ'
        assert loaded_state['last_signal_date'] == '2025-11-20'
    
    def test_load_corrupted_state(self, monkeypatch, tmp_path):
        """Test loading corrupted state file."""
        state_file = str(tmp_path / "position_state.json")
        monkeypatch.setattr(main, 'STATE_FILE', state_file)
        
        # Create corrupted file
        with open(state_file, 'w') as f:
            f.write("not valid json {")
        
        # Should return default state
        state = main.load_state()
        assert state['position'] == 'CASH'
        assert state['last_signal_date'] is None


class TestCacheManagement:
    """Tests for market data cache management."""
    
    def test_save_and_load_cache(self, monkeypatch, tmp_path):
        """Test saving and loading cache."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(main, 'CACHE_FILE', cache_file)
        
        # Save cache
        test_data = {'QQQ_3y': {'some': 'data'}}
        main.save_cache(test_data)
        
        # Load and verify
        loaded_cache = main.load_cache()
        assert loaded_cache == test_data
    
    def test_cache_expiry(self, monkeypatch, tmp_path):
        """Test cache expiry based on market close."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(main, 'CACHE_FILE', cache_file)
        
        # Save old cache (before last market close)
        old_time = datetime.now(timezone.utc) - timedelta(days=2)
        cache_data = {
            'timestamp': old_time,
            'data': {'QQQ_3y': {'some': 'data'}}
        }
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        # Mock get_last_market_close to return yesterday's close
        mock_last_close = datetime.now(timezone.utc) - timedelta(days=1)
        monkeypatch.setattr(main, 'get_last_market_close', lambda: mock_last_close)
        
        # Should return None (expired - cache is older than last market close)
        loaded_cache = main.load_cache()
        assert loaded_cache is None
    
    def test_cache_not_expired(self, monkeypatch, tmp_path):
        """Test cache not expired (newer than last market close)."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(main, 'CACHE_FILE', cache_file)
        
        # Save recent cache (after last market close)
        recent_time = datetime.now(timezone.utc)
        cache_data = {
            'timestamp': recent_time,
            'data': {'QQQ_3y': {'test': 'data'}}
        }
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        # Mock get_last_market_close to return a time before the cache
        mock_last_close = datetime.now(timezone.utc) - timedelta(hours=2)
        monkeypatch.setattr(main, 'get_last_market_close', lambda: mock_last_close)
        
        # Should return data (cache is newer than last market close)
        loaded_cache = main.load_cache()
        assert loaded_cache == {'QQQ_3y': {'test': 'data'}}
    
    def test_load_cache_no_file(self, monkeypatch, tmp_path):
        """Test loading cache when file doesn't exist."""
        cache_file = str(tmp_path / "nonexistent.pkl")
        monkeypatch.setattr(main, 'CACHE_FILE', cache_file)
        
        result = main.load_cache()
        assert result is None
    
    def test_load_cache_corrupted(self, monkeypatch, tmp_path):
        """Test loading corrupted cache file."""
        cache_file = str(tmp_path / "cache.pkl")
        monkeypatch.setattr(main, 'CACHE_FILE', cache_file)
        
        # Create corrupted file
        with open(cache_file, 'wb') as f:
            f.write(b"corrupted data")
        
        result = main.load_cache()
        assert result is None

