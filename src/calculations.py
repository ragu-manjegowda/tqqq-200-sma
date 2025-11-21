"""
Technical analysis calculations and formatting utilities.
"""
import math


def compute_sma(series, period):
    """
    Compute Simple Moving Average.
    
    Args:
        series: pandas Series of prices
        period: number of periods for the moving average
        
    Returns:
        pandas Series with SMA values
    """
    return series.rolling(window=period).mean()


def pct_distance(current, target):
    """
    Calculate percentage distance from current to target.
    
    Returns positive percentage if current < target (need to go up),
    negative percentage if current > target (already above).
    
    Args:
        current: current value
        target: target value
        
    Returns:
        float: percentage distance, or None if invalid inputs
    """
    if current == 0 or math.isnan(current) or math.isnan(target):
        return None
    return (target / current - 1) * 100.0


def format_pct(val):
    """
    Format percentage value for display.
    
    Args:
        val: percentage value or None
        
    Returns:
        str: formatted percentage string
    """
    if val is None or math.isnan(val):
        return "N/A"
    return f"{val:+.2f}%"

