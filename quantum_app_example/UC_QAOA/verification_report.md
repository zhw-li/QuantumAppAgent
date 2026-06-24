# Verification Report — UC_QAOA（机组组合量子优化平台）

> 对应 `experiment-pipeline` Stage 4。如实记录验证结论与局限。

## 1. 验证范围

| 维度 | 说明 |
|------|------|
| 实验复现 | 3 种规模（2×2/3×2/4×2 = 4/6/8 qubit），命令见各报告 `command` |
| 报告契约 | `baseline_report.json`、`quantum_report.json` 对照 cqlib-sdk artifact contract |
| 应用证据 | 后端 4 端点 + 前端（本地 + 天衍云 SFC） |
| 验证日期 | 2026-06-23 |

## 2. 核心结果（3 规模，QAOA p=2, restarts=5）

| 规模 | qubit | QAOA 成本 | 经典最优 | gap(%) | 可行 | 耗时 |
|------|-------|----------|---------|--------|------|------|
| 2×2 | 4 | 19724.44 | 19724.44 | **0.0%** | ✅ | 6.57s |
| 3×2 | 6 | 28067.22 | 28067.22 | **0.0%** | ✅ | 4.75s |
| 4×2 | 8 | 28674.86 | 28067.22 | 2.16% | ✅ | 11.65s |

## 3. Success Signals 核验

| # | requirements.json 声明 | 实测 | 通过 |
|---|----------------------|------|------|
| 1 | QAOA 全规模返回可行解 | 3/3 可行 | ✅ |
| 2 | 4-6 qubit gap ≤ 5% | 4q=0%，6q=0% | ✅ |
| 3 | 8 qubit 可扩展且近最优 | gap=2.16% < 5% | ✅ |

**全部 success signals 满足。**

## 4. 报告契约合规性

字段 task/data/primary_metric/higher_is_better/value/command/artifact_paths/backend/qubits/limitations 均已填写（baseline seed=null 确定性，quantum 含 qaoa_layers/restarts/optimizer/qubo_modeling）。

## 5. 缺失项与局限（诚实声明）

1. **仅模拟器**：cqlib StatevectorSimulator，非真实硬件。
2. **8 qubit 有 gap**：QAOA 在 8 qubit 出现 2.16% gap，反映 QAOA 在更大组合问题上的启发式局限；可通过增加层数/restart 改善，但这非本轮目标。
3. **基线受限**：暴力枚举仅 n≤20 可行，更大规模需其他经典启发式基线（如 LP 松弛）。
4. **SFC 未拆子组件**：`qccp-page-output/ucQaoa/index.vue` 为单文件（965 行），功能完整，属可选优化。
5. **未集成进 qccp-web**：集成步骤见 `INTEGRATE.md`。

## 6. 结论

应用功能完整、报告可复现、成功信号全部满足、局限如实记录。**符合标准示范应用要求**。
