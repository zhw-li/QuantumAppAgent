# Solution Plan — Finance_QRC（量子储备池计算金融预测平台）

> 本文件对应 `experiment-pipeline` Stage 1 的规划产物，描述交付阶段、成功信号、验证检查与依赖。

## 1. 问题与目标

| 项 | 内容 |
|----|------|
| 任务 | 股票价格时序回归（next-day Close 预测） |
| 量子方法 | Quantum Reservoir Computing（cqlib StatevectorSimulator，RY 角度编码 + 固定参数量子储备池 + Pauli-Z 测量 + 非线性特征增强 + Ridge 读出） |
| 经典基线 | Classic Reservoir Computing（Echo State Network，稀疏循环储备池 + tanh + Ridge 读出） |
| 主指标 | RMSE（越低越好），辅以 MAE、MAPE |
| 数据 | DOW 10 demo tier（AAPL/MSFT/JPM/JNJ/V），2023-01-01 ~ 2025-01-01，window=5，80/20 时序划分 |

## 2. 阶段划分（对应 experiment-pipeline 4 阶段）

### Stage 1 — Scope & Baseline（已完成）
- 结构化需求：见 `requirements.json`
- 经典基线：ClassicRC，3 seeds 平均，见 `baseline_report.json`
- **门禁**：需求/数据/主指标/基线显式且可复现 → ✅ 满足（`python run_experiment.py --tier demo --seeds 42 123 456`）

### Stage 2 — Quantum Method（已完成）
- QRC 量子算法实现：见 `backend/qrc_model.py`
- 与基线同 task/data/metric 对比：见 `quantum_report.json`
- **门禁**：quantum_report 与 baseline_report 同任务/数据/指标可比 → ✅ 满足
- **结果**：QRC 在 JPM/V 上显著优于 ClassicRC（RMSE 改进 +30.1%/+16.2%），参数效率 99.53%（46 vs 9702 参数）

### Stage 3 — Application Packaging（已完成）
- 后端：Python FastAPI，9 端点，端口 8009（见 `backend/main.py`）
- 前端（本地预览）：CDN HTML + app.js，见 `frontend/`
- 前端（天衍云 SFC）：Vue 3 `<script setup>`，见 `qccp-page-output/quantumReservoir/`
- 集成文档：见 `INTEGRATE.md`

### Stage 4 — Verification & Handoff（本文档即其一）
- 验证报告：见 `verification_report.md`
- README：见 `README.md`

## 3. 成功信号（success signals）

来源：`requirements.json`，对照实测结果（3 seeds 平均）：

| # | 成功信号 | 实测 | 状态 |
|---|---------|------|------|
| 1 | QRC 参数效率 > 90% vs Classic RC | 99.53%（46/9702） | ✅ |
| 2 | QRC RMSE 平均在 Classic RC 的 2x 以内 | QRC avg 5.83 vs Classic 5.45（1.07x） | ✅ |
| 3 | QRC 在至少 1 支股票上优于 Classic RC | JPM(+30.1%)、V(+16.2%) | ✅ |

## 4. 验证检查清单

- [x] 基线已建立并记录（`baseline_report.json`）
- [x] 主指标跨运行一致（3 seeds + per-stock std）
- [x] 量子结果与经典基线对比过（同 task/data/metric）
- [x] 后端 API/前端/部署证据齐备
- [x] 失败案例与限制已记录（见 `quantum_report.json` limitations）

## 5. 依赖与部署边界

| 项 | 内容 |
|----|------|
| 运行环境 | conda env `evos`（Python 3.12，含 cqlib/fastapi/numpy/sklearn/yfinance） |
| 后端语言 | **Python FastAPI**（非 Java；按决策保持 Python，不走 qccp-service Java 标准） |
| 端口 | 8009 |
| 数据来源 | yfinance（运行时在线下载并缓存到 `data/cache/`） |
| 部署边界 | 本地 demo 用 FastAPI 直接 serve 前端；天衍云集成走 `qccp-page-output/` 的 SFC，**当前未集成进 qccp-web 工程** |
| 量子硬件 | 仅模拟器（StatevectorSimulator），**非真实硬件**，结果不得描述为硬件性能 |
