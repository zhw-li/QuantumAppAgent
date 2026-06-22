"""
图工具模块：预设图定义、MaxCut QUBO建模、暴力搜索最优解

MaxCut QUBO推导:
    - 二值变量 x_i 表示顶点 i 的分区 (0 或 1)
    - 切割值: cut(x) = sum_{(i,j)∈E} w_{ij} * (x_i XOR x_j)
                           = sum_{(i,j)∈E} w_{ij} * (x_i + x_j - 2*x_i*x_j)
    - QUBO最小化形式: f(x) = sum_{(i,j)∈E} w_{ij} * (2*x_i*x_j - x_i - x_j) = -cut(x)
    - 因此: minimize f(x) ⟺ maximize cut(x), 且 cut(x) = -f(x)
"""

from itertools import product
from typing import Dict, List, Optional, Tuple

import numpy as np


# ============================================================
# 预设图定义
# ============================================================

PRESET_GRAPHS = {
    "simple_4": {
        "name": "simple_4",
        "n_nodes": 4,
        "edges": [[0, 1, 1], [1, 2, 1], [2, 0, 1], [2, 3, 1]],
        "description": "三角形 + 悬挂节点，最优切割值=3",
    },
    "medium_6": {
        "name": "medium_6",
        "n_nodes": 6,
        "edges": [
            [0, 1, 1], [1, 2, 1], [2, 3, 1],
            [3, 4, 1], [4, 5, 1], [5, 0, 1],
            [0, 3, 1], [1, 4, 1],
        ],
        "description": "环 + 对角线，最优切割值=8",
    },
    "large_8": {
        "name": "large_8",
        "n_nodes": 8,
        "edges": [
            [0, 1, 1], [0, 2, 1], [0, 3, 1],
            [1, 2, 1], [1, 4, 1], [1, 5, 1],
            [2, 3, 1], [2, 4, 1], [2, 6, 1],
            [3, 6, 1], [3, 7, 1],
            [4, 5, 1], [4, 6, 1],
            [5, 6, 1], [5, 7, 1],
            [6, 7, 1],
        ],
        "description": "8节点稠密图，最优切割值=11",
    },
}


def get_graph(name: str) -> Optional[dict]:
    """获取预设图数据，不存在则返回None"""
    return PRESET_GRAPHS.get(name)


def list_graphs() -> List[dict]:
    """列出所有预设图的元信息（不含边列表，仅概要）"""
    return [
        {"name": g["name"], "n_nodes": g["n_nodes"],
         "n_edges": len(g["edges"]), "description": g["description"]}
        for g in PRESET_GRAPHS.values()
    ]


# ============================================================
# MaxCut QUBO建模
# ============================================================

def edges_to_qubo(
    edges: List[List[int]], n_nodes: int
) -> Tuple[Dict[int, float], Dict[Tuple[int, int], float], float]:
    """
    从边列表构建MaxCut的QUBO模型

    QUBO: f(x) = sum_{(i,j)∈E} w_{ij} * (2*x_i*x_j - x_i - x_j)
        = x^T Q x + l^T x + offset

    Args:
        edges: 边列表，每条边为 [source, target, weight]
        n_nodes: �点数

    Returns:
        linear: 线性项系数 {qubit: coeff}
        quadratic: 二次项系数 {(qubit_i, qubit_j): coeff}
        offset: 常数偏移（MaxCut中为0）
    """
    linear: Dict[int, float] = {}
    quadratic: Dict[Tuple[int, int], float] = {}

    for src, tgt, w in edges:
        # 线性项: -w 对每个端点
        linear[src] = linear.get(src, 0.0) - w
        linear[tgt] = linear.get(tgt, 0.0) - w
        # 二次项: 2*w
        key = (min(src, tgt), max(src, tgt))
        quadratic[key] = quadratic.get(key, 0.0) + 2.0 * w

    return linear, quadratic, 0.0  # MaxCut offset = 0


def normalize_qubo(
    linear: Dict[int, float], quadratic: Dict[Tuple[int, int], float], offset: float = 0.0
) -> Tuple[Dict[int, float], Dict[Tuple[int, int], float], float, float]:
    """
    将QUBO系数归一化到[-1, 1]范围，提升QAOA数值稳定性

    Returns:
        norm_linear: 归一化后的线性项
        norm_quadratic: 归一化后的二次项
        norm_offset: 归一化后的偏移
        norm_factor: 归一化因子（用于还原真实值）
    """
    all_vals = list(linear.values()) + list(quadratic.values())
    if not all_vals:
        return linear, quadratic, offset, 1.0
    max_abs = max(abs(v) for v in all_vals)
    if max_abs == 0:
        return linear, quadratic, offset, 1.0

    norm_factor = max_abs
    norm_linear = {k: v / norm_factor for k, v in linear.items()}
    norm_quadratic = {k: v / norm_factor for k, v in quadratic.items()}
    norm_offset = offset / norm_factor

    return norm_linear, norm_quadratic, norm_offset, norm_factor


def qubo_value(
    x: List[int],
    linear: Dict[int, float],
    quadratic: Dict[Tuple[int, int], float],
    offset: float = 0.0,
) -> float:
    """计算给定分配下的QUBO值"""
    val = offset
    val += sum(coeff * x[i] for i, coeff in linear.items())
    val += sum(coeff * x[i] * x[j] for (i, j), coeff in quadratic.items())
    return val


def cut_value(x: List[int], edges: List[List[int]]) -> float:
    """
    计算给定分配下的切割值

    cut(x) = sum_{(i,j)∈E} w_{ij} * (x_i XOR x_j)
           = sum_{(i,j)∈E} w_{ij} * (x_i + x_j - 2*x_i*x_j)
    """
    total = 0.0
    for src, tgt, w in edges:
        total += w * (x[src] + x[tgt] - 2 * x[src] * x[tgt])
    return total


def total_edge_weight(edges: List[List[int]]) -> float:
    """计算所有边权重之和"""
    return sum(w for _, _, w in edges)


# ============================================================
# 暴力搜索最优解
# ============================================================

def brute_force_maxcut(
    edges: List[List[int]], n_nodes: int
) -> Dict:
    """
    暴力搜索MaxCut的最优解，遍历所有 2^n 种分配

    Returns:
        {
            "optimal_cut": float,           # 最优切割值
            "optimal_partitions": list,     # 所有达到最优的分配列表
            "best_partition": list,         # 第一个最优分配
            "cut_values": list,             # 所有分配的切割值
            "n_evaluated": int              # 评估的分配总数
        }
    """
    best_cut = -float("inf")
    best_partitions = []
    all_cuts = []

    for assignment in product([0, 1], repeat=n_nodes):
        x = list(assignment)
        cv = cut_value(x, edges)
        all_cuts.append(cv)
        if cv > best_cut:
            best_cut = cv
            best_partitions = [x]
        elif cv == best_cut:
            best_partitions.append(x)

    return {
        "optimal_cut": best_cut,
        "optimal_partitions": best_partitions,
        "best_partition": best_partitions[0],
        "cut_values": all_cuts,
        "n_evaluated": 2**n_nodes,
    }


def get_cut_edges(x: List[int], edges: List[List[int]]) -> List[List[int]]:
    """获取被切割的边列表"""
    result = []
    for src, tgt, w in edges:
        if x[src] != x[tgt]:
            result.append([src, tgt, w])
    return result
