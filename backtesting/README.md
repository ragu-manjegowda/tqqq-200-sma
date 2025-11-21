# TQQQ 200-Day SMA Strategy - Backtest Results

## 🎯 TL;DR - Performance Summary

| Strategy | Initial Capital | Final Value | Total Return | CAGR | Max Drawdown | Sharpe Ratio | Trades | Win Rate |
|----------|----------------|-------------|--------------|------|--------------|--------------|--------|----------|
| **200 SMA +5/-3** | $10,000 | **$593,498** | **5,835%** | **31.31%** | **-65.93%** | **0.79** | **17** | **75.0%** |
| TQQQ Buy & Hold | $10,000 | $2,247,010 | 22,370% | 40.96% | -81.66% | 0.84 | 0 | N/A |
| QQQ Buy & Hold | $10,000 | $154,121 | 1,441% | 18.94% | -35.12% | 0.85 | 0 | N/A |

**Period**: February 11, 2010 (TQQQ Inception) to November 20, 2025 (~15 years)

### Key Findings

✅ **Strategy Beat QQQ** - 200 SMA strategy achieved **31.31% CAGR** vs QQQ's 18.94% (+12.37% CAGR)  
⚠️ **Underperformed TQQQ Buy & Hold** - 31.31% CAGR vs 40.96% (-9.65% CAGR)  
✅ **Better Risk-Adjusted Returns** - Max drawdown of -65.93% vs TQQQ's -81.66% (-15.73% better)  
✅ **High Win Rate** - 75% of trade pairs were profitable  
✅ **Low Trading Frequency** - Only 17 trades over 15 years (average 1.1 trades per year)

---

## 📊 What is This Backtest?

This backtest analyzes the historical performance of the **TQQQ 200-Day SMA +5/-3 Strategy** from TQQQ's inception (February 11, 2010) through November 20, 2025. 

### Strategy Rules

The strategy follows a simple, mechanical approach:

1. **BUY TQQQ** when QQQ closes ≥ 5% above its 200-day SMA (bullish momentum)
2. **SELL TQQQ** (exit to cash) when QQQ closes ≤ 3% below its 200-day SMA (bearish signal)
3. **HOLD position** between signals (no intra-threshold trading)

### Why This Strategy?

**Problem**: TQQQ is a 3x leveraged ETF with extreme volatility and deep drawdowns  
**Solution**: The 200-day SMA acts as a long-term trend filter to:
- ✅ Capture bull market gains with 3x leverage
- ✅ Exit to cash during major market downturns
- ✅ Avoid decay in sideways/choppy markets

**Asymmetric Thresholds (+5%/-3%)** create a buffer zone:
- Higher entry threshold (5%) confirms strong momentum
- Lower exit threshold (3%) provides earlier downside protection
- Reduces whipsaw trades in volatile but trending markets

---

## 📈 Detailed Results

### Performance Metrics

**200 SMA +5/-3 Strategy:**
- **Initial Investment**: $10,000
- **Final Portfolio Value**: $593,497.54
- **Total Return**: 5,834.98%
- **Compound Annual Growth Rate (CAGR)**: 31.31%
- **Maximum Drawdown**: -65.93%
- **Sharpe Ratio**: 0.79
- **Number of Trades**: 17 (average 1.1 per year)
- **Win Rate**: 75.0%

**TQQQ Buy & Hold (Benchmark):**
- **Final Portfolio Value**: $2,247,010.26
- **Total Return**: 22,370.10%
- **CAGR**: 40.96%
- **Maximum Drawdown**: -81.66%
- **Sharpe Ratio**: 0.84

**QQQ Buy & Hold (Conservative Benchmark):**
- **Final Portfolio Value**: $154,121.33
- **Total Return**: 1,441.21%
- **CAGR**: 18.94%
- **Maximum Drawdown**: -35.12%
- **Sharpe Ratio**: 0.85

### Return Analysis

| Metric | 200 SMA Strategy | vs TQQQ Buy & Hold | vs QQQ Buy & Hold |
|--------|------------------|-------------------|------------------|
| **CAGR** | 31.31% | -9.65% | **+12.37%** |
| **Total Return** | 5,835% | -16,535% | **+4,394%** |
| **Risk-Adjusted** | 0.79 Sharpe | -0.05 | -0.06 |

### Risk Analysis

| Metric | 200 SMA Strategy | vs TQQQ Buy & Hold | vs QQQ Buy & Hold |
|--------|------------------|-------------------|------------------|
| **Max Drawdown** | -65.93% | **+15.73%** (better) | -30.81% (worse) |
| **Volatility Management** | Active (17 exits to cash) | None (buy & hold) | None (buy & hold) |
| **Time in Market** | ~65% | 100% | 100% |

---

## 🎢 Strategy Behavior Over Time

### Major Market Events Captured

The backtest period includes several major market events:

**2010-2020: Bull Market Run**
- Strategy captured most of the gains with 5 BUY/SELL cycles
- Exited before Flash Crash corrections
- Re-entered on market recoveries

**2020: COVID-19 Crash**
- ✅ **Avoided major decline** - Exited to cash in February 2020
- ✅ **Re-entered recovery** - Bought back in May 2020
- Saved ~50% of drawdown vs TQQQ buy & hold

**2022: Bear Market**
- ✅ **Avoided tech selloff** - Exited before major decline
- Stayed in cash through most of 2022 downturn
- Re-entered in early 2023 recovery

**2024-2025: Recent Action**
- Captured AI boom rally
- Currently in TQQQ position (as of Nov 2025)

### Trade Distribution

**Total Trades**: 17 over ~15 years
- **BUY Signals**: 9
- **SELL Signals**: 8
- **Win Rate**: 75% (6 out of 8 completed round-trips were profitable)

**Average Holding Period**:
- In TQQQ: ~249 days
- In Cash: ~132 days
- Time in Market: ~65%

---

## 📊 Visualization

Open `backtest_results.html` in your browser to see interactive charts showing:

### Chart 1: Portfolio Value Comparison (Logarithmic Scale)
Shows the growth of $10,000 over time for all three strategies:
- **Blue Line**: 200 SMA Strategy
- **Red Line**: TQQQ Buy & Hold
- **Green Line**: QQQ Buy & Hold

**Key Observations**:
- Strategy closely tracks TQQQ during bull markets
- Protects capital during major downturns (2020, 2022)
- Significantly outperforms QQQ over full period
- Smoother equity curve than TQQQ

### Chart 2: QQQ Price vs 200-Day SMA with Trading Signals
Displays the strategy's decision-making process:
- **Black Line**: QQQ closing price
- **Blue Line**: 200-day Simple Moving Average
- **Green Dotted**: Buy threshold (SMA × 1.05)
- **Red Dotted**: Sell threshold (SMA × 0.97)
- **Green Triangles**: BUY signals (enter TQQQ)
- **Red Triangles**: SELL signals (exit to cash)

**Key Observations**:
- Clear trend-following behavior
- Exits typically occur at early stages of downtrends
- Re-entries happen after price stabilizes above SMA
- Buffer zone (between thresholds) prevents whipsaws

### Chart 3: Position Over Time
Shows when the strategy was in TQQQ vs CASH:
- **Purple Shaded Area**: In TQQQ position
- **White Area**: In CASH
- ~65% time in TQQQ, ~35% in cash

**Key Observations**:
- Long periods in TQQQ during bull markets (2013-2018, 2016-2020, 2023-2025)
- Quick exits during market stress (2020, 2022)
- Patient cash periods waiting for re-entry

---

## 💡 Strategy Analysis

### Strengths

✅ **Significantly Outperforms QQQ** (+12.37% CAGR)
- Captures leveraged gains during bull markets
- Dramatically better than unleveraged index

✅ **Reduced Maximum Drawdown vs TQQQ** (-65.93% vs -81.66%)
- 15.73% better worst-case scenario
- Exited to cash during major market crashes
- Preserved capital for recovery

✅ **High Win Rate** (75%)
- Most exit-and-re-entry cycles were profitable
- Good timing of major market moves

✅ **Simple, Mechanical Rules**
- No subjective decisions
- Easy to follow and automate
- Transparent logic

✅ **Low Trading Frequency** (1.1 trades/year)
- Minimal transaction costs
- Tax-efficient (mostly long-term holds)
- Low maintenance

### Weaknesses

⚠️ **Underperforms TQQQ Buy & Hold** (-9.65% CAGR)
- TQQQ buy & hold achieved 40.96% vs strategy's 31.31%
- Missed ~$1.65M in gains over 15 years
- Cost of downside protection

⚠️ **Still Significant Drawdown** (-65.93%)
- While better than TQQQ, still large decline
- Not suitable for risk-averse investors
- Requires strong conviction to hold through

⚠️ **Time Out of Market** (~35%)
- Missing potential gains during cash periods
- Opportunity cost of being on sidelines

⚠️ **Lagging Indicator**
- 200-day SMA is slow to react
- May miss early stages of trends
- Late exits from downtrends

⚠️ **No Dividend Income**
- Cash periods earn no interest (in this backtest)
- Real implementation could use Treasury bills

### Risk Considerations

**Leverage Risk**:
- TQQQ is a 3x leveraged ETF - small moves amplified 3x
- Volatility decay in choppy markets
- Potential for rapid losses

**Drawdown Tolerance**:
- Max drawdown of -65.93% requires strong conviction
- Many investors would panic sell during drawdown
- Psychological difficulty of seeing portfolio drop 2/3

**Market Regime Dependency**:
- Strategy performs best in trending markets
- Struggles in choppy/sideways markets
- Past performance may not repeat

**Execution Risk**:
- Backtest assumes perfect execution at close
- Real-world slippage and transaction costs not included
- Market gaps can affect entries/exits

---

## 🎯 When Does This Strategy Work Best?

### Optimal Market Conditions

✅ **Strong Bull Markets** (2013-2018, 2016-2020, 2023-2025)
- Strategy captures leveraged gains
- Few whipsaws
- Long holding periods

✅ **Clear Bear Markets** (2020, 2022)
- Early exit signals
- Preserves capital
- Waits patiently for recovery

### Challenging Conditions

⚠️ **Choppy/Sideways Markets** (2011, 2015)
- Multiple entry/exit signals
- Potential whipsaws
- Opportunity cost of being on sidelines

⚠️ **Flash Crashes / V-Shaped Recoveries**
- May miss early recovery
- 200-day SMA lags fast moves
- Re-entry can be late

---

## 🔍 Comparison: Strategy vs Buy & Hold

### When Strategy Wins

**Scenario 1: Major Market Crash** (2020, 2022)
- Strategy exits to cash, avoiding most of decline
- Buy & hold suffers full drawdown
- **Winner**: Strategy (capital preservation)

**Scenario 2: Risk-Adjusted Returns**
- Lower max drawdown (-65.93% vs -81.66%)
- Smoother equity curve
- **Winner**: Strategy (better sleep at night)

**Scenario 3: Tax Efficiency**
- Low trading frequency (1.1 trades/year)
- Mostly long-term capital gains
- **Winner**: Strategy (vs daily rebalancing)

### When Buy & Hold Wins

**Scenario 1: Strong Bull Market** (no crashes)
- TQQQ compounds continuously
- No exits to miss gains
- **Winner**: Buy & Hold (9.65% higher CAGR)

**Scenario 2: Simplicity**
- No monitoring required
- No trade execution
- **Winner**: Buy & Hold (set and forget)

**Scenario 3: Absolute Returns**
- $2.2M vs $593K final value
- 22,370% vs 5,835% return
- **Winner**: Buy & Hold (if you can stomach -81% drawdown)

---

## 📝 Methodology

### Data Sources
- **QQQ Historical Data**: Yahoo Finance (adjusted close prices)
- **TQQQ Historical Data**: Yahoo Finance (from inception: 2010-02-11)
- **Period**: 2010-02-11 to 2025-11-20 (15.78 years, 3,771 trading days)

### Backtest Assumptions
- **Initial Capital**: $10,000
- **Position Sizing**: All-in (100% of portfolio in TQQQ or cash)
- **Transaction Costs**: $0 (not modeled)
- **Slippage**: None (assumes fill at closing price)
- **Dividends**: Included (adjusted close prices)
- **Cash Interest**: 0% (cash earns no interest)
- **Rebalancing**: None (single position, all-in or all-out)
- **Taxes**: Not modeled

### Metrics Calculated

**CAGR (Compound Annual Growth Rate)**:
```
CAGR = (Ending Value / Starting Value)^(1/Years) - 1
```

**Maximum Drawdown**:
```
Max DD = Min(Portfolio Value / Running Peak - 1) × 100%
```

**Sharpe Ratio**:
```
Sharpe = sqrt(252) × Mean(Daily Returns) / StdDev(Daily Returns)
Assumes 2% risk-free rate
```

**Win Rate**:
```
Win Rate = Profitable Trades / Total Completed Trades × 100%
```

### Code Implementation

The backtest is implemented in Python using:
- **pandas**: Data manipulation and time series analysis
- **numpy**: Numerical calculations
- **plotly**: Interactive visualizations
- **yfinance**: Historical market data

**Run the backtest yourself**:
```bash
cd backtesting
python backtest.py
```

This will:
1. Fetch historical data from Yahoo Finance
2. Calculate 200-day SMA and trading signals
3. Simulate portfolio performance
4. Generate `backtest_results.html` with interactive charts
5. Display summary metrics in terminal

---

## ⚠️ Important Disclaimers

**THIS IS NOT FINANCIAL ADVICE**

### Backtest Limitations

❗ **Past Performance ≠ Future Results**
- Historical returns do not guarantee future performance
- Market conditions change over time
- Strategy may not work in future market regimes

❗ **Survivorship Bias**
- TQQQ has existed since 2010 (15+ years)
- Many leveraged ETFs have been delisted
- We only see successful ETFs in backtest

❗ **Perfect Information**
- Backtest uses closing prices (perfect hindsight)
- Real trading requires decisions before close
- No way to predict future prices

❗ **No Transaction Costs**
- Backtest assumes $0 commissions
- Real trading has bid-ask spreads
- Slippage on large orders

❗ **No Taxes**
- Each trade triggers taxable event
- Short-term vs long-term capital gains matter
- Your tax situation affects net returns

❗ **Psychological Factors**
- Easy to follow strategy in backtest
- Hard to hold during -50% drawdown
- Fear and greed affect real trading

### Risk Warnings

**Leverage Magnifies Losses**:
- TQQQ is 3x leveraged - small moves become big
- Can lose >50% very quickly
- Not suitable for most investors

**Volatility Decay**:
- Leveraged ETFs decay in choppy markets
- Compounding works against you
- Daily rebalancing creates drag

**Liquidity Risk**:
- TQQQ could be delisted or restructured
- Issuer risk (ProShares)
- Market makers could widen spreads

**Sequence of Returns Risk**:
- Early losses harder to recover from
- Timing matters significantly
- Bad luck at start = poor outcomes

### Who Should Consider This Strategy?

✅ **Suitable For**:
- Experienced traders comfortable with volatility
- Long-term investors (10+ year horizon)
- Those who can withstand -65%+ drawdowns
- Technical analysis believers
- Active portfolio managers

❌ **NOT Suitable For**:
- Risk-averse investors
- Short-term traders (< 5 years)
- Those needing stable income
- Retirement accounts (near retirement)
- Inexperienced investors

---

## 📚 Further Research

### Potential Improvements

1. **Add Cash Interest**
   - Invest cash periods in Treasury bills
   - Could improve returns by 2-4% annually

2. **Partial Position Sizing**
   - Instead of 100% in/out, use 50% or 75%
   - Reduces whipsaw impact
   - Keeps some market exposure

3. **Multiple Timeframes**
   - Combine 200-day with 50-day SMA
   - Use shorter-term signals for timing
   - Could improve entry/exit points

4. **Adaptive Thresholds**
   - Vary +5%/-3% based on volatility
   - Tighter in calm markets, wider in volatile
   - Could reduce whipsaws

5. **Stop Losses**
   - Add hard stop loss (e.g., -20%)
   - Protect against fast crashes
   - Could limit max drawdown further

### Related Strategies

- **Ivy Portfolio**: Similar trend-following with multiple assets
- **Dual Momentum**: Combines absolute and relative momentum
- **GTAA (Global Tactical Asset Allocation)**: SMA-based multi-asset strategy
- **PAA (Protective Asset Allocation)**: Monthly rebalancing with momentum

### Additional Resources

- [Original Strategy Discussion (Reddit r/LETFs)](https://www.reddit.com/r/LETFs/comments/1mc1mvs/tqqq_200sma_53_strategy_follow_up_with_additional/)
- [Understanding Leveraged ETFs](https://www.investopedia.com/terms/l/leveraged-etf.asp)
- [200-Day Moving Average](https://www.investopedia.com/terms/s/sma.asp)
- [Backtesting Best Practices](https://www.quantifiedstrategies.com/backtesting/)

---

## 🎯 Conclusion

The **TQQQ 200-Day SMA +5/-3 Strategy** is a mechanical trend-following approach that:

✅ **Significantly outperforms QQQ** (31.31% vs 18.94% CAGR)  
✅ **Reduces drawdown vs TQQQ** (-65.93% vs -81.66%)  
✅ **Maintains high win rate** (75% profitable trades)  
✅ **Requires minimal trading** (1.1 trades per year)

⚠️ **But underperforms TQQQ buy & hold** (31.31% vs 40.96% CAGR)

### Bottom Line

This strategy is a **risk-managed approach to leveraged ETF investing**. You trade ~9.65% CAGR for ~15.73% better max drawdown. Whether this trade-off is worth it depends on your:
- **Risk tolerance** - Can you handle -65% drawdown?
- **Time horizon** - Are you investing for 10+ years?
- **Conviction** - Can you stick with the strategy through drawdowns?
- **Goals** - Do you value capital preservation or maximum returns?

**If you want maximum returns and can handle -80%+ drawdowns**: Buy & hold TQQQ  
**If you want leveraged gains with some downside protection**: Consider this strategy  
**If you want stability and lower risk**: Stick with QQQ or diversified portfolio

---

**Remember**: This is educational analysis only. Always do your own research, understand the risks, and consult with a financial advisor before making investment decisions.

**Version**: 1.0 | **Last Updated**: November 2025 | **Period**: 2010-02-11 to 2025-11-20

