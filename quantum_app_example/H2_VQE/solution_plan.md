# Solution Plan — H2_VQE（氢分子基态能量 VQE 计算平台）

> 本文件对应 `experiment-pipeline` Stage 1 的规划产物，描述交付阶段、成功信号、验证检查与依赖。

## 1. 问题与目标

| 项 | 内容 |
|----|------|
| 任务 | 计算氢分子 H2 基态能量（变分量子本征求解器 VQE） |
| 量子方法 | VQE + hardware-efficient ansatz（RY-RZ + CNOT）+ COBYLA 优化器，cqlib StatevectorSimulator |
| 经典基线 | 精确对角化（4×4 Pauli 哈密顿量，numpy.linalg.eigvalsh） |
| 主指标 | 能量误差 mHartree（越低越好），化学精度阈值 1.6 mHa |
| 数据 | H2 分子，STO-3G 基组，Parity + 2-qubit reduction，2 qubits；13 个键长（0.50–3.00 Å） |

## 2. 阶段划分（对应 experiment-pipeline 4 阶段）

### Stage 1 — Scope & Baseline（已完成）
- 结构化需求：见 `artifacts/requirements.json`
- 经典基线：精确对角化（解析可复现），见 `artifacts/baseline_report.json`
- **门禁**：需求/数据/主指标/基线显式且可复现 → ✅

### Stage 2 — Quantum Method（已完成）
- VQE 实现：见 `backend/main.py`（`hardware_efficient_ansatz`、`run_vqe`、`optimize_vqe_iterative`）
- 与基线同 task/data/metric 对比：见 `artifacts/quantum_report.json`
- **门禁**：quantum_report 与 baseline_report 同任务/数据/指标可比 → ✅

### Stage 3 — Application Packaging（已完成）
- 后端：Python FastAPI，端口 8002（见 `backend/main.py`）
- 前端（本地预览）：CDN HTML + app.js，见 `frontend/`
- 前端（天衍云 SFC）：见 `qccp-page-output/vqeH2/`
- 集成文档：见 `qccp-page-output/vqeH2/INTEGRATE.md`

### Stage 4 — Verification & Handoff
- 验证报告：见 `verification_report.md`
- README：见 `README.md`

## 3. 成功信号（success signals）

来源：`artifacts/requirements.json`，对照实测结果（见 `quantum_report.json`）：

| # | 成功信号 | 实测 | 状态 |
|---|---------|------|------|
| 1 | VQE 在平衡键长 0.74 Å 达化学精度（< 1.6 mHartree） | gap=0.0000 mHa | ✅ |
| 2 | VQE 能量曲线与精确解在各键长吻合 | 13/13 达化学精度，平均 0.0316 mHa | ✅ |
| 3 | VQE 在迭代层预算内收敛（≤3 层 ansatz） | 全部 1 层收敛，无需升层 | ✅ |

## 4. 验证检查清单

- [x] 基线已建立并记录（精确对角化，解析可复现，见 `baseline_report.json`）
- [x] 主指标跨运行一致（VQE 全 13 键长实测，statevector 确定性结果）
- [x] 量子结果与经典基线对比过（同 task/data/metric，逐键长误差）
- [x] 后端 API/前端/部署证据齐备
- [x] 失败案例与限制已记录（见 `quantum_report.json` limitations）

## 5. 依赖与部署边界

| 项 | 内容 |
|----|------|
| 运行环境 | conda env `evos`（Python 3.12，含 cqlib/fastapi/numpy/scipy） |
| 后端语言 | **Python FastAPI**（按决策保持 Python，不走 qccp-service Java 标准） |
| 端口 | 8002 |
| 数据来源 | 硬编码 H2 哈密顿量系数（Qiskit Nature / PySCF 标准输出，离线，无需联网） |
| 部署边界 | 本地 demo 用 FastAPI 直接 serve 前端；天衍云集成走 `qccp-page-output/` 的 SFC，**当前未集成进 qccp-web 工程** |
| 量子硬件 | 仅模拟器（StatevectorSimulator），**非真实硬件**，结果不得描述为硬件性能 |
| 复现命令 | 见 `artifacts/baseline_report.json` 与 `artifacts/quantum_report.json` 的 `command` 字段 |
