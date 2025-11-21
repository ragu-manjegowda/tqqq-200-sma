"""
Configuration and constants for the TQQQ SMA trading system.
"""

# ========== TRADING PARAMETERS ==========
QQQ_SYMBOL = "QQQ"
TQQQ_SYMBOL = "TQQQ"

SMA_PERIOD = 200
BUY_MULTIPLIER = 1.05   # +5% vs sma200
SELL_MULTIPLIER = 0.97  # -3% vs sma200

# Manual position override - Set this to override the saved position state
# Options: "CASH", "TQQQ", or None (to use saved state from position_state.json)
# Example: If you manually sold TQQQ, set MANUAL_POSITION = "CASH"
#          If you manually bought TQQQ, set MANUAL_POSITION = "TQQQ"
#          If you want to use the saved state, set MANUAL_POSITION = None
MANUAL_POSITION = None

# ========== FILE PATHS ==========
DATA_DIR = "data"
STATE_FILE = "data/position_state.json"
SIGNAL_LOG_CSV = "data/signals_log.csv"
CACHE_FILE = "data/market_data_cache.pkl"
INTERACTIVE_CHART_FILENAME = "data/tqqq_sma_chart.html"

# ========== DATA FETCHING ==========
HISTORY_YEARS = 3       # years of data to fetch for reliable SMA
                        # Note: Actual fetch is 5 years (for chart) but signals use 3 years
                        # This reduces API calls. If rate limiting occurs, the cache
                        # file persists data between runs in GitHub Actions.
# Cache expires after market close (4 PM ET / 9 PM UTC)
# Cache file is reused in GitHub Actions to minimize Yahoo Finance API calls

# ========== VISUALIZATION ==========
# Whether to print ASCII chart of last 6 months with buy/sell levels
PRINT_CHART = True

# Whether to generate interactive HTML chart (5 years of data)
GENERATE_INTERACTIVE_CHART = True

# ========== EMAIL ALERTS ==========
# Optional email alert config -- set enabled=True and fill your SMTP values if you want emails
EMAIL_ALERT = {
    "enabled": False,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your.email@example.com",
    "password": "your-app-password-or-smtp-password",
    "from_addr": "your.email@example.com",
    "to_addrs": ["your.email@example.com"],
}

