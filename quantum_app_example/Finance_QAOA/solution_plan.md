# Solution Plan — Finance_QAOA（量子组合投资优化平台）

> 本文件对应 `experiment-pipeline` Stage 1 的规划产物。

## 1. 问题与目标

| 项 | 内容 |
|----|------|
| 任务 | 量子组合优化：从 DOW 成分股中选 k 支，平衡收益与风险 |
| 量子方法 | QAOA（p=2 层，5 restarts，COBYLA），cqlib StatevectorSimulator；组合选择建模为 QUBO |
| 经典基线 | Markowitz 均值-方差优化（连续权重）+ 暴力二值枚举（精确对比） |
| 主指标 | cost_gap_percent（越低越好，0% = 与暴力最优一致） |
| 编码 | 每支股票 1 qubit，x_i = 是否选入组合 |

## 2. 阶段划分

### Stage 1 — Scope & Baseline ✅
- 需求：见 `artifacts/requirements.json`
- 基线：Markowitz + 暴力枚举，见 `artifacts/baseline_report.json`

### Stage 2 — Quantum Method ✅
- QAOA 实现：见 `backend/qaoa_solver.py`、`backend/qubo_model.py`
- 对比：见 `artifacts/quantum_report.json`

### Stage 3 — Application Packaging ✅
- 后端：Python FastAPI，端口 8006（实测用 8106 避让）
- 前端（本地预览）：CDN HTML + app.js，见 `frontend/`
- 前端（天衍云 SFC）：见 `qccp-page-output/financeQaoa/`

### Stage 4 — Verification & Handoff
- 验证报告：见 `verification_report.md`

## 3. 成功信号（实测）

| # | 成功信号 | 实测 | 状态 |
|---|---------|------|------|
| 1 | 5-8 股 tier QAOA gap 0% | demo=0%，standard=0% | ✅ |
| 2 | 12 股（full）可扩展产出可行组合 | 产出可行组合（gap 125.4%） | ⚠️ 部分满足 |
| 3 | 小 tier QAOA Sharpe 与经典可比 | demo Sharpe 0.89 vs 经典 0.91 | ✅ |

> 诚实说明：full tier（12 qubit）出现 125.4% gap，QAOA 在 p=2/restarts=5 下未找到最优——这是 QAOA 启发式在大规模组合问题上的已知局限，详见 verification_report。

## 4. 验证检查清单

- [x] 基线已建立（Markowitz + 暴力枚举）
- [x] 量子结果与基线对比（同 task/data/metric，3 tier）
- [x] 后端 API/前端/部署证据齐备
- [x] 局限已记录（full tier gap、仅模拟器）

## 5. 依赖与部署边界

| 项 | 内容 |
|----|------|
| 运行环境 | conda env `evos`（Python 3.12，cqlib/fastapi/numpy/pandas/scipy） |
| 后端语言 | Python FastAPI |
| 端口 | 8006（默认） |
| 数据 | `data/*.csv`（12 支 DOW 股 2018-2022，离线） |
| 部署边界 | 本地 demo 用 FastAPI serve 前端；天衍云集成走 SFC，**未集成进 qccp-web** |
| 量子硬件 | 仅模拟器，**非真实硬件** |
