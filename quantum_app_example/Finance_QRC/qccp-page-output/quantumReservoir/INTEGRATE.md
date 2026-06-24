# INTEGRATE.md — Quantum Reservoir Computing Finance Prediction Page

## 1. Page Info

| Field | Value |
|-------|-------|
| Page name | Quantum Reservoir Computing Finance Prediction |
| pageKey | `quantumReservoir` |
| Module | `solution` |
| Final route | `/solution/quantumReservoir` |
| Backend port | 8009 |

## 2. File Copy Destinations

| Source (in this output) | Destination (in qccp-web) |
|-------------------------|---------------------------|
| `project-files/src/views/solution/quantumReservoir/index.vue` | `src/views/solution/quantumReservoir/index.vue` |
| `project-files/src/views/solution/quantumReservoir/components/PredictionChart.vue` | `src/views/solution/quantumReservoir/components/PredictionChart.vue` |
| `project-files/src/views/solution/quantumReservoir/components/MetricsCard.vue` | `src/views/solution/quantumReservoir/components/MetricsCard.vue` |
| `project-files/src/views/solution/quantumReservoir/components/ReservoirScatter.vue` | `src/views/solution/quantumReservoir/components/ReservoirScatter.vue` |
| `project-files/src/views/solution/quantumReservoir/components/CircuitInfo.vue` | `src/views/solution/quantumReservoir/components/CircuitInfo.vue` |
| `project-files/src/views/solution/quantumReservoir/data.js` | `src/views/solution/quantumReservoir/data.js` |

## 3. Route Object

Append to the appropriate children array in the router config:

```js
{
  path: 'quantumReservoir',
  name: 'QuantumReservoir',
  component: () => import('@/views/solution/quantumReservoir/index.vue'),
  meta: {
    title: '量子储备池计算金融预测',
    enTitle: 'Quantum Reservoir Computing Finance Prediction'
  }
}
```

## 4. Chinese i18n (append to `src/utils/lang/zh.js`)

```js
quantumReservoir: {
  banner: {
    title: '量子储备池计算金融预测',
    subtitle: '基于量子储备池计算(Quantum Reservoir Computing)的股票价格预测，对比经典储备池与量子储备池的预测性能'
  },
  controls: {
    stock: '股票',
    stockPlaceholder: '选择股票',
    nQubits: '量子比特数',
    depth: '电路深度',
    windowSize: '时间窗口',
    nReservoir: '储备池规模',
    spectralRadius: '谱半径',
    ridgeAlpha: '岭回归系数',
    solve: '开始预测',
    solving: '预测中...',
    retry: '重试'
  },
  metrics: {
    rmse: 'RMSE',
    mae: 'MAE',
    mape: 'MAPE',
    paramEfficiency: '参数效率',
    classic: '经典',
    quantum: '量子',
    improvement: '提升'
  },
  tabs: {
    prediction: '预测对比',
    scatter: '储备池状态',
    circuit: '量子电路',
    compare: '多股票对比'
  },
  chart: {
    actual: '真实值',
    classic: '经典RC预测',
    quantum: '量子RC预测',
    noData: '暂无预测数据，请先运行预测'
  },
  scatter: {
    quantumTitle: '量子储备池状态(PCA)',
    classicTitle: '经典储备池状态(PCA)',
    noData: '暂无储备池状态数据'
  },
  circuit: {
    nQubits: '量子比特数',
    depth: '电路深度',
    gateCount: '门数量',
    paramCount: '参数数量',
    circuitType: '电路类型',
    qcisCode: 'QCIS 量子指令',
    noData: '暂无电路信息'
  },
  compare: {
    ticker: '股票代码',
    classicRMSE: '经典RMSE',
    quantumRMSE: '量子RMSE',
    classicMAE: '经典MAE',
    quantumMAE: '量子MAE',
    classicParams: '经典参数量',
    quantumParams: '量子参数量',
    noData: '暂无对比数据'
  },
  algorithm: {
    title: '算法说明',
    desc1: '量子储备池计算(Quantum Reservoir Computing, QRC)是一种融合量子计算与储备池计算的混合方法。储备池计算将输入数据映射到高维储备池状态空间，通过线性读出层完成预测任务。',
    desc2: '在QRC中，参数化量子电路(PQC)充当非线性储备池，量子态的丰富动力学特性提供了经典储备池难以实现的高维非线性映射。量子电路的酉变换和纠缠特性使得少量参数即可覆盖庞大的希尔伯特空间，实现参数高效的特征提取。',
    desc3: '本平台对比经典储备池网络(RC)与量子储备池计算(QRC)在股票价格预测任务上的表现，从RMSE、MAE、MAPE及参数效率四个维度评估量子方法的性能优势。'
  },
  message: {
    solveSuccess: '预测完成',
    solveFailed: '预测失败，请检查参数后重试',
    loadFailed: '数据加载失败',
    networkError: '网络异常，请稍后重试',
    noResult: '请选择股票和参数，点击"开始预测"运行实验'
  }
}
```

## 5. English i18n (append to `src/utils/lang/en.js`)

```js
quantumReservoir: {
  banner: {
    title: 'Quantum Reservoir Computing Finance Prediction',
    subtitle: 'Stock price prediction using Quantum Reservoir Computing, comparing classical and quantum reservoir prediction performance'
  },
  controls: {
    stock: 'Stock',
    stockPlaceholder: 'Select stock',
    nQubits: 'Qubits',
    depth: 'Circuit Depth',
    windowSize: 'Window Size',
    nReservoir: 'Reservoir Size',
    spectralRadius: 'Spectral Radius',
    ridgeAlpha: 'Ridge Alpha',
    solve: 'Start Prediction',
    solving: 'Predicting...',
    retry: 'Retry'
  },
  metrics: {
    rmse: 'RMSE',
    mae: 'MAE',
    mape: 'MAPE',
    paramEfficiency: 'Param Efficiency',
    classic: 'Classic',
    quantum: 'Quantum',
    improvement: 'Improvement'
  },
  tabs: {
    prediction: 'Prediction',
    scatter: 'Reservoir States',
    circuit: 'Quantum Circuit',
    compare: 'Multi-stock Compare'
  },
  chart: {
    actual: 'Actual',
    classic: 'Classic RC',
    quantum: 'Quantum RC',
    noData: 'No prediction data yet. Run a prediction first.'
  },
  scatter: {
    quantumTitle: 'Quantum Reservoir States (PCA)',
    classicTitle: 'Classic Reservoir States (PCA)',
    noData: 'No reservoir state data available'
  },
  circuit: {
    nQubits: 'Qubits',
    depth: 'Depth',
    gateCount: 'Gate Count',
    paramCount: 'Parameter Count',
    circuitType: 'Circuit Type',
    qcisCode: 'QCIS Instructions',
    noData: 'No circuit information available'
  },
  compare: {
    ticker: 'Ticker',
    classicRMSE: 'Classic RMSE',
    quantumRMSE: 'Quantum RMSE',
    classicMAE: 'Classic MAE',
    quantumMAE: 'Quantum MAE',
    classicParams: 'Classic Params',
    quantumParams: 'Quantum Params',
    noData: 'No comparison data available'
  },
  algorithm: {
    title: 'Algorithm Description',
    desc1: 'Quantum Reservoir Computing (QRC) is a hybrid approach combining quantum computing with reservoir computing. Reservoir computing maps input data into a high-dimensional reservoir state space and uses a linear readout layer for prediction tasks.',
    desc2: 'In QRC, a parameterized quantum circuit (PQC) serves as a nonlinear reservoir. The rich dynamics of quantum states provide high-dimensional nonlinear mappings that are difficult for classical reservoirs to achieve. The unitary transformation and entanglement properties of quantum circuits enable a small number of parameters to cover a vast Hilbert space, achieving parameter-efficient feature extraction.',
    desc3: 'This platform compares classical reservoir computing (RC) and quantum reservoir computing (QRC) on stock price prediction tasks, evaluating the performance advantages of the quantum approach across four dimensions: RMSE, MAE, MAPE, and parameter efficiency.'
  },
  message: {
    solveSuccess: 'Prediction completed',
    solveFailed: 'Prediction failed. Please check parameters and retry.',
    loadFailed: 'Failed to load data',
    networkError: 'Network error. Please try again later.',
    noResult: 'Select a stock and parameters, then click "Start Prediction" to run the experiment.'
  }
}
```

## 6. Existing npm Dependencies Used

| Dependency | Version (existing) | Usage |
|------------|---------------------|-------|
| `vue` | ^3.5.x | Composition API, `<script setup>` |
| `vue-i18n` | existing | `$t()`, `useI18n()` |
| `element-plus` | existing | `el-card`, `el-select`, `el-radio-group`, `el-slider`, `el-button`, `el-tabs`, `el-table`, `el-empty`, `ElMessage` |
| `echarts` | existing | Prediction chart, scatter plots, compare bar chart |

No new dependencies required.

## 7. API Endpoints

All endpoints target the QRC backend at port 8009. In production, requests go through `@/utils/axios.js` with `VITE_APP_BASE_API` prefix.

| # | Method | URL | Request | Response | apiCode |
|---|--------|-----|----------|----------|---------|
| 1 | POST | `/api/solve` | `{ ticker, n_qubits, depth, window_size, n_reservoir, spectral_radius, ridge_alpha, seed }` | 后端原始：`{ ticker, params, classic:{RMSE,MAE,MAPE,n_params,predictions,actual,dates}, quantum:{...}, comparison }`；页面经 `api/quantumReservoir/index.js` 适配为 `{ success, stock, params, metrics:{classic,quantum}, predictions:{dates,actual,classic,quantum} }` | (TBD) |
| 2 | GET | `/api/stocks` | — | `{ stocks: string[], default }` | (TBD) |
| 3 | GET | `/api/params` | — | `{ n_qubits:{default,options}, depth:{default,options}, window_size:{default,options}, n_reservoir:{default,min,max}, spectral_radius:{default,min,max}, ridge_alpha:{default,min,max} }` | (TBD) |
| 4 | GET | `/api/circuit?n_qubits=&depth=` | — | 后端原始：`{ n_qubits, depth, n_parameters, gate_counts, circuit_depth, qcis }`；页面适配为 `{ n_qubits, depth, gate_count, gate_counts, parameter_count, circuit_depth, circuit_type, qcis_code }` | (TBD) |
| 5 | GET | `/api/reservoir-states?ticker=&n_qubits=&depth=&window_size=` | — | 后端原始：`{ quantum_states, classic_states, input_values }`；页面适配为 `{ quantumPoints, classicPoints, input_values }` | (TBD) |
| 6 | GET | `/api/compare` | — | `{ stocks:[{ticker, classic_rmse, quantum_rmse, improvement, quantum_wins}], summary }`；页面适配为 compare 表格行（含 `classic_RMSE`/`quantum_RMSE` 大写键） | (TBD) |
| 7 | GET | `/api/raw-data/{ticker}?days=365` | — | `{ ticker, dates, close, volume, open, high, low }` | (TBD) |

**API field casing**: Backend returns UPPERCASE metric keys (`RMSE`, `MAE`, `MAPE`). 前端读 `metrics.classic.RMSE` 等大写键；`api/quantumReservoir/index.js` 负责把后端字段（如 `n_params`→`param_count`、分散的 classic/quantum 块→`metrics` 包裹）适配为页面期望结构。

**API 模块**: 页面通过 `@/api/quantumReservoir/index.js` 调用，该模块经 `@/utils/axios.js` 发请求并做响应适配。**本页面已接真实后端**（不再使用 mock 数据）。

## 8. Footer Usage

**Yes** — `<Footer />` is imported and rendered at the bottom of the page.

```js
import Footer from '@/components/Footer.vue';
```

## 9. Login Permission / Nav Entry

- **Login required**: No (public solution page)
- **Nav entry**: Add "量子储备池计算金融预测" / "Quantum Reservoir Computing" under the Solution navigation group if desired

## 10. Verification Command

```bash
npm run build
```

This should compile without errors if all files are copied to the correct destinations and i18n entries are appended.

---

## Integration Checklist

- [ ] Copy all project-files to their destinations in qccp-web (含 `src/api/quantumReservoir/index.js` API 适配模块)
- [ ] Append route object to the solution children array
- [ ] Append `quantumReservoir` zh object to `src/utils/lang/zh.js`
- [ ] Append `quantumReservoir` en object to `src/utils/lang/en.js`
- [ ] Configure backend API proxy for port 8009 in dev server or nginx（页面已通过 `@/api/quantumReservoir/index.js` → `@/utils/axios.js` 调真实后端）
- [ ] Fill in `apiCode` values for each endpoint when available
- [ ] Run `npm run build` to verify no compilation errors
- [ ] Test Chinese/English language switching
- [ ] Test all 4 tabs render charts correctly (ECharts+el-tabs deferred render)
- [ ] Test loading, error, and empty states
