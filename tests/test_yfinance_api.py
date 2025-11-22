#!/usr/bin/env python3
"""
Integration test to verify yfinance API is accessible AND pre-fetch data for main script.

This is a smoke test that:
1. Makes a REAL API call to verify API is accessible
2. Fetches the actual data needed by main script (QQQ + TQQQ)
3. Saves to cache so main script doesn't need to fetch again

This eliminates duplicate API calls in the workflow.
"""
import sys
import os
import warnings

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import fetch_adj_close
from src.config import QQQ_SYMBOL, TQQQ_SYMBOL, HISTORY_YEARS

# Suppress yfinance FutureWarnings
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')


def test_yfinance_api():
    """Test that yfinance API is accessible and pre-fetch data."""
    print("🔍 Testing Yahoo Finance API connectivity...")
    print(f"   Fetching {HISTORY_YEARS} years of market data...")
    print()

    try:
        # Fetch QQQ data (this will cache it)
        print(f"   📊 Fetching {QQQ_SYMBOL} data...")
        qqq_data = fetch_adj_close(QQQ_SYMBOL, HISTORY_YEARS, use_cache=True)

        if qqq_data.empty:
            print(f"   ❌ ERROR: No data returned for {QQQ_SYMBOL}")
            return False

        print(f"      ✓ Got {len(qqq_data)} days of {QQQ_SYMBOL} data")
        print(f"      ✓ Latest: {qqq_data.index[-1].strftime('%Y-%m-%d')}")

        # Fetch TQQQ data (this will cache it)
        print(f"   📊 Fetching {TQQQ_SYMBOL} data...")
        tqqq_data = fetch_adj_close(TQQQ_SYMBOL, HISTORY_YEARS, use_cache=True)

        if tqqq_data.empty:
            print(f"   ❌ ERROR: No data returned for {TQQQ_SYMBOL}")
            return False

        print(f"      ✓ Got {len(tqqq_data)} days of {TQQQ_SYMBOL} data")
        print(f"      ✓ Latest: {tqqq_data.index[-1].strftime('%Y-%m-%d')}")

        # Fetch 5 years for chart (this will also cache it)
        print(f"   📊 Fetching {QQQ_SYMBOL} 5-year data for chart...")
        qqq_5y = fetch_adj_close(QQQ_SYMBOL, 5, use_cache=True)

        if qqq_5y.empty:
            print(f"   ❌ ERROR: No 5-year data returned for {QQQ_SYMBOL}")
            return False

        print(f"      ✓ Got {len(qqq_5y)} days of 5-year data")

        print()
        print("✅ API test passed!")
        print(f"   📁 Data cached - main script will use cached data")
        print(f"   ⚡ No additional API calls needed")
        return True

    except Exception as e:
        print(f"❌ ERROR: Failed to fetch data from yfinance")
        print(f"   Exception: {e}")
        print()
        print("   Possible causes:")
        print("   - Yahoo Finance API is down")
        print("   - Network connectivity issue")
        print("   - Rate limiting (429 error)")
        print("   - Market holiday (no recent data)")
        return False


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    print("=" * 70)
    print("  Yahoo Finance API Health Check + Data Pre-fetch")
    print("=" * 70)
    print()

    success = test_yfinance_api()

    print()
    print("=" * 70)

    if success:
        print("✅ API health check PASSED - proceeding with workflow")
        print("   Main script will use cached data (no additional API calls)")
        sys.exit(0)
    else:
        print("❌ API health check FAILED - workflow will fail")
        print()
        print("Recommendation: Wait a few minutes and try again")
        sys.exit(1)
