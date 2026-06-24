# Verification Report — Finance_QRC（量子储备池计算金融预测平台）

> 对应 `experiment-pipeline` Stage 4。本报告对照 `requirements.json` / `baseline_report.json` / `quantum_report.json` 与应用证据，**如实**记录验证结论、缺失项与局限，不夸大、不伪造。

## 1. 验证范围

| 维度 | 说明 |
|------|------|
| 实验复现 | 5 股票（demo tier）× 3 seeds（42/123/456），命令见各报告 `command` 字段 |
| 报告契约 | `baseline_report.json`、`quantum_report.json` 字段对照 `cqlib-sdk` artifact contract |
| 应用证据 | 后端 9 端点 + 前端（本地 CDN 预览 + 天衍云 SFC） |
| 验证日期 | 2026-06-23 |

## 2. 核心结果对照（3 seeds 平均，RMSE）

| 股票 | Classic RC | QRC | 改进 | 结论 |
|------|-----------|-----|------|------|
| AAPL | 4.60 ± 0.21 | 7.53 ± 1.15 | -63.6% | QRC 落后 |
| MSFT | 5.23 ± 0.04 | 7.60 ± 0.46 | -45.2% | QRC 落后 |
| **JPM** | **8.61 ± 0.40** | **5.97 ± 0.92** | **+30.1%** | **QRC 显著领先** |
| JNJ | 1.23 ± 0.005 | 1.74 ± 0.16 | -41.2% | QRC 落后 |
| **V** | **7.56 ± 0.36** | **6.29 ± 0.78** | **+16.2%** | **QRC 领先** |

> 平均 RMSE：Classic 5.45，QRC 5.83（QRC 平均略逊，但差距在 2x 内）。

## 3. Success Signals 核验

| # | requirements.json 声明 | 实测 | 通过 |
|---|----------------------|------|------|
| 1 | QRC 参数效率 > 90% vs Classic RC | 99.53%（46 / 9702 参数） | ✅ |
| 2 | QRC RMSE 平均在 Classic RC 的 2x 以内 | 5.83 / 5.45 = 1.07x | ✅ |
| 3 | QRC 在 ≥1 支股票上优于 Classic RC | JPM(+30.1%)、V(+16.2%) | ✅ |

**全部 success signals 满足。**

## 4. 报告契约合规性

| 字段 | baseline_report | quantum_report |
|------|----------------|----------------|
| task | ✅ | ✅ |
| data | ✅ | ✅ |
| primary_metric | ✅ | ✅ |
| higher_is_better | ✅ | ✅ |
| value | ✅（含 std） | ✅（含 std） |
| command | ✅ 可复现 | ✅ 可复现 |
| artifact_paths | ✅ | ✅ |
| seed | ✅ [42,123,456] | ✅ [42,123,456] |
| backend | ✅ | ✅ |
| qubits | — | ✅ 4 |
| circuit_depth | — | ✅ 7 |
| limitations | ✅ | ✅ |

> 注：Classic 基线为纯经典方法，`shots`/`qubits`/`circuit_depth` 按 cqlib-sdk 契约「when available」非必填，故 baseline 不含。

## 5. 应用证据核验

| 证据 | 状态 |
|------|------|
| 后端 `/api/health` 200 | ✅ |
| 后端 `/api/solve` 返回 QRC vs ClassicRC 结果 | ✅ |
| 后端 `/api/stocks`/`/api/params`/`/api/circuit` 等端点 | ✅ |
| 前端本地预览可渲染（CDN 模式） | ✅ |
| 天衍云 SFC（`qccp-page-output/`） | ✅ 已补 api 模块 + 接真实 API |

## 6. 缺失项与局限（诚实声明）

1. **仅模拟器**：所有量子结果来自 cqlib StatevectorSimulator，**非真实量子硬件**，不可描述为硬件性能。
2. **数据规模有限**：demo tier 仅 5 支股票；standard(8)/full(10) tier 未在本轮报告数据中实测（应用支持，可按需补跑）。
3. **QRC 优势依赖股票**：QRC 在 JPM/V 上领先，但在 AAPL/MSFT/JNJ 上落后，优势非普适；存在 seed 方差（已报告 std）。
4. **未集成进 qccp-web 工程**：SFC 已按标准产出，但未执行 `npm run build` 接入真实 qccp-web（无该工程源码），集成步骤见 `INTEGRATE.md`。
5. **天衍云 SFC 历史版本默认走 mock 数据**：原 `index.vue` 为 `isProduction=false`，本轮已修复为接真实后端 API（见 1.4）。

## 7. 结论

应用功能完整、报告可复现、成功信号全部满足、局限已如实记录。**符合标准示范应用交付要求**，可用于作为其余应用的改造样板。
