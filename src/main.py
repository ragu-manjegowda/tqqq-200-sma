#!/usr/bin/env python3
"""
tqqq-sma

All-in / All-out TQQQ trading signal based on QQQ 200-day SMA with +5% buy / -3% sell thresholds.

Behavior:
 - You start in CASH (or whatever position is stored in position_state.json).
 - BUY only triggers when position == "CASH" AND QQQ_close >= SMA200 * BUY_MULTIPLIER.
   That first BUY flips the state to "TQQQ" and logs the trade.
 - SELL only triggers when position == "TQQQ" AND QQQ_close <= SMA200 * SELL_MULTIPLIER.
 - While position == "TQQQ", BUY signals are ignored (explicit "already in buy mode" behavior).
 - While position == "CASH", SELL signals are ignored (can't sell when you're already out).
 - Each run prints a friendly summary and percent distances to thresholds.
 - When a transition happens, the script appends a line to signals_log.csv.
 - Data source: yfinance (free). Indicators computed with pandas.

Usage:
  - Install dependencies:
      uv sync
  - Run *after* market close (US market close ~1:00 PM PT). Example: run at 1:05 PM PT.
      uv run tqqq-sma

NOT FINANCIAL ADVICE: This script only *signals* the mechanical rule we agreed on. Use with appropriate position sizing and risk controls.
"""
import os
import json
import pickle
from datetime import datetime, timezone, timedelta
import pandas as pd
import yfinance as yf
import math
import smtplib
import time
from email.message import EmailMessage

# ---------- USER SETTINGS ----------
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

STATE_FILE = "data/position_state.json"
SIGNAL_LOG_CSV = "data/signals_log.csv"
HISTORY_YEARS = 3       # years of data to fetch for reliable SMA
CACHE_FILE = "data/market_data_cache.pkl"
# Cache expires after market close (4 PM ET / 9 PM UTC)

# Whether to print ASCII chart of last 6 months with buy/sell levels
PRINT_CHART = True

# Whether to generate interactive HTML chart (5 years of data)
GENERATE_INTERACTIVE_CHART = True
INTERACTIVE_CHART_FILENAME = "data/tqqq_sma_chart.html"

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

# ---------- helpers ----------
def debug_print(*args, **kwargs):
    print(*args, **kwargs)

def load_state():
    # default: assume we're out of the market (CASH)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            # fallback if corrupted
            return {"position": "CASH", "last_signal_date": None, "created": datetime.now(timezone.utc).isoformat()}
    else:
        state = {"position": "CASH", "last_signal_date": None, "created": datetime.now(timezone.utc).isoformat()}
        save_state(state)
        return state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)

def get_last_market_close():
    """Get the timestamp of the last market close (4 PM ET / 9 PM UTC)"""
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
    """Load cached market data if available and not expired (based on market close)"""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Check if cache is expired based on market close time
        cache_time = cache_data.get('timestamp')
        if cache_time:
            last_market_close = get_last_market_close()
            
            # Cache is valid only if it was created AFTER the last market close
            if cache_time >= last_market_close:
                age = datetime.now(timezone.utc) - cache_time
                debug_print(f"Using cached data from today (age: {age.seconds // 3600}h {(age.seconds % 3600) // 60}m)")
                return cache_data.get('data')
            else:
                debug_print(f"Cache is from before last market close, fetching fresh data...")
                return None
        
        return None
    except Exception as e:
        debug_print(f"Cache load error: {e}, fetching fresh data...")
        return None

def save_cache(data):
    """Save market data to cache"""
    try:
        cache_data = {
            'timestamp': datetime.now(timezone.utc),
            'data': data
        }
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(cache_data, f)
        debug_print("Market data cached successfully")
    except Exception as e:
        debug_print(f"Cache save error: {e}")



def fetch_data_with_retry(symbol, interval="1d", period="3y", retries=5, delay=2):
    """
    Fetch data from yfinance with retries and basic fallback logic.
    interval: "1d", "1h", "30m" etc.
    period:   "3y", "1mo", etc.
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
    """Fetch adjusted close data with optional caching"""
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


def compute_sma(series, period):
    return series.rolling(window=period).mean()

def pct_distance(current, target):
    # percent needed to reach target from current: (target / current - 1) * 100
    # But we present sign nicely: positive means current < target (needs +X%), negative means current > target (already over by X%)
    if current == 0 or math.isnan(current) or math.isnan(target):
        return None
    return (target / current - 1) * 100.0

def send_email(subject, body):
    if not EMAIL_ALERT.get("enabled", False):
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ALERT["from_addr"]
    msg["To"] = ", ".join(EMAIL_ALERT["to_addrs"])
    msg.set_content(body)
    try:
        with smtplib.SMTP(EMAIL_ALERT["smtp_server"], EMAIL_ALERT["smtp_port"]) as s:
            s.starttls()
            s.login(EMAIL_ALERT["username"], EMAIL_ALERT["password"])
            s.send_message(msg)
    except Exception as e:
        debug_print("Failed to send email:", e)

def append_signal_log(row: dict):
    df = pd.DataFrame([row])
    header = not os.path.exists(SIGNAL_LOG_CSV)
    df.to_csv(SIGNAL_LOG_CSV, mode='a', header=header, index=False)

def format_pct(x):
    if x is None or math.isnan(x):
        return "N/A"
    return f"{x:+.2f}%"

def sparkline(values, width=40):
    # simple ascii sparkline for quick visual; optional
    if not values:
        return ""
    # normalize to 0..1
    mn = min(values); mx = max(values)
    if mx - mn < 1e-9:
        return "─" * min(width, len(values))
    ticks = "▁▂▃▄▅▆▇█"
    res = []
    for i, v in enumerate(values[-width:]):
        idx = int((v - mn) / (mx - mn) * (len(ticks)-1))
        res.append(ticks[idx])
    return "".join(res)

def plot_ascii_chart(df, width=60, height=20):
    """
    Plot ASCII chart showing QQQ price, SMA200, and buy/sell thresholds
    """
    if df.empty:
        return
    
    # Get data for chart
    data = df[['adj_close', 'sma200']].copy()
    
    # Flatten any multi-level columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    data['buy_level'] = data['sma200'] * BUY_MULTIPLIER
    data['sell_level'] = data['sma200'] * SELL_MULTIPLIER
    data = data.dropna(subset=['sma200', 'buy_level', 'sell_level'])
    
    if len(data) == 0:
        return
    
    # Get min/max for scaling - flatten all values and find min/max
    import numpy as np
    value_arrays = [
        data['adj_close'].values.flatten(),
        data['sma200'].values.flatten(),
        data['buy_level'].values.flatten(),
        data['sell_level'].values.flatten()
    ]
    
    all_values = np.concatenate(value_arrays)
    all_values = all_values[~np.isnan(all_values)]  # Remove NaN values
    
    if len(all_values) == 0:
        return
    
    min_val = float(all_values.min())
    max_val = float(all_values.max())
    val_range = max_val - min_val
    
    if val_range < 1e-9:
        return
    
    # Create chart grid
    chart = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Sample data points to fit width
    step = max(1, len(data) // width)
    sampled_data = data.iloc[::step].tail(width)
    dates = sampled_data.index
    
    def scale_y(value):
        """Scale value to chart height"""
        return int((height - 1) * (1 - (value - min_val) / val_range))
    
    # Helper to safely get scalar value from row item (might be Series or scalar)
    def get_val(val):
        if isinstance(val, pd.Series):
            return val.iloc[0] if len(val) > 0 else np.nan
        return val
    
    # Plot lines (showing QQQ price, thresholds and SMA)
    for i, (idx, row) in enumerate(sampled_data.iterrows()):
        if i >= width:
            break
        
        # Plot SMA200 first (so it can be overwritten by other symbols)
        sma_val = get_val(row['sma200'])
        if not pd.isna(sma_val):
            y_sma = scale_y(sma_val)
            if 0 <= y_sma < height:
                if chart[y_sma][i] == ' ':
                    chart[y_sma][i] = '─'
        
        # Plot buy threshold
        buy_val = get_val(row['buy_level'])
        if not pd.isna(buy_val):
            y_buy = scale_y(buy_val)
            if 0 <= y_buy < height:
                if chart[y_buy][i] == ' ':
                    chart[y_buy][i] = '+'
        
        # Plot sell threshold
        sell_val = get_val(row['sell_level'])
        if not pd.isna(sell_val):
            y_sell = scale_y(sell_val)
            if 0 <= y_sell < height:
                if chart[y_sell][i] == ' ':
                    chart[y_sell][i] = '-'
        
        # Plot QQQ price (last so it appears on top)
        qqq_val = get_val(row['adj_close'])
        if not pd.isna(qqq_val):
            y_qqq = scale_y(qqq_val)
            if 0 <= y_qqq < height:
                chart[y_qqq][i] = '●'
    
    # Print chart
    debug_print("")
    debug_print("Chart: Last 6 Months (QQQ Price, SMA200 & Thresholds)")
    debug_print("─" * 60)
    
    # Print chart with y-axis labels on the right
    for i, row in enumerate(chart):
        y_val = min_val + (val_range * (height - 1 - i) / (height - 1))
        label = f"${y_val:6.2f}"
        debug_print(f"{''.join(row)} │ {label}")
    
    # Build x-axis with monthly markers
    # Track which months we've seen to add markers
    last_month = None
    month_positions = []
    
    for i, date in enumerate(dates):
        if i >= width:
            break
        current_month = date.strftime("%Y-%m")
        if current_month != last_month:
            month_positions.append((i, current_month))
            last_month = current_month
    
    # Print x-axis
    debug_print("└" + "─" * width)
    
    # Create month tick marks
    tick_line = [' '] * width
    for pos, _ in month_positions:
        if pos < width:
            tick_line[pos] = '│'
    debug_print(''.join(tick_line))
    
    # Print month labels with spacing (show every 2-3 months to avoid overlap)
    step = max(1, len(month_positions) // 6)  # Show ~6 labels
    display_months = []
    for i in range(0, len(month_positions), step):
        display_months.append(month_positions[i])
    
    # Build label line carefully to avoid overlaps
    label_line = [' '] * width
    for pos, month_str in display_months:
        if pos + len(month_str) <= width:
            # Check if there's room (no overlap with previous label)
            can_place = True
            for j in range(pos, min(pos + len(month_str), width)):
                if label_line[j] != ' ':
                    can_place = False
                    break
            
            if can_place:
                for j, ch in enumerate(month_str):
                    if pos + j < width:
                        label_line[pos + j] = ch
    
    debug_print(''.join(label_line))
    debug_print("")
    debug_print(f"Legend: ● QQQ Price  ─ SMA200  + Buy Level (+5%)  - Sell Level (-3%)")
    debug_print("")

def generate_interactive_chart(df, filename=INTERACTIVE_CHART_FILENAME):
    """
    Generate interactive HTML chart with plotly showing 5 years of data
    with fancy features: hover tooltips, zoom, buffer zones, etc.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        debug_print("Plotly not installed. Skipping interactive chart generation.")
        return
    
    if df.empty:
        return
    
    # Prepare data
    data = df[['adj_close', 'sma200']].copy()
    
    # Flatten columns if needed
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    data['buy_level'] = data['sma200'] * BUY_MULTIPLIER
    data['sell_level'] = data['sma200'] * SELL_MULTIPLIER
    data = data.dropna()
    
    if len(data) == 0:
        return
    
    # Create figure
    fig = go.Figure()
    
    # Add buffer zone (area between buy and sell levels)
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['buy_level'],
        mode='lines',
        name='Buy Level (+5%)',
        line=dict(color='rgba(0, 200, 0, 0.3)', width=1, dash='dot'),
        hovertemplate='<b>Buy Level</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['sell_level'],
        mode='lines',
        name='Sell Level (-3%)',
        line=dict(color='rgba(200, 0, 0, 0.3)', width=1, dash='dot'),
        fill='tonexty',
        fillcolor='rgba(200, 200, 200, 0.1)',
        hovertemplate='<b>Sell Level</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>',
        showlegend=True
    ))
    
    # Add SMA200
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['sma200'],
        mode='lines',
        name='SMA200',
        line=dict(color='rgba(100, 100, 255, 0.8)', width=2),
        hovertemplate='<b>SMA200</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>',
        showlegend=True
    ))
    
    # Add QQQ price
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['adj_close'],
        mode='lines',
        name='QQQ Price',
        line=dict(color='rgba(0, 0, 0, 0.9)', width=2.5),
        hovertemplate='<b>QQQ Price</b><br>Date: %{x}<br>Price: $%{y:.2f}<br>%{text}',
        text=[f"vs SMA: {((p/s - 1) * 100):+.2f}%" if not pd.isna(s) and s > 0 else "" 
              for p, s in zip(data['adj_close'], data['sma200'])],
        showlegend=True
    ))
    
    # Calculate percentage distance from SMA
    pct_from_sma = ((data['adj_close'] / data['sma200']) - 1) * 100
    
    # Highlight buy/sell zones with vertical rectangles
    # Find periods where price crosses thresholds
    buy_signals = (data['adj_close'] >= data['buy_level']).astype(int).diff() == 1
    sell_signals = (data['adj_close'] <= data['sell_level']).astype(int).diff() == 1
    
    # Add shapes for buy/sell signal points
    for date in data.index[buy_signals]:
        fig.add_vline(
            x=pd.Timestamp(date),
            line_width=1,
            line_dash="dash",
            line_color="green",
            opacity=0.5,
        )
        fig.add_annotation(
            x=pd.Timestamp(date),
            y=1,
            yref="paper",
            text="BUY",
            showarrow=False,
            font=dict(color="green", size=10),
            yshift=10
        )
    
    for date in data.index[sell_signals]:
        fig.add_vline(
            x=pd.Timestamp(date),
            line_width=1,
            line_dash="dash",
            line_color="red",
            opacity=0.5,
        )
        fig.add_annotation(
            x=pd.Timestamp(date),
            y=0,
            yref="paper",
            text="SELL",
            showarrow=False,
            font=dict(color="red", size=10),
            yshift=-10
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'TQQQ Trading Strategy - 5 Year Analysis<br><sub>QQQ Price vs 200-Day SMA with Trading Thresholds</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial, sans-serif'}
        },
        xaxis_title='Date',
        yaxis_title='Price ($)',
        hovermode='x unified',
        template='plotly_white',
        height=700,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.2)',
            borderwidth=1
        ),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(200, 200, 200, 0.2)'
        ),
        plot_bgcolor='rgba(250, 250, 250, 1)',
    )
    
    # Add range selector buttons
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=2, label="2y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            bgcolor='rgba(255, 255, 255, 0.8)',
            activecolor='rgba(100, 100, 255, 0.3)'
        )
    )
    
    # Save to HTML
    fig.write_html(
        filename,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'tqqq_sma_chart',
                'height': 1000,
                'width': 1600,
                'scale': 2
            }
        }
    )
    
    debug_print(f"✨ Interactive chart saved to: {filename}")
    debug_print(f"   Open in browser to explore with zoom, hover, and more!")

# ---------- main ----------
def main():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    debug_print("")
    debug_print("═" * 60)
    debug_print("  TQQQ 200-Day SMA Trading Signal")
    debug_print("═" * 60)
    # load state
    state = load_state()

    # Check for manual position override
    if MANUAL_POSITION is not None:
        if MANUAL_POSITION not in ["CASH", "TQQQ"]:
            debug_print(f"WARNING: Invalid MANUAL_POSITION '{MANUAL_POSITION}'. Using saved state.")
            position = state.get("position", "CASH")
        else:
            # Apply manual override and save it
            old_position = state.get("position", "CASH")
            if old_position != MANUAL_POSITION:
                debug_print(f"Manual override: {old_position} → {MANUAL_POSITION}")
                state["position"] = MANUAL_POSITION
                state["last_signal_date"] = None  # Reset signal date on manual change
                save_state(state)
            position = MANUAL_POSITION
    else:
        position = state.get("position", "CASH")

    last_signal_date = state.get("last_signal_date", None)

    # fetch data
    debug_print("Fetching market data...")
    qdf = fetch_adj_close(QQQ_SYMBOL, HISTORY_YEARS)

    # compute sma
    qdf['sma200'] = compute_sma(qdf['adj_close'], SMA_PERIOD)

    # Generate interactive chart if enabled (fetch 5 years of data)
    if GENERATE_INTERACTIVE_CHART:
        debug_print("Generating interactive chart...")
        qdf_5y = fetch_adj_close(QQQ_SYMBOL, 5)
        qdf_5y['sma200'] = compute_sma(qdf_5y['adj_close'], SMA_PERIOD)
        generate_interactive_chart(qdf_5y)

    # Print ASCII chart if enabled
    if PRINT_CHART:
        # Get last 6 months of data for chart
        six_months_ago = qdf.index[-1] - pd.DateOffset(months=6)
        chart_data = qdf[qdf.index >= six_months_ago].copy()
        plot_ascii_chart(chart_data)

    # latest row
    latest_q = qdf.iloc[-1]
    latest_date = latest_q.name.strftime("%Y-%m-%d")
    qqq_close = latest_q['adj_close'].iloc[0] if isinstance(latest_q['adj_close'], pd.Series) else float(latest_q['adj_close'])
    sma200_val = latest_q['sma200']
    if isinstance(sma200_val, pd.Series):
        sma200 = float(sma200_val.iloc[0]) if not sma200_val.isna().iloc[0] else None
    else:
        sma200 = float(sma200_val) if not pd.isna(sma200_val) else None

    if sma200 is None:
        debug_print(f"Not enough history to compute SMA{SMA_PERIOD}. Need more data.")
        return

    buy_level = sma200 * BUY_MULTIPLIER
    sell_level = sma200 * SELL_MULTIPLIER

    pct_vs_sma = pct_distance(sma200, qqq_close)      # percentage of current price vs SMA200 (positive = above SMA, negative = below SMA)
    pct_to_buy = pct_distance(qqq_close, buy_level)   # positive => needs +X% to reach buy threshold
    pct_to_sell = pct_distance(qqq_close, sell_level) # positive => needs +X% to reach sell threshold (i.e. current < sell_level)

    # human-friendly summary
    debug_print("")
    debug_print("─" * 60)
    debug_print(f"Date:                    {latest_date}")
    debug_print(f"QQQ Close:               ${qqq_close:.2f}")
    debug_print(f"SMA{SMA_PERIOD}:                  ${sma200:.2f}")
    debug_print(f"QQQ vs SMA{SMA_PERIOD}:           {format_pct(pct_vs_sma)}")
    debug_print("")
    debug_print(f"BUY Threshold (+5%):     ${buy_level:.2f}")
    debug_print(f"SELL Threshold (-3%):    ${sell_level:.2f}")
    debug_print("")
    debug_print(f"Distance to BUY:         {format_pct(pct_to_buy)}")
    debug_print(f"Distance to SELL:        {format_pct(pct_to_sell)}")

    debug_print("─" * 60)
    debug_print(f"Position:                {position}")
    if last_signal_date:
        debug_print(f"Last Signal Date:        {last_signal_date}")
    debug_print("─" * 60)
    debug_print("")

    # Decision logic
    reason = ""
    log_row = None

    # BUY condition (only if currently CASH)
    if position == "CASH":
        if qqq_close >= buy_level:
            reason = f"QQQ {qqq_close:.2f} >= BUY threshold {buy_level:.2f}"
            # update state
            state["position"] = "TQQQ"
            state["last_signal_date"] = latest_date
            save_state(state)
            # prepare log
            log_row = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "action": "BUY",
                "position_from": "CASH",
                "position_to": "TQQQ",
                "date": latest_date,
                "qqq_close": qqq_close,
                "sma200": sma200,
                "pct_vs_sma": pct_vs_sma,
                "buy_level": buy_level,
                "sell_level": sell_level,
                "pct_to_buy": pct_to_buy,
                "pct_to_sell": pct_to_sell,
            }
            debug_print("🟢 ALERT: BUY TQQQ")
            debug_print(f"   {reason}")
        else:
            # Still waiting for first buy opportunity
            reason = "Position=CASH and BUY condition not yet met."
            debug_print("⏸️  STATUS: Waiting for BUY signal")
            debug_print(f"   Currently in CASH, awaiting entry.")
            # show a helpful note (how far away from buy)
            if pct_to_buy is not None:
                if pct_to_buy > 0:
                    debug_print(f"   QQQ needs +{pct_to_buy:.2f}% to reach BUY threshold.")
                else:
                    # negative means current > buy_level (should not happen if buy triggered) but handle gracefully
                    debug_print(f"   QQQ is already above BUY threshold by {-pct_to_buy:.2f}% (check state).")
    # SELL condition (only if currently TQQQ)
    elif position == "TQQQ":
        if qqq_close <= sell_level:
            reason = f"QQQ {qqq_close:.2f} <= SELL threshold {sell_level:.2f}"
            state["position"] = "CASH"
            state["last_signal_date"] = latest_date
            save_state(state)
            log_row = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "action": "SELL",
                "position_from": "TQQQ",
                "position_to": "CASH",
                "date": latest_date,
                "qqq_close": qqq_close,
                "sma200": sma200,
                "pct_vs_sma": pct_vs_sma,
                "buy_level": buy_level,
                "sell_level": sell_level,
                "pct_to_buy": pct_to_buy,
                "pct_to_sell": pct_to_sell,
            }
            debug_print("🔴 ALERT: SELL TQQQ")
            debug_print(f"   {reason}")
        else:
            # Already in buy mode — ignore additional buy triggers
            reason = "Position=TQQQ and SELL condition not met. Ignoring further BUY triggers to avoid late entry."
            debug_print("✅ STATUS: Holding TQQQ")
            debug_print(f"   Currently in position, SELL condition not met.")
            # indicate how far the sell condition is (if close)
            if pct_to_sell is not None:
                if pct_to_sell > 0:
                    debug_print(f"   QQQ needs +{pct_to_sell:.2f}% to reach SELL threshold.")
                else:
                    debug_print(f"   QQQ is {(-pct_to_sell):.2f}% above SELL threshold.")

    # Append to log when a trade occurs
    if log_row:
        append_signal_log(log_row)
        # optional email
        subject = f"TQQQ {log_row['action']} Alert - {log_row['date']}"
        body_lines = [
            f"Action: {log_row['action']}",
            f"Date: {log_row['date']}",
            f"QQQ Close: {log_row['qqq_close']:.4f}",
            f"SMA{SMA_PERIOD}: {log_row['sma200']:.4f}",
            f"QQQ vs SMA{SMA_PERIOD}: {format_pct(log_row['pct_vs_sma'])}",
            f"Buy level: {log_row['buy_level']:.4f}",
            f"Sell level: {log_row['sell_level']:.4f}",
            f"pct_to_buy: {format_pct(log_row['pct_to_buy'])}",
            f"pct_to_sell: {format_pct(log_row['pct_to_sell'])}",
            "",
            "This message is generated by a mechanical SMA-based signalling script."
        ]
        send_email(subject, "\n".join(body_lines))
        debug_print(f"\n   Trade logged to {SIGNAL_LOG_CSV}")
        if EMAIL_ALERT.get("enabled", False):
            debug_print(f"   Email alert sent")

    debug_print("")
    debug_print("─" * 60)
    debug_print("📊 Interactive Chart: Open data/tqqq_sma_chart.html in your browser")
    debug_print("   to explore 5 years of historical data with 200-day SMA,")
    debug_print("   buy/sell thresholds, zoom, hover tooltips, and more!")
    debug_print("─" * 60)

if __name__ == "__main__":
    main()
