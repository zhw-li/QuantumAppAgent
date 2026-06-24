# MaxCut_QAOA — 最大割量子优化平台

基于 QAOA（Quantum Approximate Optimization Algorithm，量子近似优化算法）求解 MaxCut（最大割）问题，与经典暴力搜索对比。

## 概述

本平台使用 cqlib SDK 实现 QAOA 算法求解 MaxCut 问题。MaxCut 是图论经典 NP-hard 问题：将图节点分成两部分，使跨越切分的边权重和最大。问题被建模为 QUBO，经归一化后由 QAOA 在量子电路上求解，与暴力枚举的经典精确解对比。

## 核心算法

### 量子方法 (QAOA)
1. **QUBO 建模**: MaxCut → 最大化跨越切分的边权重和，转为 QUBO（`f(x)=Σ w_ij·(2x_ix_j − x_i − x_j) = −cut(x)`，最优切割值 = −min f(x)）
2. **归一化**: QUBO 归一化改善 QAOA 优化景观
3. **量子电路**: p 层 QAOA ansatz（H⊗n 初始化 → 代价 ZZ/Z 项 → 混合 RX），ZZ 门用 CNOT-RZ-CNOT 分解
4. **优化器**: COBYLA（scipy），多 restart；后处理从概率分布搜索 top-k 可行解

### 经典基线（暴力枚举）
- 枚举所有 2^n 种节点划分，取最大切分值（n≤8 可行）

## 实验结果（3 预设图，QAOA p=2, restarts=5）

| 图 | 节点/边 | qubit | QAOA cut | 暴力最优 | gap(%) | 耗时 |
|----|---------|-------|---------|---------|--------|------|
| simple_4 | 4/4 | 4 | 3.0 | 3.0 | **0.0%** | 13.09s |
| medium_6 | 6/8 | 6 | 8.0 | 8.0 | **0.0%** | 6.72s |
| large_8 | 8/16 | 8 | 11.0 | 11.0 | **0.0%** | 17.71s |

**关键发现**: QAOA 在全部 3 个预设图（4-8 qubit）上找到精确最优 MaxCut（gap 0%）。详见 `artifacts/quantum_report.json`。

## 技术栈

### 量子算法
- **cqlib SDK**: 量子电路（`Circuit`/`Parameter`）、`StatevectorSimulator`
- **numpy/scipy**: QUBO 建模、COBYLA 优化

### 后端
- **FastAPI**: 5 个 API 端点，端口 8006

### 前端（CDN 预览版）
- Vue 3 CDN + Element Plus CDN + ECharts CDN

### 天衍云集成版
- Vue 3 SFC + Element Plus + Vue I18n，详见 `qccp-page-output/maxcutQaoa/INTEGRATE.md`

## 快速启动

```bash
pip install cqlib numpy scipy fastapi uvicorn
cd backend
python main.py
# 访问 http://localhost:8006/
```

## 复现实验报告

```bash
# 启动后端后，3 预设图实测
for g in simple_4 medium_6 large_8; do
  curl -X POST http://localhost:8006/api/solve -H "Content-Type: application/json" \
    -d "{\"graph_name\":\"$g\",\"depth\":2,\"restarts\":5,\"maxiter\":300}"
done
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/graphs` | 预设图列表 |
| GET | `/api/graph/{name}` | 指定预设图数据 |
| POST | `/api/solve` | QAOA 求解 MaxCut |
| POST | `/api/brute-force` | 暴力搜索最优 |

## 标准产物（7 件套）

| 产物 | 路径 | 说明 |
|------|------|------|
| requirements.json | `artifacts/requirements.json` | 结构化需求 |
| solution_plan.md | `solution_plan.md` | 交付计划与门禁 |
| baseline_report.json | `artifacts/baseline_report.json` | 经典基线（暴力枚举） |
| quantum_report.json | `artifacts/quantum_report.json` | 量子方法（QAOA，3 图） |
| verification_report.md | `verification_report.md` | 验证报告 |
| README.md | `README.md` | 本文件 |
| INTEGRATE.md | `qccp-page-output/maxcutQaoa/INTEGRATE.md` | 天衍云集成说明 |

## 项目结构

```
MaxCut_QAOA/
├── backend/
│   ├── main.py            # FastAPI 服务（端口 8006，含 QAOA 入口）
│   ├── graph_utils.py     # 图定义、QUBO 建模、暴力搜索
│   ├── maxcut_solver.py   # QAOA MaxCut 求解器（cqlib）
│   └── requirements.txt
├── frontend/
│   ├── index.html         # CDN 预览页面（Vue 3 + ECharts）
│   └── static/{app.js, style.css}
├── qccp-page-output/maxcutQaoa/  # 天衍云 SFC 页面
│   ├── project-files/src/{views,api}/
│   └── INTEGRATE.md
├── artifacts/             # 标准报告产物
│   ├── requirements.json
│   ├── baseline_report.json
│   ├── quantum_report.json
│   └── maxcut_experiment_3graphs.json
├── solution_plan.md
├── verification_report.md
└── README.md
```

## 局限性

- 仅模拟器（cqlib StatevectorSimulator），非真实硬件
- 3 个预设图规模小（4-8 节点），对 QAOA 有利；更密/更大图表现可能不同
- statevector 模拟（非采样），无测量统计噪声
