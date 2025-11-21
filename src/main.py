#!/usr/bin/env python3
"""
tqqq-sma - Main entry point

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

NOT FINANCIAL ADVICE: This script only *signals* the mechanical rule we agreed on. 
Use with appropriate position sizing and risk controls.
"""
import os
from datetime import datetime, timezone
import pandas as pd

from . import config
from .data_fetcher import fetch_adj_close
from .calculations import compute_sma, pct_distance, format_pct
from .state_manager import load_state, save_state
from .charts import plot_ascii_chart, generate_interactive_chart
from .logger import append_signal_log, send_email


def main():
    """Main entry point for the TQQQ SMA trading signal system."""
    # Ensure data directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    print("")
    print("═" * 60)
    print("  TQQQ 200-Day SMA Trading Signal")
    print("═" * 60)
    
    # Load state
    state = load_state()

    # Check for manual position override
    if config.MANUAL_POSITION is not None:
        if config.MANUAL_POSITION not in ["CASH", "TQQQ"]:
            print(f"WARNING: Invalid MANUAL_POSITION '{config.MANUAL_POSITION}'. Using saved state.")
            position = state.get("position", "CASH")
        else:
            # Apply manual override and save it
            old_position = state.get("position", "CASH")
            if old_position != config.MANUAL_POSITION:
                print(f"Manual override: {old_position} → {config.MANUAL_POSITION}")
                state["position"] = config.MANUAL_POSITION
                state["last_signal_date"] = None  # Reset signal date on manual change
                save_state(state)
            position = config.MANUAL_POSITION
    else:
        position = state.get("position", "CASH")

    last_signal_date = state.get("last_signal_date", None)

    # Fetch data
    print("Fetching market data...")
    qdf = fetch_adj_close(config.QQQ_SYMBOL, config.HISTORY_YEARS)
    tqqq_df = fetch_adj_close(config.TQQQ_SYMBOL, config.HISTORY_YEARS)

    # Compute SMA
    qdf['sma200'] = compute_sma(qdf['adj_close'], config.SMA_PERIOD)

    # Generate interactive chart if enabled (fetch 5 years of data)
    if config.GENERATE_INTERACTIVE_CHART:
        print("Generating interactive chart...")
        qdf_5y = fetch_adj_close(config.QQQ_SYMBOL, 5)
        qdf_5y['sma200'] = compute_sma(qdf_5y['adj_close'], config.SMA_PERIOD)
        generate_interactive_chart(qdf_5y)

    # Print ASCII chart if enabled
    if config.PRINT_CHART:
        # Get last 6 months of data for chart
        six_months_ago = qdf.index[-1] - pd.DateOffset(months=6)
        chart_data = qdf[qdf.index >= six_months_ago].copy()
        plot_ascii_chart(chart_data)

    # Get latest values
    latest_q = qdf.iloc[-1]
    latest_date = latest_q.name.strftime("%Y-%m-%d")
    qqq_close = latest_q['adj_close'].iloc[0] if isinstance(latest_q['adj_close'], pd.Series) else float(latest_q['adj_close'])
    sma200_val = latest_q['sma200']
    if isinstance(sma200_val, pd.Series):
        sma200 = float(sma200_val.iloc[0]) if not sma200_val.isna().iloc[0] else None
    else:
        sma200 = float(sma200_val) if not pd.isna(sma200_val) else None
    
    # Get latest TQQQ price
    latest_tqqq = tqqq_df.iloc[-1]
    tqqq_close = latest_tqqq['adj_close'].iloc[0] if isinstance(latest_tqqq['adj_close'], pd.Series) else float(latest_tqqq['adj_close'])

    if sma200 is None:
        print(f"Not enough history to compute SMA{config.SMA_PERIOD}. Need more data.")
        return

    # Calculate trading levels and distances
    buy_level = sma200 * config.BUY_MULTIPLIER
    sell_level = sma200 * config.SELL_MULTIPLIER

    pct_vs_sma = pct_distance(sma200, qqq_close)      # percentage of current price vs SMA200
    pct_to_buy = pct_distance(qqq_close, buy_level)   # positive => needs +X% to reach buy threshold
    pct_to_sell = pct_distance(qqq_close, sell_level) # positive => needs +X% to reach sell threshold

    # Print human-friendly summary
    print("")
    print("─" * 60)
    print(f"Date:                    {latest_date}")
    print(f"QQQ Close:               ${qqq_close:.2f}")
    print(f"SMA{config.SMA_PERIOD}:                  ${sma200:.2f}")
    print(f"QQQ vs SMA{config.SMA_PERIOD}:           {format_pct(pct_vs_sma)}")
    print("")
    print(f"BUY Threshold (+5%):     ${buy_level:.2f}")
    print(f"SELL Threshold (-3%):    ${sell_level:.2f}")
    print("")
    print(f"Distance to BUY:         {format_pct(pct_to_buy)}")
    print(f"Distance to SELL:        {format_pct(pct_to_sell)}")

    print("─" * 60)
    print(f"Position:                {position}")
    if last_signal_date:
        print(f"Last Signal Date:        {last_signal_date}")
    print(f"TQQQ Close:              ${tqqq_close:.2f}")
    print("─" * 60)
    print("")

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
                "tqqq_close": tqqq_close,
            }
            print("🟢 ALERT: BUY TQQQ")
            print(f"   {reason}")
        else:
            # Not at buy threshold yet
            reason = f"Position=CASH. QQQ has not reached BUY threshold."
            print("⚪ STATUS: Holding CASH")
            print(f"   {reason}")
            if pct_to_buy is not None:
                if pct_to_buy > 0:
                    print(f"   QQQ needs {format_pct(pct_to_buy)} to reach BUY threshold.")
                else:
                    # negative means current > buy_level (should not happen if buy triggered) but handle gracefully
                    print(f"   QQQ is already above BUY threshold by {-pct_to_buy:.2f}% (check state).")
    
    # SELL condition (only if currently TQQQ)
    elif position == "TQQQ":
        if qqq_close <= sell_level:
            reason = f"QQQ {qqq_close:.2f} <= SELL threshold {sell_level:.2f}"
            # update state
            state["position"] = "CASH"
            state["last_signal_date"] = latest_date
            save_state(state)
            # prepare log
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
                "tqqq_close": tqqq_close,
            }
            print("🔴 ALERT: SELL TQQQ")
            print(f"   {reason}")
        else:
            # Already in buy mode — ignore additional buy triggers
            reason = "Position=TQQQ and SELL condition not met. Ignoring further BUY triggers to avoid late entry."
            print("✅ STATUS: Holding TQQQ")
            print(f"   Currently in position, SELL condition not met.")
            # indicate how far the sell condition is (if close)
            if pct_to_sell is not None:
                if pct_to_sell > 0:
                    print(f"   QQQ needs +{pct_to_sell:.2f}% to reach SELL threshold.")
                else:
                    print(f"   QQQ is {(-pct_to_sell):.2f}% above SELL threshold.")

    # Append to log when a trade occurs
    if log_row:
        append_signal_log(log_row)
        # optional email
        subject = f"TQQQ {log_row['action']} Alert - {log_row['date']}"
        body_lines = [
            f"Action: {log_row['action']}",
            f"Date: {log_row['date']}",
            f"QQQ Close: {log_row['qqq_close']:.4f}",
            f"SMA{config.SMA_PERIOD}: {log_row['sma200']:.4f}",
            f"QQQ vs SMA{config.SMA_PERIOD}: {format_pct(log_row['pct_vs_sma'])}",
            f"Buy level: {log_row['buy_level']:.4f}",
            f"Sell level: {log_row['sell_level']:.4f}",
            f"pct_to_buy: {format_pct(log_row['pct_to_buy'])}",
            f"pct_to_sell: {format_pct(log_row['pct_to_sell'])}",
            "",
            "This message is generated by a mechanical SMA-based signalling script."
        ]
        send_email(subject, "\n".join(body_lines))
        print(f"\n   Trade logged to {config.SIGNAL_LOG_CSV}")
        if config.EMAIL_ALERT.get("enabled", False):
            print(f"   Email alert sent")

    print("")
    print("─" * 60)
    print("📊 Interactive Chart: Open data/tqqq_sma_chart.html in your browser")
    print("   to explore 5 years of historical data with 200-day SMA,")
    print("   buy/sell thresholds, zoom, hover tooltips, and more!")
    print("─" * 60)


if __name__ == "__main__":
    main()
