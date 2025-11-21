#!/usr/bin/env bash
#
# clean-cached-data.sh - Remove cached market data and generated files
#
# This script deletes the data/ folder which contains:
#   - market_data_cache.pkl (cached Yahoo Finance data)
#   - position_state.json (trading position state)
#   - signals_log.csv (trade history log)
#   - tqqq_sma_chart.html (interactive chart)
#
# ⚠️  WARNING: This will delete your trading history and position state!
#

set -e

# Get the project root (parent of scripts directory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -d "data" ]; then
    echo "⚠️  WARNING: This will delete all cached data including:"
    echo "   • Market data cache (will be refetched on next run)"
    echo "   • Trading position state (will reset to CASH)"
    echo "   • Trade history log"
    echo "   • Generated charts"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "🗑️  Removing data/ directory..."
        rm -rf data/
        echo "✅ Cached data deleted!"
        echo ""
        echo "📝 Note: On next run, the script will:"
        echo "   • Refetch market data from Yahoo Finance"
        echo "   • Start with position = CASH"
        echo "   • Create a new trade log"
    else
        echo "❌ Cancelled. No data was deleted."
        exit 1
    fi
else
    echo "ℹ️  No data/ directory found. Nothing to clean."
fi

