# Verification Report — Finance_QAOA（量子组合投资优化平台）

> 对应 `experiment-pipeline` Stage 4。如实记录验证结论与局限，不夸大。

## 1. 验证范围

| 维度 | 说明 |
|------|------|
| 实验复现 | 3 tier（demo 5股/standard 8股/full 12股），QAOA p=2, restarts=5, q=0.5 |
| 报告契约 | `baseline_report.json`、`quantum_report.json` 对照 cqlib-sdk artifact contract |
| 应用证据 | 后端 7 端点 + 前端（本地 + 天衍云 SFC，5 Tab） |
| 验证日期 | 2026-06-23 |

## 2. 核心结果（3 tier）

| tier | qubit | QAOA 选股 | 经典选股 | cost_gap(%) | QAOA Sharpe | 经典 Sharpe | 耗时 |
|------|-------|----------|---------|-------------|------------|------------|------|
| demo | 5 | AAPL,MSFT,JNJ | MSFT,AAPL,JNJ | **0.0%** | 0.890 | 0.912 | 16s |
| standard | 8 | AAPL,MSFT,JNJ,KO | AAPL,MSFT,KO,CAT | **0.0%** | 0.889 | 0.924 | 26s |
| full | 12 | AAPL,BA,MMM,WMT | AAPL,MSFT,KO,WMT | 125.4% | 0.393 | 0.929 | 229s |

## 3. Success Signals 核验

| # | requirements.json 声明 | 实测 | 通过 |
|---|----------------------|------|------|
| 1 | 5-8 股 tier QAOA gap 0% | demo=0%，standard=0% | ✅ |
| 2 | 12 股可扩展产出可行组合 | 产出可行组合，但 gap 125.4% | ⚠️ 部分 |
| 3 | 小 tier QAOA Sharpe 与经典可比 | demo 0.89 vs 0.91 | ✅ |

**2/3 完全满足；signal 2 部分满足（可行但非最优）。**

## 4. 报告契约合规性

字段 task/data/primary_metric/higher_is_better/value/command/artifact_paths/seed/backend/qubits/qaoa_layers/restarts/optimizer/qubo_modeling/limitations 均已填写。

## 5. 缺失项与局限（诚实声明）

1. **仅模拟器**：cqlib StatevectorSimulator，非真实硬件。
2. **full tier 大 gap**：12 qubit 出现 125.4% gap——QAOA 在 p=2/restarts=5 下未充分探索 2^12 空间，最高概率比特串偏离最优。增大 p/restarts 可改善但耗时更长（full 已 229s）。这是 QAOA 启发式的已知局限，非 bug。
3. **求解时间增长快**：16s→26s→229s，随 qubit 数指数增长。
4. **经典 vs 量子口径不同**：Markowitz 是连续权重优化，QAOA 是二值选择，二者 return/risk 不直接可比；cost_gap 是相对暴力二值最优。
5. **历史数据**：2018-2022 历史收益，非前瞻预测。
6. **未集成进 qccp-web**：集成步骤见 `INTEGRATE.md`。

## 6. 结论

应用功能完整、报告可复现。QAOA 在小中规模（5-8 qubit）达最优（gap 0%），在 12 qubit 受启发式局限出现偏差——该结果如实记录，体现了 QAOA 的规模敏感性，具有示范价值。**符合标准示范应用要求**（成功信号 2/3 完全满足，1 部分满足且已如实标注）。
