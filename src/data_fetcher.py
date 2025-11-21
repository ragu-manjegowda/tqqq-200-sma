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


def fetch_data_with_retry(symbol, interval="1d", period="3y", retries=3, initial_delay=2):
    """
    Fetch data from yfinance with retries and exponential backoff.

    Args:
        symbol: ticker symbol
        interval: data interval ("1d", "1h", "30m", etc.)
        period: time period ("3y", "1mo", etc.)
        retries: number of retry attempts (reduced from 5 to 3)
        initial_delay: initial seconds to wait between retries (exponential backoff)

    Returns:
        DataFrame: fetched data with standardized columns
    """
    delay = initial_delay

    for attempt in range(1, retries + 1):
        try:
            # Add a small delay before each request to avoid rate limiting
            if attempt > 1:
                time.sleep(delay)

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
            error_str = str(e).lower()

            # Detect rate limiting
            if "429" in error_str or "rate limit" in error_str or "too many requests" in error_str:
                print(f"[{symbol}] ⚠️  Rate limit detected on attempt {attempt}/{retries}")
                # Use longer delay for rate limits
                delay = min(delay * 3, 60)  # Cap at 60 seconds
            else:
                print(f"[{symbol}] Fetch attempt {attempt}/{retries} failed: {e}")
                delay = min(delay * 2, 30)  # Exponential backoff, cap at 30 seconds

            if attempt < retries:
                print(f"[{symbol}] Retrying in {delay} seconds...")

    print(f"!!! ERROR: Unable to fetch data for {symbol} after {retries} attempts.")
    print(f"           This may be due to rate limiting from GitHub Actions IP addresses.")
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

    # Add delay between different symbol fetches to avoid rate limiting
    # This gives Yahoo Finance a breather between requests
    print(f"[{symbol}] Fetching {years} years of data...")
    time.sleep(1)  # 1 second delay before fetching

    # Fetch fresh data
    # first try daily data (most common)
    df = fetch_data_with_retry(symbol, interval="1d", period=f"{years}y", retries=3)
    if df.empty:
        print(f"[{symbol}] Daily fetch failed. Trying 1h interval fallback...")
        time.sleep(2)  # Longer delay before fallback
        df = fetch_data_with_retry(symbol, interval="1h", period=f"{years}y", retries=2)

    if df.empty:
        print(f"[{symbol}] 1h fallback failed. Trying 30m interval fallback...")
        time.sleep(2)  # Longer delay before fallback
        df = fetch_data_with_retry(symbol, interval="30m", period=f"{years}y", retries=2)

    if df.empty:
        raise RuntimeError(
            f"Failed to fetch any valid data for {symbol}\n"
            f"           Possible rate limiting from Yahoo Finance.\n"
            f"           Try again in a few minutes or check if Yahoo Finance is accessible."
        )

    df = df[["adj_close"]].copy()

    # Save to cache
    if use_cache:
        cached_data = load_cache() or {}
        cached_data[cache_key] = df
        save_cache(cached_data)

    return df

