#!/usr/bin/env python3
"""
TQQQ 200-Day SMA Strategy Backtesting

Backtests the 200 SMA +5/-3 strategy from TQQQ inception (2010-02-11) to present.
Compares strategy performance against buy-and-hold TQQQ and QQQ.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_fetcher import fetch_data_with_retry
from src.calculations import compute_sma


# Strategy parameters
SMA_PERIOD = 200
BUY_MULTIPLIER = 1.05   # +5%
SELL_MULTIPLIER = 0.97  # -3%
INITIAL_CAPITAL = 10000  # $10,000 starting capital


def fetch_full_history(symbol, start_date='2010-02-11'):
    """Fetch complete history from TQQQ inception."""
    print(f"Fetching {symbol} data from {start_date}...")

    # Fetch with daily interval
    df = fetch_data_with_retry(symbol, interval='1d', period='max', retries=5, delay=2)

    if df.empty:
        raise RuntimeError(f"Failed to fetch data for {symbol}")

    # Filter to start date
    df = df[df.index >= start_date]

    print(f"  Fetched {len(df)} days of data from {df.index[0].date()} to {df.index[-1].date()}")
    return df


def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate."""
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return 0
    return (pow(end_value / start_value, 1 / years) - 1) * 100


def calculate_max_drawdown(portfolio_values):
    """Calculate maximum drawdown percentage."""
    running_max = portfolio_values.expanding().max()
    drawdown = (portfolio_values - running_max) / running_max * 100
    return drawdown.min()


def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio (assuming 2% risk-free rate)."""
    excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
    if excess_returns.std() == 0:
        return 0
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()


def backtest_strategy(qqq_data, tqqq_data):
    """
    Backtest the 200 SMA +5/-3 strategy.

    Returns:
        dict: Strategy results with portfolio values, trades, and metrics
    """
    print("\n" + "="*60)
    print("Running Backtest: 200 SMA +5/-3 Strategy")
    print("="*60)

    # Extract adj_close series
    qqq_close = qqq_data['adj_close'].squeeze() if isinstance(qqq_data['adj_close'], pd.DataFrame) else qqq_data['adj_close']
    tqqq_close = tqqq_data['adj_close'].squeeze() if isinstance(tqqq_data['adj_close'], pd.DataFrame) else tqqq_data['adj_close']

    # Align data
    combined = pd.DataFrame({
        'qqq_close': qqq_close,
        'tqqq_close': tqqq_close
    }).dropna()

    # Calculate QQQ SMA
    combined['sma200'] = compute_sma(combined['qqq_close'], SMA_PERIOD)
    combined['buy_level'] = combined['sma200'] * BUY_MULTIPLIER
    combined['sell_level'] = combined['sma200'] * SELL_MULTIPLIER

    # Drop rows with NaN SMA (first 200 days)
    combined = combined.dropna()

    print(f"\nBacktest period: {combined.index[0].date()} to {combined.index[-1].date()}")
    print(f"Total trading days: {len(combined)}")
    print(f"Initial capital: ${INITIAL_CAPITAL:,.2f}")

    # Initialize strategy tracking
    position = 'CASH'  # Start in CASH
    cash = INITIAL_CAPITAL
    shares = 0
    portfolio_values = []
    positions = []
    trades = []

    # Run backtest
    for date, row in combined.iterrows():
        qqq_price = row['qqq_close']
        tqqq_price = row['tqqq_close']
        buy_threshold = row['buy_level']
        sell_threshold = row['sell_level']

        # Check for signals
        if position == 'CASH' and qqq_price >= buy_threshold:
            # BUY signal - go all in to TQQQ
            shares = cash / tqqq_price
            cash = 0
            position = 'TQQQ'
            trades.append({
                'date': date,
                'action': 'BUY',
                'qqq_price': qqq_price,
                'tqqq_price': tqqq_price,
                'shares': shares,
                'value': shares * tqqq_price
            })

        elif position == 'TQQQ' and qqq_price <= sell_threshold:
            # SELL signal - exit to CASH
            cash = shares * tqqq_price
            position = 'CASH'
            trades.append({
                'date': date,
                'action': 'SELL',
                'qqq_price': qqq_price,
                'tqqq_price': tqqq_price,
                'shares': shares,
                'value': cash
            })
            shares = 0

        # Calculate portfolio value
        if position == 'TQQQ':
            portfolio_value = shares * tqqq_price
        else:
            portfolio_value = cash

        portfolio_values.append(portfolio_value)
        positions.append(position)

    # Create results DataFrame
    results = combined.copy()
    results['portfolio_value'] = portfolio_values
    results['position'] = positions

    # Calculate final metrics
    final_value = portfolio_values[-1]
    total_return = (final_value / INITIAL_CAPITAL - 1) * 100
    years = (combined.index[-1] - combined.index[0]).days / 365.25
    cagr = calculate_cagr(INITIAL_CAPITAL, final_value, years)

    # Calculate returns for Sharpe ratio
    returns = pd.Series(portfolio_values).pct_change()
    sharpe = calculate_sharpe_ratio(returns)

    max_dd = calculate_max_drawdown(pd.Series(portfolio_values))

    # Count trades and win rate
    num_trades = len(trades)
    winning_trades = 0
    for i in range(0, len(trades) - 1, 2):
        if i + 1 < len(trades):
            buy_value = trades[i]['value']
            sell_value = trades[i + 1]['value']
            if sell_value > buy_value:
                winning_trades += 1

    win_rate = (winning_trades / (num_trades // 2) * 100) if num_trades > 0 else 0

    print(f"\n{'─'*60}")
    print("STRATEGY RESULTS")
    print(f"{'─'*60}")
    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return:          {total_return:,.2f}%")
    print(f"CAGR:                  {cagr:.2f}%")
    print(f"Max Drawdown:          {max_dd:.2f}%")
    print(f"Sharpe Ratio:          {sharpe:.2f}")
    print(f"Number of Trades:      {num_trades}")
    print(f"Win Rate:              {win_rate:.1f}%")

    return {
        'results': results,
        'trades': trades,
        'final_value': final_value,
        'total_return': total_return,
        'cagr': cagr,
        'max_drawdown': max_dd,
        'sharpe_ratio': sharpe,
        'num_trades': num_trades,
        'win_rate': win_rate,
        'years': years
    }


def backtest_buy_and_hold(data, symbol_name, initial_capital=INITIAL_CAPITAL):
    """Backtest buy-and-hold strategy."""
    print(f"\n{'─'*60}")
    print(f"Buy-and-Hold: {symbol_name}")
    print(f"{'─'*60}")

    # Extract adj_close series
    adj_close = data['adj_close'].squeeze() if isinstance(data['adj_close'], pd.DataFrame) else data['adj_close']

    initial_price = adj_close.iloc[0]
    final_price = adj_close.iloc[-1]
    shares = initial_capital / initial_price
    final_value = shares * final_price

    portfolio_values = shares * adj_close
    total_return = (final_value / initial_capital - 1) * 100
    years = (data.index[-1] - data.index[0]).days / 365.25
    cagr = calculate_cagr(initial_capital, final_value, years)

    returns = portfolio_values.pct_change()
    sharpe = calculate_sharpe_ratio(returns)
    max_dd = calculate_max_drawdown(portfolio_values)

    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return:          {total_return:,.2f}%")
    print(f"CAGR:                  {cagr:.2f}%")
    print(f"Max Drawdown:          {max_dd:.2f}%")
    print(f"Sharpe Ratio:          {sharpe:.2f}")

    return {
        'portfolio_values': portfolio_values,
        'final_value': final_value,
        'total_return': total_return,
        'cagr': cagr,
        'max_drawdown': max_dd,
        'sharpe_ratio': sharpe,
        'years': years
    }


def generate_backtest_report(strategy_results, tqqq_bh, qqq_bh):
    """Generate HTML report with visualizations."""
    print(f"\n{'='*60}")
    print("Generating Backtest Report")
    print(f"{'='*60}")

    results = strategy_results['results']

    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            'Portfolio Value Comparison',
            'QQQ Price vs 200-Day SMA with Buy/Sell Thresholds',
            'Strategy Position Over Time'
        ),
        vertical_spacing=0.1,
        row_heights=[0.4, 0.4, 0.2]
    )

    # Plot 1: Portfolio values comparison
    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=strategy_results['results']['portfolio_value'],
            mode='lines',
            name='200 SMA Strategy',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=tqqq_bh['portfolio_values'],
            mode='lines',
            name='TQQQ Buy & Hold',
            line=dict(color='red', width=2)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=qqq_bh['portfolio_values'],
            mode='lines',
            name='QQQ Buy & Hold',
            line=dict(color='green', width=2)
        ),
        row=1, col=1
    )

    # Plot 2: QQQ price with SMA and thresholds
    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=results['qqq_close'],
            mode='lines',
            name='QQQ Price',
            line=dict(color='black', width=2),
            showlegend=True
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=results['sma200'],
            mode='lines',
            name='SMA200',
            line=dict(color='blue', width=1.5),
            showlegend=True
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=results['buy_level'],
            mode='lines',
            name='Buy Level (+5%)',
            line=dict(color='green', width=1, dash='dot'),
            showlegend=True
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=results['sell_level'],
            mode='lines',
            name='Sell Level (-3%)',
            line=dict(color='red', width=1, dash='dot'),
            showlegend=True
        ),
        row=2, col=1
    )

    # Add trade markers
    buy_trades = [t for t in strategy_results['trades'] if t['action'] == 'BUY']
    sell_trades = [t for t in strategy_results['trades'] if t['action'] == 'SELL']

    if buy_trades:
        fig.add_trace(
            go.Scatter(
                x=[t['date'] for t in buy_trades],
                y=[t['qqq_price'] for t in buy_trades],
                mode='markers',
                name='BUY Signals',
                marker=dict(color='green', size=10, symbol='triangle-up'),
                showlegend=True
            ),
            row=2, col=1
        )

    if sell_trades:
        fig.add_trace(
            go.Scatter(
                x=[t['date'] for t in sell_trades],
                y=[t['qqq_price'] for t in sell_trades],
                mode='markers',
                name='SELL Signals',
                marker=dict(color='red', size=10, symbol='triangle-down'),
                showlegend=True
            ),
            row=2, col=1
        )

    # Plot 3: Position over time
    position_numeric = [1 if p == 'TQQQ' else 0 for p in results['position']]
    fig.add_trace(
        go.Scatter(
            x=results.index,
            y=position_numeric,
            mode='lines',
            name='Position',
            fill='tozeroy',
            line=dict(color='purple', width=1),
            showlegend=False
        ),
        row=3, col=1
    )

    # Update layout
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Portfolio Value ($)", type='log', row=1, col=1)
    fig.update_yaxes(title_text="QQQ Price ($)", row=2, col=1)
    fig.update_yaxes(title_text="Position", ticktext=['CASH', 'TQQQ'], tickvals=[0, 1], row=3, col=1)

    fig.update_layout(
        title={
            'text': 'TQQQ 200-Day SMA Strategy Backtest Results<br><sub>Performance from TQQQ Inception to Present</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        height=1400,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )

    # Save to HTML
    output_file = 'backtesting/backtest_results.html'
    fig.write_html(output_file)
    print(f"\n✅ Backtest report saved to: {output_file}")

    return output_file


def main():
    """Run complete backtest analysis."""
    print("\n" + "="*60)
    print("TQQQ 200-DAY SMA STRATEGY BACKTEST")
    print("="*60)
    print(f"Start Date: TQQQ Inception (2010-02-11)")
    print(f"Strategy: 200 SMA with +5% BUY / -3% SELL thresholds")
    print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    print("="*60)

    # Fetch historical data
    qqq_data = fetch_full_history('QQQ', start_date='2010-02-11')
    tqqq_data = fetch_full_history('TQQQ', start_date='2010-02-11')

    # Align dates
    common_dates = qqq_data.index.intersection(tqqq_data.index)
    qqq_data = qqq_data.loc[common_dates]
    tqqq_data = tqqq_data.loc[common_dates]

    # Run backtests
    strategy_results = backtest_strategy(qqq_data, tqqq_data)
    tqqq_bh = backtest_buy_and_hold(tqqq_data, 'TQQQ')
    qqq_bh = backtest_buy_and_hold(qqq_data, 'QQQ')

    # Generate report
    generate_backtest_report(strategy_results, tqqq_bh, qqq_bh)

    # Print summary comparison
    print(f"\n{'='*60}")
    print("SUMMARY COMPARISON")
    print(f"{'='*60}")
    print(f"{'Strategy':<25} {'Final Value':>15} {'CAGR':>10} {'Max DD':>10} {'Sharpe':>10}")
    print(f"{'-'*60}")
    print(f"{'200 SMA +5/-3':<25} ${strategy_results['final_value']:>14,.2f} {strategy_results['cagr']:>9.2f}% {strategy_results['max_drawdown']:>9.2f}% {strategy_results['sharpe_ratio']:>9.2f}")
    print(f"{'TQQQ Buy & Hold':<25} ${tqqq_bh['final_value']:>14,.2f} {tqqq_bh['cagr']:>9.2f}% {tqqq_bh['max_drawdown']:>9.2f}% {tqqq_bh['sharpe_ratio']:>9.2f}")
    print(f"{'QQQ Buy & Hold':<25} ${qqq_bh['final_value']:>14,.2f} {qqq_bh['cagr']:>9.2f}% {qqq_bh['max_drawdown']:>9.2f}% {qqq_bh['sharpe_ratio']:>9.2f}")
    print(f"{'='*60}\n")

    return {
        'strategy': strategy_results,
        'tqqq_bh': tqqq_bh,
        'qqq_bh': qqq_bh
    }


if __name__ == '__main__':
    results = main()

