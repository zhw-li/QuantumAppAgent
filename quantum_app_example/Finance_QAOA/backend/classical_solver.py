import numpy as np
from scipy.optimize import minimize


def markowitz_optimize(mu, sigma, k, q=0.5):
    """
    Continuous Markowitz optimization for comparison.
    Minimize -x'mu + q * x'Sigma*x subject to sum(x) = 1, x >= 0

    Returns dict with portfolio weights and metrics.
    """
    n = len(mu)

    def neg_sharpe(w):
        ret = w @ mu
        risk = np.sqrt(w @ sigma @ w)
        return -(ret / risk) if risk > 1e-10 else 0

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [(0, 1) for _ in range(n)]

    # Try multiple starting points
    best_result = None
    best_val = float("inf")

    for _ in range(10):
        w0 = np.random.dirichlet(np.ones(n))
        result = minimize(
            neg_sharpe,
            w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000},
        )
        if result.fun < best_val:
            best_val = result.fun
            best_result = result

    weights = best_result.x
    weights = np.maximum(weights, 0)
    weights /= weights.sum()

    port_return = float(weights @ mu)
    port_risk = float(np.sqrt(weights @ sigma @ weights))
    port_sharpe = float(port_return / port_risk) if port_risk > 0 else 0

    # Also compute efficient frontier
    frontier = compute_efficient_frontier(mu, sigma, n_points=20)

    return {
        "weights": weights.tolist(),
        "portfolio_return": port_return,
        "portfolio_risk": port_risk,
        "portfolio_sharpe": port_sharpe,
        "efficient_frontier": frontier,
    }


def compute_efficient_frontier(mu, sigma, n_points=20):
    """Compute efficient frontier points."""
    n = len(mu)
    min_ret = float(np.min(mu))
    max_ret = float(np.max(mu))
    target_returns = np.linspace(min_ret, max_ret, n_points)

    frontier = []
    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, t=target: w @ mu - t},
        ]
        bounds = [(0, 1) for _ in range(n)]

        w0 = np.ones(n) / n
        result = minimize(
            lambda w: w @ sigma @ w,
            w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500},
        )

        if result.success:
            w = result.x
            frontier.append(
                {"return": float(w @ mu), "risk": float(np.sqrt(w @ sigma @ w))}
            )

    return frontier
