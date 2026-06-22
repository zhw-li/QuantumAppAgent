from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import pandas as pd
import json
from pathlib import Path

from .data_loader import (
    load_stock_data,
    compute_statistics,
    TIER_DEMO,
    TIER_STANDARD,
    TIER_FULL,
    STOCK_FILES,
)
from .qaoa_solver import solve_qaoa, brute_force_optimal
from .classical_solver import markowitz_optimize

app = FastAPI(title="Quantum Portfolio Optimization", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---- Cache ----
_cache = {}


class OptimizeRequest(BaseModel):
    tier: str = "demo"  # demo, standard, full
    k: int = 3  # number of stocks to select
    q: float = 0.5  # risk aversion
    depth: int = 2  # QAOA depth
    restarts: int = 5  # QAOA restarts
    force: bool = False  # bypass cache


# ---- Helper ----


def _get_tier_symbols(tier: str) -> list:
    """Map tier name to stock symbol list."""
    if tier == "demo":
        return TIER_DEMO
    elif tier == "standard":
        return TIER_STANDARD
    elif tier == "full":
        return TIER_FULL
    else:
        raise HTTPException(400, f"Invalid tier: {tier}. Use demo, standard, or full.")


def _build_mu_sigma(symbols, stats):
    """Build mu and sigma arrays from statistics, preserving symbol order."""
    mu = np.array([stats["annual_returns"][s] for s in symbols])
    sigma_df = pd.DataFrame(stats["annual_covariance"])
    sigma = sigma_df.loc[symbols, symbols].values
    return mu, sigma


def _compute_max_drawdown(prices_series):
    """Compute max drawdown from a price series."""
    cummax = prices_series.cummax()
    drawdown = (prices_series - cummax) / cummax
    return float(drawdown.min())


# ---- Endpoints ----


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "quantum-portfolio-optimizer", "port": 8006}


@app.get("/api/stocks")
async def list_stocks():
    """List all available stocks with basic info."""
    stocks = []
    for symbol in STOCK_FILES:
        df = load_stock_data(symbol)
        latest = df.iloc[-1]
        first = df.iloc[0]
        total_return = (latest["Adj Close"] - first["Adj Close"]) / first["Adj Close"]
        stocks.append(
            {
                "symbol": symbol,
                "name": symbol,
                "start_date": str(df["Date"].iloc[0].date()),
                "end_date": str(df["Date"].iloc[-1].date()),
                "latest_price": round(float(latest["Adj Close"]), 2),
                "total_return": round(float(total_return) * 100, 2),
                "data_points": len(df),
            }
        )
    return {
        "stocks": stocks,
        "tiers": {"demo": TIER_DEMO, "standard": TIER_STANDARD, "full": TIER_FULL},
    }


@app.get("/api/stock/{symbol}/history")
async def stock_history(symbol: str, days: int = 0):
    """Get price history for a stock — returns {date, close} format for frontend."""
    if symbol not in STOCK_FILES:
        raise HTTPException(404, f"Stock {symbol} not found")
    df = load_stock_data(symbol)
    if days > 0:
        df = df.tail(days)
    # Frontend expects array of {date, close} objects
    history = [
        {"date": str(row["Date"].date()), "close": round(float(row["Adj Close"]), 2)}
        for _, row in df.iterrows()
    ]
    return {
        "symbol": symbol,
        "history": history,
    }


@app.get("/api/statistics")
async def get_statistics(tier: str = "demo"):
    """Get return statistics and correlation for a tier — returns arrays for frontend table."""
    symbols = _get_tier_symbols(tier)
    stats = compute_statistics(symbols)

    # Build arrays for frontend table compatibility
    annual_returns_list = [float(stats["annual_returns"][s]) for s in symbols]
    daily_stats = stats.get("daily_returns_stats", {})

    # Compute annualized volatility and other stats per stock
    annual_volatilities = []
    sharpe_ratios = []
    max_drawdowns = []
    total_returns = []

    for s in symbols:
        df = load_stock_data(s)
        prices = df["Adj Close"]
        daily_ret = prices.pct_change().dropna()

        ann_vol = float(daily_ret.std() * np.sqrt(252))
        ann_ret = float(stats["annual_returns"][s])
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0
        mdd = _compute_max_drawdown(prices)
        total_ret = float((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0])

        annual_volatilities.append(ann_vol)
        sharpe_ratios.append(sharpe)
        max_drawdowns.append(mdd)
        total_returns.append(total_ret)

    # Build correlation matrix as 2D array
    corr_dict = stats.get("correlation_matrix", {})
    corr_matrix = []
    for s1 in symbols:
        row = [float(corr_dict[s1][s2]) for s2 in symbols]
        corr_matrix.append(row)

    return {
        "symbols": symbols,
        "annual_returns": annual_returns_list,
        "annual_volatilities": annual_volatilities,
        "sharpe_ratios": sharpe_ratios,
        "max_drawdowns": max_drawdowns,
        "total_returns": total_returns,
        "correlation": corr_matrix,
        "correlation_matrix": corr_matrix,
        "annual_covariance": stats["annual_covariance"],
        "price_history": stats.get("price_history", {}),
    }


@app.post("/api/optimize/classical")
async def optimize_classical(req: OptimizeRequest):
    """Run Markowitz mean-variance optimization — returns flat format for frontend."""
    symbols = _get_tier_symbols(req.tier)
    stats = compute_statistics(symbols)
    mu, sigma = _build_mu_sigma(symbols, stats)

    result = markowitz_optimize(mu, sigma, req.k, req.q)

    # Convert weights array to {symbol: weight} dict for frontend pie charts
    weights_dict = {symbols[i]: round(float(result["weights"][i]), 4) for i in range(len(symbols))}

    # Top-k selection
    top_k_indices = np.argsort(-np.array(result["weights"]))[: req.k]
    selected_stocks = [symbols[i] for i in top_k_indices]

    # Individual stock risk-return points for frontier plot
    stock_points = [
        {
            "name": symbols[i],
            "risk": float(np.sqrt(sigma[i, i])),
            "return": float(mu[i]),
        }
        for i in range(len(symbols))
    ]

    return {
        "weights": weights_dict,
        "portfolio_return": result["portfolio_return"],
        "portfolio_risk": result["portfolio_risk"],
        "portfolio_sharpe": result["portfolio_sharpe"],
        "sharpe_ratio": result["portfolio_sharpe"],
        "efficient_frontier": result["efficient_frontier"],
        "selected_stocks": selected_stocks,
        "top_k_selection": {
            "indices": top_k_indices.tolist(),
            "symbols": selected_stocks,
            "weights": [round(float(result["weights"][i]), 4) for i in top_k_indices],
        },
        "stock_points": stock_points,
        "symbols": symbols,
        "tier": req.tier,
    }


@app.post("/api/optimize/quantum")
async def optimize_quantum(req: OptimizeRequest):
    """Run QAOA portfolio optimization — returns flat format for frontend."""
    cache_key = f"quantum_{req.tier}_{req.k}_{req.q}_{req.depth}_{req.restarts}"

    if not req.force and cache_key in _cache:
        return _cache[cache_key]

    symbols = _get_tier_symbols(req.tier)
    stats = compute_statistics(symbols)
    mu, sigma = _build_mu_sigma(symbols, stats)

    # QAOA solve
    qaoa_result = solve_qaoa(mu, sigma, req.k, req.q, req.depth, req.restarts)

    # Brute force for comparison
    bf_result = brute_force_optimal(mu, sigma, req.k, req.q)

    # Cost gap
    cost_gap = (
        abs(qaoa_result["objective_value"] - bf_result["qubo_objective_value"])
        / max(abs(bf_result["qubo_objective_value"]), 1e-10)
        * 100
    )

    # Build weights dict for selected stocks (equal weight for binary selection)
    selected_indices = qaoa_result["selected_indices"]
    selected_stocks = [symbols[i] for i in selected_indices]
    # Binary selection: equal weight among selected
    weights_dict = {symbols[i]: round(1.0 / len(selected_indices), 4) for i in selected_indices}
    # Add zero-weight stocks for pie chart
    for i, s in enumerate(symbols):
        if i not in selected_indices:
            weights_dict[s] = 0.0

    # Build top-bitstrings for frontend
    top_bitstrings = []
    for bits, prob in qaoa_result["qaoa_details"]["probability_top10"]:
        top_bitstrings.append({
            "bitstring": bits,
            "probability": prob,
            "is_selected": bits == "".join(str(b) for b in qaoa_result["solution"]),
        })

    # Flat format for frontend
    result = {
        "symbols": symbols,
        "tier": req.tier,
        "k": req.k,
        "q": req.q,
        "solution": qaoa_result["solution"],
        "selected_indices": selected_indices,
        "selected_stocks": selected_stocks,
        "weights": weights_dict,
        "portfolio_return": qaoa_result["portfolio_return"],
        "portfolio_risk": qaoa_result["portfolio_risk"],
        "portfolio_sharpe": qaoa_result["portfolio_sharpe"],
        "sharpe_ratio": qaoa_result["portfolio_sharpe"],
        "cost_gap": round(cost_gap, 4),
        "optimal_energy": qaoa_result["objective_value"],
        "penalty_weight": qaoa_result["qaoa_details"]["penalty"],
        "norm_factor": qaoa_result["qaoa_details"]["norm_factor"],
        "n_qubits": qaoa_result["qaoa_details"]["n_qubits"],
        "depth": qaoa_result["qaoa_details"]["depth"],
        "top_bitstrings": top_bitstrings,
        "brute_force": {
            "selected_stocks": [symbols[i] for i in bf_result["selected_indices"]],
            "portfolio_return": bf_result["portfolio_return"],
            "portfolio_risk": bf_result["portfolio_risk"],
            "portfolio_sharpe": bf_result["portfolio_sharpe"],
        },
    }

    # Save results
    result_path = RESULTS_DIR / f"quantum_{req.tier}_k{req.k}.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    _cache[cache_key] = result
    return result


@app.post("/api/compare")
async def compare_optimization(req: OptimizeRequest):
    """Run both classical and quantum optimization for comparison."""
    symbols = _get_tier_symbols(req.tier)
    stats = compute_statistics(symbols)
    mu, sigma = _build_mu_sigma(symbols, stats)

    # Classical
    classical = markowitz_optimize(mu, sigma, req.k, req.q)
    classical_weights_dict = {symbols[i]: round(float(classical["weights"][i]), 4) for i in range(len(symbols))}
    top_k_indices = np.argsort(-np.array(classical["weights"]))[: req.k]

    # Quantum
    qaoa_result = solve_qaoa(mu, sigma, req.k, req.q, req.depth, req.restarts)
    bf_result = brute_force_optimal(mu, sigma, req.k, req.q)
    cost_gap = (
        abs(qaoa_result["objective_value"] - bf_result["qubo_objective_value"])
        / max(abs(bf_result["qubo_objective_value"]), 1e-10)
        * 100
    )

    # Quantum weights
    q_selected_indices = qaoa_result["selected_indices"]
    q_weights_dict = {symbols[i]: round(1.0 / len(q_selected_indices), 4) for i in q_selected_indices}
    for i, s in enumerate(symbols):
        if i not in q_selected_indices:
            q_weights_dict[s] = 0.0

    return {
        "symbols": symbols,
        "tier": req.tier,
        "k": req.k,
        "q": req.q,
        "classical": {
            "weights": classical_weights_dict,
            "portfolio_return": classical["portfolio_return"],
            "portfolio_risk": classical["portfolio_risk"],
            "portfolio_sharpe": classical["portfolio_sharpe"],
            "sharpe_ratio": classical["portfolio_sharpe"],
            "efficient_frontier": classical["efficient_frontier"],
            "selected_stocks": [symbols[i] for i in top_k_indices],
        },
        "quantum": {
            "weights": q_weights_dict,
            "selected_indices": qaoa_result["selected_indices"],
            "selected_stocks": [symbols[i] for i in qaoa_result["selected_indices"]],
            "portfolio_return": qaoa_result["portfolio_return"],
            "portfolio_risk": qaoa_result["portfolio_risk"],
            "portfolio_sharpe": qaoa_result["portfolio_sharpe"],
            "sharpe_ratio": qaoa_result["portfolio_sharpe"],
            "objective_value": qaoa_result["objective_value"],
            "qubo_energy": qaoa_result["objective_value"],
            "optimal_energy": qaoa_result["objective_value"],
            "cost_gap": round(cost_gap, 4),
            "n_qubits": qaoa_result["qaoa_details"]["n_qubits"],
        },
        "bruteforce": {
            "selected_indices": bf_result["selected_indices"],
            "selected_stocks": [symbols[i] for i in bf_result["selected_indices"]],
            "portfolio_return": bf_result["portfolio_return"],
            "portfolio_risk": bf_result["portfolio_risk"],
            "portfolio_sharpe": bf_result["portfolio_sharpe"],
            "sharpe_ratio": bf_result["portfolio_sharpe"],
            "qubo_energy": bf_result["qubo_objective_value"],
            "optimal_energy": bf_result["qubo_objective_value"],
        },
        "efficient_frontier": classical["efficient_frontier"],
    }


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    html_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    return {"message": "Frontend not built yet. Use ./docs for API."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8006, reload=True)
