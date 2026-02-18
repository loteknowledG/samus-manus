"""Lightweight daily backtester and simple strategies (no external deps).

Functions:
- sma_signals(prices, window): returns position array (0/1) using SMA momentum rule
- run_backtest(prices, positions, initial_capital=10000): returns performance dict

This is intentionally small and pure-Python so it works in CI without extra packages.
"""
from typing import List, Dict
import math


def sma(prices: List[float], window: int) -> List[float]:
    out = [None] * len(prices)
    s = 0.0
    for i, p in enumerate(prices):
        s += p
        if i >= window:
            s -= prices[i - window]
            out[i] = s / window
        elif i == window - 1:
            out[i] = s / window
    return out


def sma_signals(prices: List[float], window: int = 20) -> List[int]:
    """Return position signal (1=long, 0=flat) based on price > SMA(window).

    Signal is 1 starting the day AFTER price > SMA is observed (to avoid lookahead).
    """
    if len(prices) < window:
        return [0] * len(prices)
    ma = sma(prices, window)
    pos = [0] * len(prices)
    for i in range(1, len(prices)):
        if ma[i - 1] is None:
            pos[i] = 0
        else:
            pos[i] = 1 if prices[i - 1] > ma[i - 1] else 0
    return pos


def run_backtest(prices: List[float], positions: List[int], initial_capital: float = 10000.0) -> Dict:
    """Simulate portfolio returns given daily closing prices and discrete positions (0/1).

    Returns a dict with total_return, annual_return (approx), sharpe, max_drawdown, daily_returns list.
    """
    n = len(prices)
    if n < 2:
        return {'total_return': 0.0, 'annual_return': 0.0, 'sharpe': 0.0, 'max_drawdown': 0.0, 'equity_curve': [initial_capital], 'daily_returns': []}

    daily_returns = []
    equity = initial_capital
    equity_curve = [equity]
    portfolio_rets = []
    for i in range(1, n):
        ret = (prices[i] / prices[i - 1]) - 1.0
        pos = positions[i] if i < len(positions) else 0
        port_ret = pos * ret
        portfolio_rets.append(port_ret)
        equity = equity * (1.0 + port_ret)
        equity_curve.append(equity)
        daily_returns.append(port_ret)

    total_return = (equity_curve[-1] / initial_capital) - 1.0
    days = len(daily_returns)
    annual_return = ((1.0 + total_return) ** (252.0 / max(days, 1))) - 1.0 if days > 0 else 0.0
    # sharpe ~= mean / std * sqrt(252)
    mean_ret = sum(daily_returns) / max(len(daily_returns), 1)
    std_ret = math.sqrt(sum((r - mean_ret) ** 2 for r in daily_returns) / max(len(daily_returns), 1))
    sharpe = (mean_ret / std_ret * math.sqrt(252.0)) if std_ret > 0 else 0.0
    # max drawdown
    peak = equity_curve[0]
    max_dd = 0.0
    for val in equity_curve:
        if val > peak:
            peak = val
        dd = (peak - val) / peak
        if dd > max_dd:
            max_dd = dd

    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'sharpe': sharpe,
        'max_drawdown': max_dd,
        'equity_curve': equity_curve,
        'daily_returns': daily_returns,
    }
