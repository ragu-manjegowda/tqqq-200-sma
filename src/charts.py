"""
Chart generation utilities for ASCII and interactive Plotly charts.
"""
import pandas as pd
import numpy as np

from . import config


def plot_ascii_chart(df, width=60, height=20):
    """
    Plot ASCII chart showing QQQ price, SMA200, and buy/sell thresholds.

    Args:
        df: DataFrame with adj_close and sma200 columns
        width: chart width in characters
        height: chart height in characters
    """
    if df.empty:
        return

    # Get data for chart
    data = df[['adj_close', 'sma200']].copy()

    # Flatten any multi-level columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data['buy_level'] = data['sma200'] * config.BUY_MULTIPLIER
    data['sell_level'] = data['sma200'] * config.SELL_MULTIPLIER
    data = data.dropna(subset=['sma200', 'buy_level', 'sell_level'])

    if len(data) == 0:
        return

    # Get min/max for scaling - flatten all values and find min/max
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
    print("")
    print("Chart: Last 6 Months (QQQ Price, SMA200 & Thresholds)")
    print("─" * 60)

    # Print chart with y-axis labels on the right
    for i, row in enumerate(chart):
        y_val = min_val + (val_range * (height - 1 - i) / (height - 1))
        label = f"${y_val:6.2f}"
        print(f"{''.join(row)} │ {label}")

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
    print("└" + "─" * width)

    # Create month tick marks
    tick_line = [' '] * width
    for pos, _ in month_positions:
        if pos < width:
            tick_line[pos] = '│'
    print(''.join(tick_line))

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

    print(''.join(label_line))
    print("")
    print(f"Legend: ● QQQ Price  ─ SMA200  + Buy Level (+5%)  - Sell Level (-3%)")
    print("")


def generate_interactive_chart(df, filename=None):
    """
    Generate interactive HTML chart with plotly showing 5 years of data
    with fancy features: hover tooltips, zoom, buffer zones, etc.

    Args:
        df: DataFrame with adj_close and sma200 columns
        filename: output filename (defaults to config.INTERACTIVE_CHART_FILENAME)
    """
    if filename is None:
        filename = config.INTERACTIVE_CHART_FILENAME

    try:
        import plotly.graph_objects as go
    except ImportError:
        print("Plotly not installed. Skipping interactive chart generation.")
        return

    if df.empty:
        return

    # Prepare data
    data = df[['adj_close', 'sma200']].copy()

    # Flatten columns if needed
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data['buy_level'] = data['sma200'] * config.BUY_MULTIPLIER
    data['sell_level'] = data['sma200'] * config.SELL_MULTIPLIER
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

    print(f"✨ Interactive chart saved to: {filename}")
    print(f"   Open in browser to explore with zoom, hover, and more!")

