import math
from samus_manus_mvp.quant.backtest import sma_signals, run_backtest


def test_sma_signals_insufficient_length():
    prices = [100.0, 101.0, 102.0]
    pos = sma_signals(prices, window=5)
    assert all(p == 0 for p in pos)


def test_run_backtest_constant_prices():
    prices = [100.0] * 30
    pos = sma_signals(prices, window=5)
    res = run_backtest(prices, pos)
    assert abs(res['total_return']) < 1e-8
    assert res['sharpe'] == 0.0


def test_strategy_profitable_on_uptrend():
    # linear uptrend
    prices = [100.0 + i * 0.5 for i in range(60)]
    pos = sma_signals(prices, window=5)
    res = run_backtest(prices, pos)
    assert res['total_return'] > 0.0
    assert res['annual_return'] > 0.0
    # Sharpe should be positive for a clean uptrend
    assert res['sharpe'] >= 0.0
