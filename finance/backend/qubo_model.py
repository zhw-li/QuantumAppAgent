"""
投资组合选择QUBO建模模块

目标: 最大化 f(x) = x'mu - q * x'Sigma*x
QUBO:  最小化 -f(x) + λ * (sum(x) - k)²

策略:
1. 自适应惩罚 λ = max(2·obj_scale·n, 10·obj_scale)
2. QUBO系数归一化到[-1,1]确保QAOA数值稳定
3. 保留原始系数用于目标函数评估
"""
import numpy as np


def build_portfolio_qubo(
    mu: np.ndarray, sigma: np.ndarray, k: int, q: float = 0.5
) -> dict:
    """
    Build QUBO for portfolio selection with adaptive penalty and normalization.
    """
    n = len(mu)

    # Step 1: Build the objective-only QUBO (minimize -f(x))
    obj_linear = {}
    obj_quadratic = {}
    for i in range(n):
        obj_linear[i] = -mu[i] + q * sigma[i, i]
        for j in range(i + 1, n):
            obj_quadratic[(i, j)] = 2 * q * sigma[i, j]

    # Step 2: Scale objective so max |coeff| = 1
    obj_all_vals = list(obj_linear.values()) + list(obj_quadratic.values())
    obj_max = max(abs(v) for v in obj_all_vals) if obj_all_vals else 1.0
    if obj_max < 1e-12:
        obj_max = 1.0

    for i in obj_linear:
        obj_linear[i] = obj_linear[i] / obj_max
    for key in obj_quadratic:
        obj_quadratic[key] = obj_quadratic[key] / obj_max

    # Step 3: Adaptive penalty — ensures constraint dominates objective
    obj_scale = max(float(np.max(np.abs(mu))), q * float(np.max(np.abs(sigma))))
    if obj_scale < 1e-12:
        obj_scale = 1.0
    penalty = max(2 * obj_scale * n, 10 * obj_scale)

    linear = {}
    quadratic = {}
    for i in range(n):
        linear[i] = obj_linear[i] + penalty * (1 - 2 * k)
        for j in range(i + 1, n):
            quadratic[(i, j)] = obj_quadratic[(i, j)] + 2 * penalty

    offset = penalty * k * k

    # Step 4: Normalize to [-1, 1] for QAOA numerical stability
    all_vals = list(linear.values()) + list(quadratic.values())
    norm_factor = max(abs(v) for v in all_vals) if all_vals else 1.0
    if norm_factor < 1e-12:
        norm_factor = 1.0

    linear_norm = {i: v / norm_factor for i, v in linear.items()}
    quadratic_norm = {(i, j): v / norm_factor for (i, j), v in quadratic.items()}
    offset_norm = offset / norm_factor

    return {
        "linear": linear_norm,
        "quadratic": quadratic_norm,
        "offset": offset_norm,
        "penalty": penalty,
        "norm_factor": norm_factor,
        "n_qubits": n,
        # Raw (unnormalized) coefficients for objective evaluation
        "raw_linear": linear,
        "raw_quadratic": quadratic,
        "raw_offset": offset,
    }


def evaluate_qubo(solution, linear, quadratic, offset=0.0):
    """Evaluate QUBO value for a binary solution vector."""
    value = offset
    for i, coeff in linear.items():
        value += coeff * solution[i]
    for (i, j), coeff in quadratic.items():
        value += coeff * solution[i] * solution[j]
    return value


def evaluate_objective(solution, mu, sigma, q):
    """Evaluate original portfolio objective f(x) = x'mu - q*x'Sigma*x."""
    x = np.array(solution)
    return float(x @ mu - q * x @ sigma @ x)
