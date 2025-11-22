![Tests](https://github.com/ragu-manjegowda/tqqq-sma/workflows/Run%20Tests/badge.svg)
![Daily Signal](https://github.com/ragu-manjegowda/tqqq-sma/workflows/Daily%20TQQQ%20Signal/badge.svg)


# TQQQ 200-Day SMA Trading Signal

A Python script that generates mechanical trading signals for TQQQ (3x leveraged Nasdaq ETF) based on QQQ's 200-day Simple Moving Average (SMA) with threshold-based entry and exit rules.

## ✨ Features

- 🎯 **Mechanical Trading Signals** - Clear BUY/SELL signals based on QQQ's 200-day SMA
- 📊 **ASCII Chart** - Terminal-based visualization of last 6 months
- 🌐 **Interactive HTML Chart** - Fancy 5-year chart with zoom, hover, and more
- 💾 **Smart Caching** - Caches market data for 24 hours to speed up runs
- 📝 **Trade Logging** - Comprehensive CSV log of all signals
- 🔧 **Manual Override** - Easy position synchronization
- 📧 **Email Alerts** - Optional notifications for BUY/SELL signals
- 🎨 **Clean Output** - Beautifully formatted terminal display

## 📊 Trading Algorithm

### What is the 200-Day SMA?

The **200-Day Simple Moving Average (SMA)** is a widely-watched technical indicator that:
- Calculates the average closing price of QQQ over the last 200 trading days
- Acts as a major support/resistance level
- Represents approximately 9 months of trading data
- Helps identify long-term market trends

**Formula**: `(Sum of last 200 daily closing prices) / 200`

The 200-day SMA is considered one of the most important technical indicators by institutional investors and is often used as a dividing line between bull and bear markets.

### Strategy Overview
This is an **all-in/all-out** momentum strategy that:
- Trades TQQQ (3x leveraged QQQ) based on QQQ's 200-day SMA
- Uses asymmetric thresholds (+5%/-3%) to reduce whipsaws
- Maintains state between runs to avoid duplicate signals

### Signal Rules

**BUY Signal (Enter TQQQ)**
- Triggers when: `QQQ Close >= SMA200 × 1.05` (5% above SMA)
- Only when: Current position is CASH
- Action: Go all-in to TQQQ

**SELL Signal (Exit to CASH)**
- Triggers when: `QQQ Close <= SMA200 × 0.97` (3% below SMA)
- Only when: Current position is TQQQ
- Action: Exit to CASH

**Why Asymmetric Thresholds? (The 5/3 Strategy)**
- **+5% Buy Threshold**: Waits for QQQ to be 5% above the 200-day SMA before entering
  - Confirms strong upward momentum
  - Reduces false entries during choppy/sideways markets
  - Helps avoid getting whipsawed in volatile conditions
- **-3% Sell Threshold**: Exits when QQQ drops to 3% below the 200-day SMA
  - Provides earlier protection during downturns
  - Asymmetric (tighter than entry) to preserve gains
  - Allows some wiggle room without exiting on minor dips
- **Buffer Zone**: Creates an 8% gap between entry and exit thresholds
  - Prevents frequent trading from market noise
  - Reduces transaction costs and slippage
  - Maintains position through normal market fluctuations

### What the Script Does
1. Creates `data/` directory if it doesn't exist
2. Checks cache for recent data (24-hour expiry)
3. Fetches QQQ historical data from Yahoo Finance if needed
4. Calculates the 200-day Simple Moving Average
5. Generates interactive HTML chart with 5 years of data
6. Displays ASCII chart in terminal for last 6 months
7. Compares current QQQ price against thresholds
8. Generates BUY/SELL signals based on your current position
9. Logs all trades to `data/signals_log.csv`
10. Maintains position state in `data/position_state.json`

## 🚀 Project Setup

### Prerequisites
- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone or download this project**
```bash
cd /path/to/tqqq-sma
```

2. **Install dependencies**
```bash
uv sync
```

That's it! `uv` will automatically create a virtual environment and install all dependencies (`pandas`, `yfinance`, `plotly`).

## 🏃 How to Run

### Basic Usage
```bash
uv run tqqq-sma
```

Or alternatively:
```bash
uv run src/main.py
```

### When to Run
- **Optimal time**: After US market close (~1:05 PM PT / 4:05 PM ET)
- The script uses daily closing prices, so run it after market hours
- Can be automated via cron (Linux/Mac) or Task Scheduler (Windows)

### What Happens on First Run
1. Fetches market data from Yahoo Finance (~3 seconds)
2. Caches data locally for future runs
3. Generates interactive HTML chart (`tqqq_sma_chart.html`)
4. Displays ASCII chart in terminal
5. Shows current trading signal

### Subsequent Runs
- Uses cached data (instant!)
- Cache refreshes automatically after 24 hours
- Updates all charts and signals

### Automate with Cron
To run automatically every weekday at 1:05 PM PT:
```bash
crontab -e
```

Add this line:
```
5 13 * * 1-5 cd /home/ragu/Downloads/tqqq-sma && /path/to/uv run tqqq-sma
```

### Available Commands

All project commands are available via `uv run`:

| Command | Description |
|---------|-------------|
| `uv run tqqq-sma` | Run the main trading signal script |
| `uv run format` | Format code (strip trailing whitespace) |
| `uv run clean` | Remove build artifacts and caches |
| `uv run clean-data` | Delete data/ folder (with confirmation) |
| `uv run pytest` | Run all unit tests |
| `uv run pytest -v` | Run tests with verbose output |
| `uv run pytest --cov=src` | Run tests with coverage report |

## 📊 Visualizations

### 1. ASCII Chart (Terminal)
Shows last 6 months of data directly in your terminal:

```
Chart: Last 6 Months (QQQ Price, SMA200 & Thresholds)
────────────────────────────────────────────────────────────
                                                  ●●●        │ $635.77
                                                     ● ●●    │ $627.37
                                            ●   ●●    ●      │ $618.97
                                         ●●●  ●●         ●   │ $610.57
                        ●        ●●                          │ $585.37
                      ●● ●● ●●●●●                         ++ │ $576.97
               ●●●●●       ●                      ++++++++   │ $568.57
          ● ●●●     ●●                   +++++++++           │ $560.17
+++++++++++                     ───────────        --------- │ $526.57
└────────────────────────────────────────────────────────────
│        │          │          │         │           │      
2025-06  2025-07    2025-08    2025-09   2025-10     2025-11

Legend: ● QQQ Price  ─ SMA200  + Buy Level (+5%)  - Sell Level (-3%)
```

**Features:**
- QQQ price trend (●)
- SMA200 baseline (─)
- Buy threshold at +5% (+)
- Sell threshold at -3% (-)
- Monthly date markers
- Price scale on right axis

### 2. Interactive HTML Chart (Browser)
Opens `tqqq_sma_chart.html` in your browser with 5 years of data:

**Interactive Features:**
- 🖱️ **Hover tooltips** - See exact price, date, and % vs SMA
- 🔍 **Zoom & Pan** - Click and drag to zoom into specific periods
- 📅 **Range selector** - Quick buttons for 1m, 3m, 6m, 1y, 2y, All
- 🎚️ **Range slider** - Scrub through time at the bottom
- 📸 **Export to PNG** - Download chart as high-res image
- 🎨 **Buffer zone** - Shaded area between buy/sell thresholds
- 🚦 **Signal markers** - Vertical lines showing BUY/SELL points

**Visual Elements:**
- Black line: QQQ Price
- Blue line: SMA200
- Green dotted: Buy Level (+5%)
- Red dotted: Sell Level (-3%)
- Gray shading: Buffer zone (neutral territory)
- Green vertical lines: BUY signals
- Red vertical lines: SELL signals

## 📖 Configuration

### User Settings (in `src/config.py`)

```python
# Trading symbols
QQQ_SYMBOL = "QQQ"
TQQQ_SYMBOL = "TQQQ"

# Strategy parameters
SMA_PERIOD = 200           # Moving average period
BUY_MULTIPLIER = 1.05      # +5% threshold
SELL_MULTIPLIER = 0.97     # -3% threshold

# Manual position override
MANUAL_POSITION = None     # None | "CASH" | "TQQQ"

# Visualization options
PRINT_CHART = True                              # ASCII chart (6 months)
GENERATE_INTERACTIVE_CHART = True               # HTML chart (5 years)
INTERACTIVE_CHART_FILENAME = "data/tqqq_sma_chart.html"

# Cache settings
CACHE_FILE = "data/market_data_cache.pkl"
# Cache expires after market close (4 PM ET / 9 PM UTC)

# Data settings
HISTORY_YEARS = 3          # Years of data for signal generation
```

### Manual Position Override

If you manually trade outside the script, you can sync your position:

```python
# If you manually sold TQQQ:
MANUAL_POSITION = "CASH"

# If you manually bought TQQQ:
MANUAL_POSITION = "TQQQ"

# To use saved state (normal mode):
MANUAL_POSITION = None
```

**How it works:**
1. Set `MANUAL_POSITION` to your actual position
2. Run the script once (it will update the saved state)
3. Change it back to `None`
4. The script now knows your correct position

### Email Alerts (Optional)

To receive email notifications on BUY/SELL signals:

```python
EMAIL_ALERT = {
    "enabled": True,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your.email@gmail.com",
    "password": "your-app-password",
    "from_addr": "your.email@gmail.com",
    "to_addrs": ["your.email@gmail.com"],
}
```

**Gmail Users**: Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

## 📈 Output Example

```
════════════════════════════════════════════════════════════
  TQQQ 200-Day SMA Trading Signal
════════════════════════════════════════════════════════════
Fetching market data...
Using cached data (age: 2h 15m)
Generating interactive chart...
✨ Interactive chart saved to: tqqq_sma_chart.html
   Open in browser to explore with zoom, hover, and more!

Chart: Last 6 Months (QQQ Price, SMA200 & Thresholds)
────────────────────────────────────────────────────────────
[ASCII chart displayed here]
────────────────────────────────────────────────────────────

Date:                    2025-11-20
QQQ Close:               $585.67
SMA200:                  $542.35
QQQ vs SMA200:           +7.99%

BUY Threshold (+5%):     $569.46
SELL Threshold (-3%):    $526.08

Distance to BUY:         -2.77%
Distance to SELL:        -10.18%
────────────────────────────────────────────────────────────
Position:                TQQQ
Last Signal Date:        2025-11-20
────────────────────────────────────────────────────────────

✅ STATUS: Holding TQQQ
   Currently in position, SELL condition not met.
   QQQ is 10.18% above SELL threshold.

────────────────────────────────────────────────────────────
```

## 📁 Project Structure

```
tqqq-sma/
├── src/                         # Source code (modular architecture)
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main entry point & orchestration
│   ├── config.py                # Configuration & constants
│   ├── calculations.py          # SMA & percentage calculations
│   ├── data_fetcher.py          # Yahoo Finance data fetching & caching
│   ├── state_manager.py         # Position state management
│   ├── charts.py                # ASCII & interactive chart generation
│   └── logger.py                # CSV logging & email alerts
├── tests/                       # Comprehensive test suite (72 tests)
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & shared utilities
│   ├── test_calculations.py     # SMA & percentage tests
│   ├── test_data_io.py          # Data fetching & CSV logging tests
│   ├── test_signal_logic.py     # Trading signal logic tests
│   ├── test_data_validation.py  # Edge cases & validation tests
│   └── test_state_management.py # State & cache management tests
├── scripts/                     # Utility scripts
│   ├── clean.sh                 # Clean build artifacts
│   └── clean-cached-data.sh     # Clean data/ folder
├── data/                        # Generated files (gitignored)
│   ├── position_state.json      # Current trading position
│   ├── signals_log.csv          # Historical trade log
│   ├── market_data_cache.pkl    # Cached market data
│   └── tqqq_sma_chart.html      # Interactive chart
├── pyproject.toml               # Project config & dependencies
├── uv.lock                      # Dependency lock file
├── README.md                    # Documentation (this file)
└── .gitignore                   # Git exclusions
```

### Key Files

**Source Modules:**
- `main.py` (265 lines) - Main orchestration and business logic
- `config.py` (45 lines) - All user-configurable settings
- `calculations.py` (64 lines) - Pure calculation functions
- `data_fetcher.py` (194 lines) - Market data with retry & caching
- `state_manager.py` (48 lines) - JSON state persistence
- `charts.py` (380 lines) - ASCII & Plotly visualizations
- `logger.py` (44 lines) - CSV logging & SMTP email alerts

**Utility Scripts:**
- `clean.sh` - Remove build artifacts (__pycache__, *.egg-info, .coverage, etc.)
- `clean-cached-data.sh` - Delete data/ folder (with confirmation)

**Generated Files** (in `data/`, not tracked in git):
- `position_state.json` - Current position (CASH/TQQQ) and last signal date
- `signals_log.csv` - Complete trade history with timestamps
- `market_data_cache.pkl` - Cached Yahoo Finance data (~34KB)
- `tqqq_sma_chart.html` - Interactive 5-year chart (~5MB)

## 🔧 Understanding the Output

| Metric | Description |
|--------|-------------|
| **QQQ Close** | Current QQQ closing price |
| **SMA200** | 200-day Simple Moving Average of QQQ |
| **QQQ vs SMA200** | Percentage difference from SMA (positive = above) |
| **BUY Threshold** | Price level that triggers BUY (SMA × 1.05) |
| **SELL Threshold** | Price level that triggers SELL (SMA × 0.97) |
| **Distance to BUY** | % move needed to reach BUY (negative = already passed) |
| **Distance to SELL** | % move needed to reach SELL (negative = above threshold) |

### Status Icons
- 🟢 **BUY Signal** - Enter TQQQ position
- 🔴 **SELL Signal** - Exit to CASH
- ✅ **Holding TQQQ** - In position, monitoring for exit
- ⏸️ **Waiting** - In CASH, monitoring for entry

## 📊 Trade Log

All signals are logged to `signals_log.csv` with:
- Timestamp (UTC)
- Action (BUY/SELL)
- Position transition (FROM → TO)
- QQQ price and SMA values
- Percentage vs SMA200
- All threshold distances

Example:
```csv
timestamp_utc,action,position_from,position_to,date,qqq_close,sma200,pct_vs_sma,buy_level,sell_level,pct_to_buy,pct_to_sell
2025-11-20T19:10:45.123456,BUY,CASH,TQQQ,2025-11-20,585.67,542.35,7.99,569.46,526.08,-2.77,-10.18
```

## 💾 Data Caching

The script uses **market-close-based caching** to ensure you always get the latest closing prices:

### How It Works
1. **First run (after market close)**: Fetches fresh data from Yahoo Finance, saves to cache
2. **Subsequent runs (same day)**: Uses cached data (instant!)
3. **Auto-refresh**: Cache expires after the next market close (4 PM ET / 9 PM UTC)
4. **Smart updates**: Always gets latest close when available

### Market-Close Logic
- **US Market closes**: 4:00 PM ET (9:00 PM UTC) on weekdays
- **Before market close**: Uses previous day's closing price
- **After market close**: Fetches and uses today's closing price
- **Weekends**: Uses Friday's closing price (cache valid until Monday after close)

### Cache Status
The script shows cache status:
```
Using cached data from today (age: 2h 15m)  ← Cache has today's close
Cache is from before last market close...   ← Fetching fresh data
Fetching market data...                     ← No cache, fetching fresh
```

### Cache Management
- **Location**: `data/market_data_cache.pkl`
- **Size**: ~34KB (compressed)
- **Expiry**: After each market close (4 PM ET daily)
- **Clear cache**: Delete `data/market_data_cache.pkl` to force refresh

### Example Timeline
**Monday:**
- 10:00 AM ET: Uses Friday's close (cache valid)
- 4:05 PM ET: Fetches Monday's close, updates cache
- 6:00 PM ET: Uses Monday's close (cache valid)

**Tuesday:**
- 8:00 AM ET: Uses Monday's close (cache valid)
- 4:05 PM ET: Fetches Tuesday's close, updates cache

This ensures you always get the most recent market close data! 📊

## ⚠️ Risk Disclaimer

**THIS IS NOT FINANCIAL ADVICE**

This script is a mechanical signal generator for educational purposes. Important considerations:

- **Leverage Risk**: TQQQ is a 3x leveraged ETF with significant volatility
- **Decay Risk**: Leveraged ETFs suffer from decay in choppy markets
- **No Guarantees**: Past performance does not guarantee future results
- **Position Sizing**: Use appropriate position sizing for your risk tolerance
- **Tax Implications**: Frequent trading may have tax consequences
- **Market Gaps**: The strategy uses daily closes; gap moves can affect results

**Always:**
- Understand what you're trading
- Use proper risk management
- Never trade with money you can't afford to lose
- Consult a financial advisor for personalized advice

## 🧪 Testing

### Running Tests

The project includes a comprehensive test suite with **72 unit tests** covering core functionality.

**Install test dependencies:**
```bash
uv sync --extra dev
```

**Run all tests:**
```bash
uv run pytest
```

**Run with verbose output:**
```bash
uv run pytest -v
```

**Run with coverage report:**
```bash
uv run pytest --cov=src --cov-report=html
```

**Run specific test file:**
```bash
uv run pytest tests/test_calculations.py
```

**Run specific test:**
```bash
uv run pytest tests/test_signal_logic.py::TestBuySignalLogic::test_buy_signal_triggered
```

### Test Coverage

The test suite includes:
- ✅ **17 tests** for calculations (SMA, percentages, formatting)
- ✅ **16 tests** for data I/O (Yahoo Finance fetching, CSV logging)
- ✅ **16 tests** for data validation and edge cases
- ✅ **15 tests** for signal logic (BUY/SELL conditions, thresholds)
- ✅ **8 tests** for state and cache management

**Test Categories:**
- `test_calculations.py` - SMA computation, percentage calculations, formatting
- `test_data_io.py` - Yahoo Finance data fetching, retry logic, CSV logging
- `test_signal_logic.py` - Trading signal generation, state transitions, thresholds
- `test_data_validation.py` - Edge cases, extreme values, real-world scenarios
- `test_state_management.py` - Position state, market-aware cache expiry

## 🛠️ Development

### Modular Architecture

The codebase is organized into focused, testable modules:

**Core Modules:**
- **config.py** - Centralized configuration (symbols, thresholds, file paths)
- **calculations.py** - Pure functions for SMA and percentage calculations
- **data_fetcher.py** - Data acquisition with retry logic and market-aware caching
- **state_manager.py** - Position state persistence (JSON)
- **charts.py** - Visualization (ASCII terminal + Plotly interactive)
- **logger.py** - Trade logging (CSV) and email notifications (SMTP)
- **main.py** - Orchestration layer tying everything together

**Benefits:**
- ✅ Single Responsibility - Each module has one clear purpose
- ✅ Easy Testing - Pure functions with minimal dependencies
- ✅ Maintainability - Changes isolated to relevant modules
- ✅ Reusability - Modules can be imported independently

### Cleanup Scripts

**Format code** (strip trailing whitespace):
```bash
uv run format
```
Cleans up whitespace in all project files:
- **Python/YAML/TOML files**: Removes all trailing whitespace
- **Markdown files**: Preserves trailing spaces (needed for line breaks), but removes spaces from empty lines

**Remove build artifacts:**
```bash
uv run clean
```
Removes: `__pycache__`, `*.egg-info`, `.coverage`, `.pytest_cache`, build artifacts, linter caches

**Clean cached data** (with confirmation):
```bash
uv run clean-data
```
⚠️ Deletes: `data/` folder (market cache, position state, trade log, charts)

> **Note**: Shell script versions (`./scripts/clean.sh` and `./scripts/clean-cached-data.sh`) are also available.

### Dependencies

**Core:**
- **pandas** (>=2.3.3) - Data manipulation and SMA calculation
- **yfinance** (>=0.2.66) - Free market data from Yahoo Finance
- **plotly** (>=5.24.1) - Interactive chart generation

**Development (optional):**
- **pytest** (>=8.0.0) - Testing framework
- **pytest-cov** (>=4.1.0) - Code coverage reports
- **pytest-mock** (>=3.12.0) - Mocking utilities

### Testing Changes
1. Modify settings in `src/config.py`
2. Run: `uv run tqqq-sma`
3. Check output, logs, and charts in `data/` directory
4. Clear cache if needed: `uv run clean-data` or `rm data/market_data_cache.pkl`
5. Run tests: `uv run pytest -v`
6. Format code: `uv run format` (before committing)
7. Clean build artifacts: `uv run clean` (optional)

### Customization Ideas
- Change SMA period (e.g., 50-day, 100-day)
- Adjust buy/sell thresholds
- Add additional indicators
- Modify chart timeframes
- Customize chart colors and styling

## 🎨 Chart Customization

### ASCII Chart Options
Located in `src/config.py`:
```python
PRINT_CHART = True          # Enable/disable ASCII chart
```

Customize dimensions in `src/charts.py`:
```python
plot_ascii_chart(data, width=60, height=20)  # Adjust dimensions
```

### Interactive Chart Options
Located in `src/config.py`:
```python
GENERATE_INTERACTIVE_CHART = True
INTERACTIVE_CHART_FILENAME = "data/tqqq_sma_chart.html"
```

Customize appearance in `src/charts.py`:
```python
# Inside generate_interactive_chart():
height=700                  # Chart height in pixels
template='plotly_white'     # Color theme
```

Available themes: `plotly`, `plotly_white`, `plotly_dark`, `ggplot2`, `seaborn`, `simple_white`

## 🚀 Performance Tips

1. **Use cache**: Leave `CACHE_EXPIRY_HOURS = 24` to minimize API calls
2. **Disable charts**: Set `PRINT_CHART = False` and `GENERATE_INTERACTIVE_CHART = False` for fastest runs
3. **Reduce history**: Lower `HISTORY_YEARS` if you only need recent signals (minimum 1 year for reliable SMA200)
4. **Cron automation**: Run once per day after market close to minimize API usage

## 🙏 Credits

This strategy is based on the TQQQ 200 SMA +5/-3 strategy discussed in the r/LETFs community:
- **Original Strategy Discussion**: [TQQQ 200SMA 5/3 Strategy Follow-up](https://www.reddit.com/r/LETFs/comments/1mc1mvs/tqqq_200sma_53_strategy_follow_up_with_additional/)

Special thanks to the r/LETFs community for sharing research and insights on leveraged ETF strategies.

## 📝 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to fork and modify for your own use. Some ideas:
- Add different indicators (RSI, MACD, Bollinger Bands)
- Implement backtesting functionality
- Add support for other leveraged ETFs (SQQQ, UPRO, etc.)
- Create a web dashboard for monitoring
- Add SMS/Telegram notifications
- Implement risk metrics (Sharpe ratio, max drawdown)
- Multi-timeframe analysis

## 📚 Additional Resources

- [GitHub Actions Workflows](.github/workflows/README.md) - CI/CD and daily signal automation
- [Backtesting Results](backtesting/README.md) - Historical performance analysis
- [Yahoo Finance API Documentation](https://python-yahoofinance.readthedocs.io/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Understanding Leveraged ETFs](https://www.investopedia.com/terms/l/leveraged-etf.asp)
- [Simple Moving Average Strategy](https://www.investopedia.com/terms/s/sma.asp)

## 🐛 Troubleshooting

### "Cache load error"
- Delete `data/market_data_cache.pkl` and run again

### "Failed to fetch data"
- Check internet connection
- Yahoo Finance might be temporarily down
- Try running again in a few minutes
- **Rate limiting** (especially in GitHub Actions): Check workflow logs and artifacts for details

### Charts not updating
- Delete cache file to force fresh data
- Check that `PRINT_CHART` and `GENERATE_INTERACTIVE_CHART` are `True`

### Position out of sync
- Use `MANUAL_POSITION` to resync with your actual position

---

**Remember**: This is a mechanical system. Markets can be irrational. Always use proper risk management and position sizing appropriate for your situation. Past performance is not indicative of future results.

**Version**: 0.1.0 | **Last Updated**: November 2025
