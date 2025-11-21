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

### Strategy Overview
This is an **all-in/all-out** momentum strategy that:
- Trades TQQQ (3x leveraged QQQ) based on QQQ's 200-day SMA
- Uses asymmetric thresholds to reduce whipsaws
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

**Why Asymmetric Thresholds?**
- The 5% buy threshold reduces false entries during choppy markets
- The 3% sell threshold provides earlier exits during downturns
- Creates a buffer zone to avoid frequent whipsaws

### What the Script Does
1. Checks cache for recent data (24-hour expiry)
2. Fetches QQQ historical data from Yahoo Finance if needed
3. Calculates the 200-day Simple Moving Average
4. Generates interactive HTML chart with 5 years of data
5. Displays ASCII chart in terminal for last 6 months
6. Compares current QQQ price against thresholds
7. Generates BUY/SELL signals based on your current position
8. Logs all trades to `signals_log.csv`
9. Maintains position state in `position_state.json`

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
uv run main.py
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

### User Settings (in `main.py`)

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
PRINT_CHART = True                        # ASCII chart (6 months)
GENERATE_INTERACTIVE_CHART = True         # HTML chart (5 years)
INTERACTIVE_CHART_FILENAME = "tqqq_sma_chart.html"

# Cache settings
CACHE_FILE = "market_data_cache.pkl"
CACHE_EXPIRY_HOURS = 24    # Refresh cache after 24 hours

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

## 📁 Project Files

### Source Files
- `main.py` - Main script with trading logic and visualizations
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Dependency lock file
- `README.md` - This file
- `.gitignore` - Files to exclude from version control

### Generated Files (Not tracked in git)
- `position_state.json` - Stores current position (CASH/TQQQ)
- `signals_log.csv` - Historical log of all BUY/SELL signals
- `market_data_cache.pkl` - Cached market data (24-hour expiry)
- `tqqq_sma_chart.html` - Interactive chart (~5MB)
- `.venv/` - Virtual environment

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

The script caches market data to improve performance:

### How It Works
1. **First run**: Fetches data from Yahoo Finance, saves to cache
2. **Subsequent runs**: Uses cached data (instant!)
3. **Auto-refresh**: Cache expires after 24 hours
4. **Smart updates**: Only fetches when needed

### Cache Status
The script shows cache status:
```
Using cached data (age: 2h 15m)  ← Using cache
Fetching market data...          ← Cache expired or missing
```

### Cache Management
- **Location**: `market_data_cache.pkl`
- **Size**: ~34KB (compressed)
- **Expiry**: 24 hours (configurable)
- **Clear cache**: Delete `market_data_cache.pkl` to force refresh

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

## 🛠️ Development

### Project Structure
```
tqqq-sma/
├── main.py                   # Main trading script
├── pyproject.toml            # Project config
├── uv.lock                   # Dependency versions
├── README.md                 # This file
├── .gitignore                # Git exclusions
├── position_state.json       # Runtime state (generated)
├── signals_log.csv           # Trade log (generated)
├── market_data_cache.pkl     # Data cache (generated)
└── tqqq_sma_chart.html       # Interactive chart (generated)
```

### Dependencies
- **pandas** (>=2.3.3) - Data manipulation and SMA calculation
- **yfinance** (>=0.2.66) - Free market data from Yahoo Finance
- **plotly** (>=5.24.1) - Interactive chart generation

### Testing Changes
1. Modify settings in `main.py`
2. Run: `uv run tqqq-sma`
3. Check output, logs, and charts
4. Clear cache if needed: `rm market_data_cache.pkl`

### Customization Ideas
- Change SMA period (e.g., 50-day, 100-day)
- Adjust buy/sell thresholds
- Add additional indicators
- Modify chart timeframes
- Customize chart colors and styling

## 🎨 Chart Customization

### ASCII Chart Options
Located in `main.py`:
```python
PRINT_CHART = True          # Enable/disable ASCII chart
plot_ascii_chart(data, width=60, height=20)  # Adjust dimensions
```

### Interactive Chart Options
```python
GENERATE_INTERACTIVE_CHART = True
INTERACTIVE_CHART_FILENAME = "tqqq_sma_chart.html"

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

- [Yahoo Finance API Documentation](https://python-yahoofinance.readthedocs.io/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Understanding Leveraged ETFs](https://www.investopedia.com/terms/l/leveraged-etf.asp)
- [Simple Moving Average Strategy](https://www.investopedia.com/terms/s/sma.asp)

## 🐛 Troubleshooting

### "Cache load error"
- Delete `market_data_cache.pkl` and run again

### "Failed to fetch data"
- Check internet connection
- Yahoo Finance might be temporarily down
- Try running again in a few minutes

### Charts not updating
- Delete cache file to force fresh data
- Check that `PRINT_CHART` and `GENERATE_INTERACTIVE_CHART` are `True`

### Position out of sync
- Use `MANUAL_POSITION` to resync with your actual position

---

**Remember**: This is a mechanical system. Markets can be irrational. Always use proper risk management and position sizing appropriate for your situation. Past performance is not indicative of future results.

**Version**: 0.1.0 | **Last Updated**: November 2025
