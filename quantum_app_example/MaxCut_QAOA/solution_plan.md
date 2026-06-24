# Solution Plan — MaxCut_QAOA（最大割量子优化平台）

> 本文件对应 `experiment-pipeline` Stage 1 的规划产物。

## 1. 问题与目标

| 项 | 内容 |
|----|------|
| 任务 | MaxCut：将图节点分成两部分，最大化跨越切分的边权重和 |
| 量子方法 | QAOA（p=2 层，5 restarts，COBYLA 优化器），cqlib StatevectorSimulator |
| 经典基线 | 暴力枚举所有 2^n 种划分 |
| 主指标 | cost_gap_percent（越低越好，0% = 最优） |
| 编码 | 每节点 1 qubit，x_i = 节点 i 在切分的哪一侧 |

## 2. 阶段划分

### Stage 1 — Scope & Baseline ✅
- 需求：见 `artifacts/requirements.json`
- 基线：暴力枚举（精确解），见 `artifacts/baseline_report.json`

### Stage 2 — Quantum Method ✅
- QAOA 实现：见 `maxcut_solver.py`、`graph_utils.py`
- 对比：见 `artifacts/quantum_report.json`

### Stage 3 — Application Packaging ✅
- 后端：Python FastAPI，端口 8006
- 前端（本地预览）：CDN HTML + app.js，见 `frontend/`
- 前端（天衍云 SFC）：见 `qccp-page-output/maxcutQaoa/`

### Stage 4 — Verification & Handoff
- 验证报告：见 `verification_report.md`

## 3. 成功信号（实测）

| # | 成功信号 | 实测 | 状态 |
|---|---------|------|------|
| 1 | QAOA 在 3 个预设图（4-8 qubit）上找到最优 MaxCut（gap 0%） | 3/3 gap=0% | ✅ |
| 2 | QAOA cut 值与暴力最优一致 | simple=3, medium=8, large=11 全一致 | ✅ |
| 3 | QAOA 在 restart/迭代预算内收敛 | 5 restarts 内全部收敛 | ✅ |

## 4. 验证检查清单

- [x] 基线已建立（暴力枚举精确解）
- [x] 量子结果与基线对比（同 task/data/metric，3 图）
- [x] 后端 API/前端/部署证据齐备
- [x] 局限已记录（仅模拟器、小图有利）

## 5. 依赖与部署边界

| 项 | 内容 |
|----|------|
| 运行环境 | conda env `evos`（Python 3.12，cqlib/fastapi/numpy/scipy） |
| 后端语言 | Python FastAPI |
| 端口 | 8006 |
| 部署边界 | 本地 demo 用 FastAPI serve 前端；天衍云集成走 SFC，**未集成进 qccp-web** |
| 量子硬件 | 仅模拟器，**非真实硬件** |
