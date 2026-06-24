"""
QAOA MaxCut求解器 — 基于cqlib SDK实现

关键cqlib模式:
    - from cqlib import Circuit, Parameter  (顶级导入)
    - from cqlib.simulator import StatevectorSimulator  (子模块导入)
    - Circuit参数必须在创建时声明: Circuit(n_qubits, parameters=names)
    - assign_parameters返回新Circuit
    - measure_all()必须在measure()之前调用
    - 比特串顺序: REVERSE (同Qiskit), key[n_qubits-1-q] = qubit q
    - ZZ分解: cx(qi,qj) → rz(qj, 2*coeff*gamma) → cx(qi,qj)
"""

import time
from typing import Dict, List, Optional, Tuple

import numpy as np
from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator
from scipy.optimize import minimize

from graph_utils import (
    brute_force_maxcut,
    cut_value,
    edges_to_qubo,
    get_cut_edges,
    normalize_qubo,
    total_edge_weight,
)


# ============================================================
# QAOA电路构建
# ============================================================

def add_zz(circuit: Circuit, qi: int, qj: int, coeff: float, gamma: Parameter):
    """
    ZZ演化门: CNOT-RZ-CNOT分解

    exp(-i * coeff * gamma * Z_i Z_j) 的实现:
        CNOT(qi, qj) → RZ(qj, 2*coeff*gamma) → CNOT(qi, qj)
    """
    circuit.cx(qi, qj)
    circuit.rz(qj, 2.0 * coeff * gamma)
    circuit.cx(qi, qj)


def add_z(circuit: Circuit, qi: int, coeff: float, gamma: Parameter):
    """单Z旋转: exp(-i * coeff * gamma * Z_i) → RZ(qi, 2*coeff*gamma)"""
    circuit.rz(qi, 2.0 * coeff * gamma)


def build_qaoa_circuit(
    n_qubits: int,
    linear: Dict[int, float],
    quadratic: Dict[Tuple[int, int], float],
    depth: int,
) -> Tuple[Circuit, List[str]]:
    """
    构建QAOA电路

    Args:
        n_qubits: 量子比特数
        linear: QUBO线性项系数 {qubit: coeff}
        quadratic: QUBO二次项系数 {(qi, qj): coeff}
        depth: QAOA层数（p值）

    Returns:
        circuit: 构建的QAOA电路
        param_names: 参数名列表（按顺序）
    """
    # 参数命名：gamma_0, beta_0, gamma_1, beta_1, ...
    param_names = []
    for layer in range(depth):
        param_names.append(f"gamma_{layer}")
        param_names.append(f"beta_{layer}")

    # 创建电路，声明参数名
    circuit = Circuit(n_qubits, parameters=param_names)

    # 初始Hadamard门，创建均匀叠加态
    for q in range(n_qubits):
        circuit.h(q)

    # 逐层构建QAOA
    for layer in range(depth):
        gamma = Parameter(f"gamma_{layer}")
        beta = Parameter(f"beta_{layer}")

        # --- Cost层: 编码QUBO问题 ---
        # Z旋转（线性项）
        for qi, coeff in linear.items():
            add_z(circuit, qi, coeff, gamma)
        # ZZ旋转（二次项）
        for (qi, qj), coeff in quadratic.items():
            add_zz(circuit, qi, qj, coeff, gamma)

        # --- Mixer层: RX旋转 ---
        for q in range(n_qubits):
            circuit.rx(q, 2.0 * beta)

    # 测量所有量子比特
    circuit.measure_all()

    return circuit, param_names


# ============================================================
# 期望值计算
# ============================================================

def compute_expectation(
    params: np.ndarray,
    circuit: Circuit,
    param_names: List[str],
    n_qubits: int,
    linear: Dict[int, float],
    quadratic: Dict[Tuple[int, int], float],
    offset: float = 0.0,
) -> float:
    """
    计算QAOA电路在给定参数下的QUBO期望值

    使用StatevectorSimulator精确模拟，通过概率分布计算期望。
    比特串约定: key[n_qubits-1-q] = qubit q（cqlib反向顺序，同Qiskit）
    """
    # 绑定参数，得到新电路
    param_dict = dict(zip(param_names, params))
    bound_circuit = circuit.assign_parameters(param_dict)

    # 模拟测量得到概率分布
    probs = StatevectorSimulator(circuit=bound_circuit).measure()

    # 计算QUBO期望值
    exp_val = 0.0
    for bits, prob in probs.items():
        if prob < 1e-15:
            continue
        # cqlib比特串: key[n_qubits-1-q] = qubit q（反向顺序，同Qiskit）
        x = [int(bits[n_qubits - 1 - i]) for i in range(n_qubits)]
        val = offset
        val += sum(coeff * x[i] for i, coeff in linear.items())
        val += sum(coeff * x[i] * x[j] for (i, j), coeff in quadratic.items())
        exp_val += prob * val

    return exp_val


# ============================================================
# 解码与后处理
# ============================================================

def decode_bitstring(bits: str, n_qubits: int) -> List[int]:
    """将比特串解码为分配列表（cqlib反向顺序: key[n_qubits-1-q] = qubit q）"""
    return [int(bits[n_qubits - 1 - i]) for i in range(n_qubits)]


def find_best_feasible(
    probs: Dict[str, float],
    n_qubits: int,
    edges: List[List[int]],
    top_k: int = 50,
) -> Tuple[float, List[int], List[List[int]], float]:
    """
    从概率分布中搜索最优可行切割方案

    注意：概率最高的比特串不一定是切割值最大的！
    需要在top-k中搜索。

    Args:
        probs: 比特串概率分布
        n_qubits: 量子比特数
        edges: 图的边列表
        top_k: 搜索范围

    Returns:
        best_cut: 最优切割值
        best_partition: 最优分配
        cut_edges: 被切割的边
        best_prob: 最优解的概率
    """
    # 按概率降序排列
    sorted_bits = sorted(probs.items(), key=lambda x: -x[1])

    best_cut = -float("inf")
    best_partition = None
    best_prob = 0.0

    for bits, prob in sorted_bits[:top_k]:
        x = decode_bitstring(bits, n_qubits)
        cv = cut_value(x, edges)
        if cv > best_cut:
            best_cut = cv
            best_partition = x
            best_prob = prob

    cut_edges_list = get_cut_edges(best_partition, edges)
    return best_cut, best_partition, cut_edges_list, best_prob


# ============================================================
# 主求解函数
# ============================================================

def solve_maxcut_qaoa(
    edges: List[List[int]],
    n_nodes: int,
    depth: int = 2,
    restarts: int = 5,
    maxiter: int = 300,
) -> Dict:
    """
    使用QAOA求解MaxCut问题

    完整流程:
        1. 从图构建QUBO模型
        2. 归一化QUBO系数
        3. 构建QAOA电路
        4. 多次随机重启优化参数
        5. 采样最优电路
        6. 解码top-k比特串，搜索最优可行解
        7. 与暴力搜索对比

    Args:
        edges: 边列表 [[src, tgt, weight], ...]
        n_nodes: 节点数
        depth: QAOA层数（p值）
        restarts: 随机重启次数
        maxiter: 每次重启的最大迭代次数

    Returns:
        完整结果字典
    """
    start_time = time.time()

    # ---- Step 1: 构建QUBO ----
    linear, quadratic, offset = edges_to_qubo(edges, n_nodes)
    total_w = total_edge_weight(edges)

    # ---- Step 2: 归一化QUBO ----
    norm_linear, norm_quadratic, norm_offset, norm_factor = normalize_qubo(
        linear, quadratic, offset
    )

    # ---- Step 3: 构建QAOA电路 ----
    circuit, param_names = build_qaoa_circuit(
        n_nodes, norm_linear, norm_quadratic, depth
    )

    # ---- Step 4: 多次随机重启优化 ----
    best_exp = float("inf")
    best_params = None
    optimization_history = []
    n_params = len(param_names)

    for restart in range(restarts):
        init_params = np.random.uniform(0, np.pi, n_params)

        # 记录每次迭代的期望值
        iter_history = []

        def make_callback(hist, best_tracker):
            """创建回调函数，避免nonlocal语法问题"""
            def callback(xk):
                exp_val = compute_expectation(
                    xk, circuit, param_names, n_nodes,
                    norm_linear, norm_quadratic, norm_offset
                )
                hist.append(exp_val)
                if exp_val < best_tracker["exp"]:
                    best_tracker["exp"] = exp_val
                    best_tracker["params"] = xk.copy()
            return callback

        best_tracker = {"exp": best_exp, "params": best_params}
        callback = make_callback(iter_history, best_tracker)

        result = minimize(
            compute_expectation,
            init_params,
            args=(circuit, param_names, n_nodes, norm_linear, norm_quadratic, norm_offset),
            method="COBYLA",
            options={"maxiter": maxiter, "rhobeg": 0.5},
            callback=callback,
        )

        optimization_history.extend(iter_history)
        # 更新最优结果
        if best_tracker["exp"] < best_exp:
            best_exp = best_tracker["exp"]
            best_params = best_tracker["params"]

    # ---- Step 5: 用最优参数采样 ----
    param_dict = dict(zip(param_names, best_params))
    optimal_circuit = circuit.assign_parameters(param_dict)
    probs = StatevectorSimulator(circuit=optimal_circuit).measure()

    # ---- Step 6: 搜索最优可行解 ----
    qaoa_cut, best_partition, cut_edges_list, best_prob = find_best_feasible(
        probs, n_nodes, edges, top_k=50
    )

    # ---- Step 7: 暴力搜索对比 ----
    bf_result = brute_force_maxcut(edges, n_nodes)
    optimal_cut = bf_result["optimal_cut"]

    # 计算cost_gap
    if optimal_cut > 0:
        cost_gap = (optimal_cut - qaoa_cut) / optimal_cut * 100.0
    else:
        cost_gap = 0.0

    elapsed = time.time() - start_time

    # ---- 整理结果 ----
    # 还原QUBO期望值到原始尺度
    real_qubo_exp = best_exp * norm_factor

    # 构建QAOA参数字典
    qaoa_params_dict = {}
    for i, name in enumerate(param_names):
        qaoa_params_dict[name] = float(best_params[i])

    # Top-10 比特串概率
    sorted_probs = sorted(probs.items(), key=lambda x: -x[1])[:10]
    top_probabilities = [
        {"bitstring": bits, "probability": float(prob), "cut_value": cut_value(decode_bitstring(bits, n_nodes), edges)}
        for bits, prob in sorted_probs
    ]

    return {
        # QAOA求解结果
        "qaoa_cut": qaoa_cut,
        "optimal_cut": optimal_cut,
        "cost_gap_percent": round(cost_gap, 2),
        "best_partition": best_partition,
        "cut_edges": cut_edges_list,
        "best_probability": float(best_prob),
        # 暴力搜索参考
        "brute_force": {
            "optimal_cut": optimal_cut,
            "n_optimal_partitions": len(bf_result["optimal_partitions"]),
            "best_partition": bf_result["best_partition"],
            "n_evaluated": bf_result["n_evaluated"],
        },
        # QUBO信息
        "qubo": {
            "n_qubits": n_nodes,
            "n_linear_terms": len(norm_linear),
            "n_quadratic_terms": len(norm_quadratic),
            "norm_factor": norm_factor,
            "qubo_expectation": float(real_qubo_exp),
        },
        # 电路信息
        "circuit_depth": depth,
        "n_qubits": n_nodes,
        "n_params": n_params,
        "qaoa_params": qaoa_params_dict,
        # 优化过程
        "optimization_history": [float(v) for v in optimization_history],
        "restarts": restarts,
        "maxiter": maxiter,
        # Top概率分布
        "top_probabilities": top_probabilities,
        # 性能
        "elapsed_time": round(elapsed, 3),
        "graph_info": {
            "n_nodes": n_nodes,
            "n_edges": len(edges),
            "total_weight": total_w,
        },
    }
