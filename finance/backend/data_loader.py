import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

STOCK_FILES = {
    "AAPL": "AAPL.csv", "BA": "BA.csv", "CAT": "CAT.csv",
    "CSCO": "CSCO.csv", "HD": "HD.csv", "IBM": "IBM.csv",
    "JNJ": "JNJ.csv", "JPM": "JPM.csv", "KO": "KO.csv",
    "MMM": "MMM.csv", "MSFT": "MSFT.csv", "WMT": "WMT.csv",
}

# Three tiers
TIER_DEMO = ["AAPL", "MSFT", "JPM", "JNJ", "HD"]  # 5 stocks
TIER_STANDARD = ["AAPL", "MSFT", "JPM", "JNJ", "HD", "KO", "CAT", "IBM"]  # 8 stocks
TIER_FULL = list(STOCK_FILES.keys())  # 12 stocks


def load_stock_data(symbol: str) -> pd.DataFrame:
    """Load a single stock's CSV data."""
    path = DATA_DIR / STOCK_FILES[symbol]
    df = pd.read_csv(path, parse_dates=["Date"])
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def compute_daily_returns(prices: pd.Series) -> pd.Series:
    """Compute daily returns from price series."""
    return prices.pct_change().dropna()

def compute_statistics(symbols: list) -> dict:
    """Compute annualized returns, covariance matrix, and other statistics for given symbols."""
    close_prices = {}
    for sym in symbols:
        df = load_stock_data(sym)
        close_prices[sym] = df.set_index("Date")["Adj Close"]

    price_df = pd.DataFrame(close_prices)
    returns_df = price_df.pct_change().dropna()

    annual_returns = returns_df.mean() * 252
    annual_cov = returns_df.cov() * 252

    return {
        "symbols": symbols,
        "annual_returns": annual_returns.to_dict(),
        "annual_covariance": annual_cov.to_dict(),
        "daily_returns_stats": {
            sym: {
                "mean": float(returns_df[sym].mean()),
                "std": float(returns_df[sym].std()),
                "sharpe": float(returns_df[sym].mean() / returns_df[sym].std())
                if returns_df[sym].std() > 0
                else 0.0,
            }
            for sym in symbols
        },
        "correlation_matrix": returns_df.corr().to_dict(),
        "price_history": {
            sym: {
                "dates": price_df[sym].index.strftime("%Y-%m-%d").tolist(),
                "prices": price_df[sym].tolist(),
            }
            for sym in symbols
        },
    }
