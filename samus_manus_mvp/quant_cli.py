"""Simple CLI for the lightweight quant backtester (demo + CSV loader).

Usage (from repo root):
  python -m samus_manus_mvp.quant_cli --example
  python -m samus_manus_mvp.quant_cli --csv path/to/prices.csv --window 20

CSV format: header with a `close` column (case-insensitive) or two columns where the second is close price.
"""
import csv
import sys
from typing import List
from pathlib import Path

from samus_manus_mvp.quant.backtest import sma_signals, run_backtest


def load_closes_from_csv(path: str) -> List[float]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    closes = []
    with path.open('r', newline='') as fh:
        reader = csv.reader(fh)
        headers = next(reader)
        # try to find a 'close' column
        close_idx = None
        for i, h in enumerate(headers):
            if h.strip().lower() == 'close':
                close_idx = i
                break
        if close_idx is None:
            # assume second column
            for row in reader:
                if len(row) >= 2:
                    try:
                        closes.append(float(row[1]))
                    except Exception:
                        continue
            return closes
        else:
            for row in reader:
                try:
                    closes.append(float(row[close_idx]))
                except Exception:
                    continue
            return closes


def demo_prices(n: int = 120):
    # gentle uptrend with noise
    import math
    prices = [100.0]
    for i in range(1, n):
        prices.append(prices[-1] * (1.0 + 0.001 + 0.002 * math.sin(i / 5.0)))
    return prices


def pretty_print(results: dict):
    print("Backtest results:")
    print(f"  Total return: {results['total_return']*100:.2f}%")
    print(f"  Annual return (est): {results['annual_return']*100:.2f}%")
    print(f"  Sharpe (est): {results['sharpe']:.2f}")
    print(f"  Max drawdown: {results['max_drawdown']*100:.2f}%")


def run_from_csv(path: str, window: int = 20):
    closes = load_closes_from_csv(path)
    pos = sma_signals(closes, window)
    return run_backtest(closes, pos)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', help='CSV file with price data')
    parser.add_argument('--window', type=int, default=20)
    parser.add_argument('--example', action='store_true')
    args = parser.parse_args()

    if args.example or not args.csv:
        prices = demo_prices()
        positions = sma_signals(prices, args.window)
        res = run_backtest(prices, positions)
        pretty_print(res)
        sys.exit(0)

    res = run_from_csv(args.csv, args.window)
    pretty_print(res)
