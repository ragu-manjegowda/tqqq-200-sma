#!/usr/bin/env python3
"""
Clean cached market data and generated files.

Removes the data/ folder which contains:
  - market_data_cache.pkl (cached Yahoo Finance data)
  - position_state.json (trading position state)
  - signals_log.csv (trade history log)
  - tqqq_sma_chart.html (interactive chart)

⚠️  WARNING: This will delete your trading history and position state!
"""
import os
import sys
import shutil
from pathlib import Path


def main():
    """Main entry point for the clean-data script."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    if not data_dir.exists():
        print("ℹ️  No data/ directory found. Nothing to clean.")
        return 0

    print("⚠️  WARNING: This will delete all cached data including:")
    print("   • Market data cache (will be refetched on next run)")
    print("   • Trading position state (will reset to CASH)")
    print("   • Trade history log")
    print("   • Generated charts")
    print()

    # Get confirmation
    try:
        response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n❌ Cancelled. No data was deleted.")
        return 1

    print()

    if response in ('yes', 'y'):
        try:
            print("🗑️  Removing data/ directory...")
            shutil.rmtree(data_dir)
            print("✅ Cached data deleted!")
            print()
            print("📝 Note: On next run, the script will:")
            print("   • Refetch market data from Yahoo Finance")
            print("   • Start with position = CASH")
            print("   • Create a new trade log")
            return 0
        except Exception as e:
            print(f"❌ Error deleting data directory: {e}")
            return 1
    else:
        print("❌ Cancelled. No data was deleted.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

