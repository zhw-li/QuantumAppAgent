# Verification Report — MaxCut_QAOA（最大割量子优化平台）

> 对应 `experiment-pipeline` Stage 4。如实记录验证结论与局限。

## 1. 验证范围

| 维度 | 说明 |
|------|------|
| 实验复现 | 3 个预设图（simple_4/medium_6/large_8 = 4/6/8 qubit），命令见各报告 `command` |
| 报告契约 | `baseline_report.json`、`quantum_report.json` 对照 cqlib-sdk artifact contract |
| 应用证据 | 后端 4 端点 + 前端（本地 + 天衍云 SFC） |
| 验证日期 | 2026-06-23 |

## 2. 核心结果（3 图，QAOA p=2, restarts=5）

| 图 | qubit | QAOA cut | 暴力最优 | gap(%) | 耗时 |
|----|-------|---------|---------|--------|------|
| simple_4 | 4 | 3.0 | 3.0 | **0.0%** | 13.09s |
| medium_6 | 6 | 8.0 | 8.0 | **0.0%** | 6.72s |
| large_8 | 8 | 11.0 | 11.0 | **0.0%** | 17.71s |

## 3. Success Signals 核验

| # | requirements.json 声明 | 实测 | 通过 |
|---|----------------------|------|------|
| 1 | QAOA 在 3 个预设图（4-8 qubit）gap 0% | 3/3 gap=0% | ✅ |
| 2 | QAOA cut 与暴力最优一致 | 全一致 | ✅ |
| 3 | QAOA 在预算内收敛 | 全部 5 restarts 内收敛 | ✅ |

**全部 success signals 满足。**

## 4. 报告契约合规性

字段 task/data/primary_metric/higher_is_better/value/command/artifact_paths/seed/backend/qubits/limitations 均已填写，qaoa_layers/restarts/optimizer/qubo_modeling 齐全。

## 5. 缺失项与局限（诚实声明）

1. **仅模拟器**：cqlib StatevectorSimulator，非真实硬件。
2. **小图有利**：3 个预设图规模小（4-8 节点），MaxCut 在此类规模上对 QAOA 有利；更密/更大的图表现可能不同。
3. **无采样噪声**：statevector 模拟，非 shot-based。
4. **重复文件已清理**：原根目录有 main.py/graph_utils.py/maxcut_solver.py/static 与 backend/frontend 重复，已统一到 backend/ + frontend/（见结构）。
5. **未集成进 qccp-web**：集成步骤见 `INTEGRATE.md`。

## 6. 结论

应用功能完整、报告可复现、成功信号全部满足（3/3 最优）、局限如实记录。**符合标准示范应用要求**。
