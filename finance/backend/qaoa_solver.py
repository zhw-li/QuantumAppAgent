"""
QAOA求解器模块 — 基于cqlib SDK

关键实现:
- 多次随机重启(首次零初始化+后续随机)
- Top-k可行解搜索(最高概率解≠最优可行解)
- COBYLA优化器
- 自适应QAOA深度: 5股p=2, 8股p=3, 12股p=3
"""
import numpy as np
from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator
from scipy.optimize import minimize

from .qubo_model import build_portfolio_qubo, evaluate_qubo, evaluate_objective


def build_qaoa_circuit(n_qubits, linear, quadratic, depth):
    """
    Build QAOA ansatz circuit with cqlib.

    CRITICAL cqlib rules:
    - Parameters MUST be declared at Circuit creation
    - assign_parameters returns a NEW circuit
    - Bitstring order: bits[i] = qubit i (FORWARD, NOT Qiskit reverse)
    """
    param_names = []
    for layer in range(depth):
        param_names.extend([f"gamma_{layer}", f"beta_{layer}"])

    circuit = Circuit(n_qubits, parameters=param_names)

    # Initial superposition
    for q in range(n_qubits):
        circuit.h(q)

    for layer in range(depth):
        gamma = Parameter(f"gamma_{layer}")
        beta = Parameter(f"beta_{layer}")

        # Cost unitary: Z terms
        for qi, coeff in linear.items():
            circuit.rz(qi, 2.0 * coeff * gamma)

        # Cost unitary: ZZ terms via CNOT-RZ-CNOT decomposition
        for (qi, qj), coeff in quadratic.items():
            circuit.cx(qi, qj)
            circuit.rz(qj, 2.0 * coeff * gamma)
            circuit.cx(qi, qj)

        # Mixer unitary
        for q in range(n_qubits):
            circuit.rx(q, 2.0 * beta)

    circuit.measure_all()
    return circuit, param_names


def compute_expectation(
    params, circuit, param_names, n_qubits, linear, quadratic, offset=0.0
):
    """Compute QUBO expectation value from statevector."""
    bound = circuit.assign_parameters(dict(zip(param_names, params)))
    probs = StatevectorSimulator(circuit=bound).measure()

    expectation = 0.0
    for bits, prob in probs.items():
        if prob < 1e-15:
            continue
        # Forward bitstring order: bits[i] = qubit i (NOT Qiskit reverse)
        x = [int(bits[i]) for i in range(n_qubits)]

        value = offset
        value += sum(coeff * x[i] for i, coeff in linear.items())
        value += sum(coeff * x[i] * x[j] for (i, j), coeff in quadratic.items())
        expectation += prob * value

    return expectation


def _get_adaptive_depth(n_qubits):
    """Adaptive QAOA depth based on problem size."""
    if n_qubits <= 5:
        return 2
    elif n_qubits <= 8:
        return 3
    else:
        return 3


def solve_qaoa(mu, sigma, k, q=0.5, depth=None, restarts=5, max_iter=300):
    """
    Solve portfolio selection using QAOA.

    Uses multi-restart COBYLA optimization with top-k feasible solution search.

    Returns dict with: solution, objective_value, selected_indices,
                       portfolio_return/risk/sharpe, qaoa_details
    """
    qubo = build_portfolio_qubo(mu, sigma, k, q)
    linear = qubo["linear"]
    quadratic = qubo["quadratic"]
    offset = qubo["offset"]
    n = qubo["n_qubits"]
    raw_linear = qubo["raw_linear"]
    raw_quadratic = qubo["raw_quadratic"]
    raw_offset = qubo["raw_offset"]

    if depth is None:
        depth = _get_adaptive_depth(n)

    circuit, param_names = build_qaoa_circuit(n, linear, quadratic, depth)

    best_cost = float("inf")
    best_params = None

    for restart in range(restarts):
        if restart == 0:
            x0 = np.zeros(len(param_names))
        else:
            x0 = np.random.uniform(0, np.pi, len(param_names))

        result = minimize(
            compute_expectation,
            x0,
            args=(circuit, param_names, n, linear, quadratic, offset),
            method="COBYLA",
            options={"maxiter": max_iter, "rhobeg": 0.5},
        )

        if result.fun < best_cost:
            best_cost = result.fun
            best_params = result.x

    # Sample from optimal circuit for top-k feasible solution search
    bound = circuit.assign_parameters(dict(zip(param_names, best_params)))
    probs = StatevectorSimulator(circuit=bound).measure()

    # Sort by probability descending
    sorted_probs = sorted(probs.items(), key=lambda x: -x[1])

    # Top-k feasible solution search: find BEST feasible (not just first)
    best_feasible = None
    best_feasible_raw_qubo = float("inf")
    top_10_bitstrings = []

    for idx, (bits, prob) in enumerate(sorted_probs[:50]):
        x = [int(bits[i]) for i in range(n)]
        if idx < 10:
            top_10_bitstrings.append([bits, float(prob)])

        # Check feasibility: sum(x) == k
        if sum(x) == k:
            raw_qubo_val = evaluate_qubo(x, raw_linear, raw_quadratic, raw_offset)
            if raw_qubo_val < best_feasible_raw_qubo:
                best_feasible_raw_qubo = raw_qubo_val
                best_feasible = x

    # Fallback: select top-k by return
    if best_feasible is None:
        indices = np.argsort(-mu)[:k].tolist()
        best_feasible = [1 if i in indices else 0 for i in range(n)]
        best_feasible_raw_qubo = evaluate_qubo(
            best_feasible, raw_linear, raw_quadratic, raw_offset
        )

    selected_indices = [i for i, v in enumerate(best_feasible) if v == 1]

    # Compute portfolio metrics: x'mu - q*x'Sigma*x, sqrt(x'Sigma*x)
    x_arr = np.array(best_feasible, dtype=float)
    port_return = float(x_arr @ mu)
    port_risk = float(np.sqrt(x_arr @ sigma @ x_arr))
    port_sharpe = float(port_return / port_risk) if port_risk > 1e-10 else 0.0

    return {
        "solution": best_feasible,
        "objective_value": float(best_feasible_raw_qubo),
        "selected_indices": selected_indices,
        "portfolio_return": port_return,
        "portfolio_risk": port_risk,
        "portfolio_sharpe": port_sharpe,
        "qaoa_details": {
            "depth": depth,
            "restarts": restarts,
            "max_iter": max_iter,
            "best_params": best_params.tolist() if best_params is not None else None,
            "penalty": qubo["penalty"],
            "norm_factor": qubo["norm_factor"],
            "n_qubits": n,
            "probability_top10": top_10_bitstrings,
        },
    }


def brute_force_optimal(mu, sigma, k, q=0.5):
    """
    Brute-force search for the optimal portfolio selection.

    Returns dict with: solution, selected_indices, objective_value,
                       qubo_objective_value, portfolio_return/risk/sharpe
    """
    from itertools import combinations

    n = len(mu)
    qubo = build_portfolio_qubo(mu, sigma, k, q)
    raw_linear = qubo["raw_linear"]
    raw_quadratic = qubo["raw_quadratic"]
    raw_offset = qubo["raw_offset"]

    best_obj = -float("inf")
    best_combo = None

    for combo in combinations(range(n), k):
        x = np.zeros(n)
        x[list(combo)] = 1
        obj = x @ mu - q * x @ sigma @ x
        if obj > best_obj:
            best_obj = obj
            best_combo = list(combo)

    # Compute QUBO objective for this solution
    solution = [1 if i in best_combo else 0 for i in range(n)]
    qubo_val = evaluate_qubo(solution, raw_linear, raw_quadratic, raw_offset)

    # Portfolio metrics
    x_arr = np.array(solution, dtype=float)
    port_return = float(x_arr @ mu)
    port_risk = float(np.sqrt(x_arr @ sigma @ x_arr))
    port_sharpe = float(port_return / port_risk) if port_risk > 1e-10 else 0.0

    return {
        "solution": solution,
        "selected_indices": best_combo,
        "objective_value": float(best_obj),
        "qubo_objective_value": float(qubo_val),
        "portfolio_return": port_return,
        "portfolio_risk": port_risk,
        "portfolio_sharpe": port_sharpe,
    }
