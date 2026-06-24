# Solution Plan — UC_QAOA（机组组合量子优化平台）

> 本文件对应 `experiment-pipeline` Stage 1 的规划产物。

## 1. 问题与目标

| 项 | 内容 |
|----|------|
| 任务 | 机组组合（Unit Commitment）：决定各发电机组在各时段的 ON/OFF，最小化总燃料成本，满足负载平衡 |
| 量子方法 | QAOA（p=2 层，5 restarts，COBYLA 优化器），cqlib StatevectorSimulator |
| 经典基线 | 暴力枚举所有 2^n 比特串（n≤8 可行） |
| 主指标 | optimality_gap_percent（越低越好，0% = 最优） |
| 编码 | x[i,t] = 机组 i 在时段 t 是否开机，qubit index = i*T + t |

## 2. 阶段划分

### Stage 1 — Scope & Baseline ✅
- 需求：见 `artifacts/requirements.json`
- 基线：暴力枚举（确定性精确解），见 `artifacts/baseline_report.json`

### Stage 2 — Quantum Method ✅
- QAOA 实现：见 `backend/main.py`（`build_qaoa_circuit`、`run_qaoa`、`find_best_feasible`）
- 对比：见 `artifacts/quantum_report.json`

### Stage 3 — Application Packaging ✅
- 后端：Python FastAPI，端口 8001
- 前端（本地预览）：CDN HTML + app.js，见 `frontend/`
- 前端（天衍云 SFC）：见 `qccp-page-output/ucQaoa/`

### Stage 4 — Verification & Handoff
- 验证报告：见 `verification_report.md`

## 3. 成功信号（实测）

| # | 成功信号 | 实测 | 状态 |
|---|---------|------|------|
| 1 | QAOA 全规模返回可行解（负载平衡满足） | 3/3 可行 | ✅ |
| 2 | 4-6 qubit gap ≤ 5% | 4q=0%，6q=0% | ✅ |
| 3 | 8 qubit 可扩展且近最优 | gap=2.16% | ✅ |

## 4. 验证检查清单

- [x] 基线已建立（暴力枚举精确解）
- [x] 量子结果与基线对比（同 task/data/metric，3 规模）
- [x] 后端 API/前端/部署证据齐备
- [x] 局限已记录（8q gap 2.16%、仅模拟器）

## 5. 依赖与部署边界

| 项 | 内容 |
|----|------|
| 运行环境 | conda env `evos`（Python 3.12，cqlib/fastapi/numpy/scipy） |
| 后端语言 | Python FastAPI |
| 端口 | 8001 |
| 部署边界 | 本地 demo 用 FastAPI serve 前端；天衍云集成走 SFC，**未集成进 qccp-web** |
| 量子硬件 | 仅模拟器，**非真实硬件** |
