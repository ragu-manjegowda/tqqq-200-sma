"""
Market data fetching with caching and retry logic.
"""
import os
import pickle
import time
from datetime import datetime, timezone, timedelta
import pandas as pd
import yfinance as yf

from . import config


def get_last_market_close():
    """
    Get the timestamp of the last market close (4 PM ET / 9 PM UTC).
    
    Returns:
        datetime: timestamp of last market close
    """
    now_utc = datetime.now(timezone.utc)
    
    # Market close is at 4 PM ET = 9 PM UTC (21:00)
    # Adjust for today or yesterday based on current time
    today_close = now_utc.replace(hour=21, minute=0, second=0, microsecond=0)
    
    # If it's currently before 9 PM UTC, use yesterday's close
    if now_utc.hour < 21:
        today_close = today_close - timedelta(days=1)
    
    # Handle weekends - go back to Friday's close
    # Monday=0, Sunday=6
    while today_close.weekday() >= 5:  # Saturday=5, Sunday=6
        today_close = today_close - timedelta(days=1)
    
    return today_close


def load_cache():
    """
    Load cached market data if available and not expired (based on market close).
    
    Returns:
        dict: cached data or None if cache is invalid/expired
    """
    if not os.path.exists(config.CACHE_FILE):
        return None
    
    try:
        with open(config.CACHE_FILE, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Check if cache is expired based on market close time
        cache_time = cache_data.get('timestamp')
        if cache_time:
            last_market_close = get_last_market_close()
            
            # Cache is valid only if it was created AFTER the last market close
            if cache_time >= last_market_close:
                age = datetime.now(timezone.utc) - cache_time
                print(f"Using cached data from today (age: {age.seconds // 3600}h {(age.seconds % 3600) // 60}m)")
                return cache_data.get('data')
            else:
                print(f"Cache is from before last market close, fetching fresh data...")
                return None
        
        return None
    except Exception as e:
        print(f"Cache load error: {e}, fetching fresh data...")
        return None


def save_cache(data):
    """
    Save market data to cache.
    
    Args:
        data: dictionary of market data to cache
    """
    try:
        cache_data = {
            'timestamp': datetime.now(timezone.utc),
            'data': data
        }
        with open(config.CACHE_FILE, 'wb') as f:
            pickle.dump(cache_data, f)
        print("Market data cached successfully")
    except Exception as e:
        print(f"Cache save error: {e}")


def fetch_data_with_retry(symbol, interval="1d", period="3y", retries=5, delay=2):
    """
    Fetch data from yfinance with retries and basic fallback logic.
    
    Args:
        symbol: ticker symbol
        interval: data interval ("1d", "1h", "30m", etc.)
        period: time period ("3y", "1mo", etc.)
        retries: number of retry attempts
        delay: seconds to wait between retries
        
    Returns:
        DataFrame: fetched data with standardized columns
    """
    for attempt in range(1, retries + 1):
        try:
            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=False,
                prepost=False,
                threads=False,
            )
            if not df.empty:
                # Ensure standardized output
                df = df.rename(columns={
                    "Adj Close": "adj_close",
                    "Close": "close"
                })
                df.index = pd.to_datetime(df.index)
                return df
        except Exception as e:
            print(f"[{symbol}] Fetch attempt {attempt}/{retries} failed: {e}")

        time.sleep(delay)
        print(f"[{symbol}] Retrying in {delay} seconds...")

    print(f"!!! ERROR: Unable to fetch data for {symbol} after {retries} attempts.")
    return pd.DataFrame()  # return empty to catch downstream


def fetch_adj_close(symbol, years, use_cache=True):
    """
    Fetch adjusted close data with optional caching.
    
    Args:
        symbol: ticker symbol
        years: number of years of historical data
        use_cache: whether to use cached data
        
    Returns:
        DataFrame: adjusted close prices
        
    Raises:
        RuntimeError: if data fetch fails
    """
    cache_key = f"{symbol}_{years}y"
    
    # Try to load from cache first
    if use_cache:
        cached_data = load_cache()
        if cached_data and cache_key in cached_data:
            return cached_data[cache_key]
    
    # Fetch fresh data
    # first try daily data
    df = fetch_data_with_retry(symbol, interval="1d", period=f"{years}y")
    if df.empty:
        print(f"[{symbol}] Daily fetch failed. Trying 1h interval fallback...")
        df = fetch_data_with_retry(symbol, interval="1h", period=f"{years}y")

    if df.empty:
        print(f"[{symbol}] 1h fallback failed. Trying 30m interval fallback...")
        df = fetch_data_with_retry(symbol, interval="30m", period=f"{years}y")

    if df.empty:
        raise RuntimeError(f"Failed to fetch any valid data for {symbol}")

    df = df[["adj_close"]].copy()
    
    # Save to cache
    if use_cache:
        cached_data = load_cache() or {}
        cached_data[cache_key] = df
        save_cache(cached_data)
    
    return df

