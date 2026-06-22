# INTEGRATE.md - financeQlstm Page

## 1. Page Info

| Field | Value |
| --- | --- |
| Page Name | QLSTM 量子时间序列预测 |
| pageKey | `financeQlstm` |
| Module | `solution` |
| Route | `/solution/financeQlstm` |

## 2. File Copy Destinations

| Source (in this output) | Destination (in qccp-web) |
| --- | --- |
| `project-files/src/views/solution/financeQlstm/index.vue` | `src/views/solution/financeQlstm/index.vue` |
| `project-files/src/views/solution/financeQlstm/components/BannerSection.vue` | `src/views/solution/financeQlstm/components/BannerSection.vue` |
| `project-files/src/views/solution/financeQlstm/components/StockSelectPanel.vue` | `src/views/solution/financeQlstm/components/StockSelectPanel.vue` |
| `project-files/src/views/solution/financeQlstm/components/ModelComparePanel.vue` | `src/views/solution/financeQlstm/components/ModelComparePanel.vue` |
| `project-files/src/views/solution/financeQlstm/components/PredictionChartPanel.vue` | `src/views/solution/financeQlstm/components/PredictionChartPanel.vue` |
| `project-files/src/views/solution/financeQlstm/components/TrainingCurvePanel.vue` | `src/views/solution/financeQlstm/components/TrainingCurvePanel.vue` |
| `project-files/src/views/solution/financeQlstm/components/ArchitectureInfoPanel.vue` | `src/views/solution/financeQlstm/components/ArchitectureInfoPanel.vue` |
| `project-files/src/views/solution/financeQlstm/data.js` | `src/views/solution/financeQlstm/data.js` |
| `project-files/src/api/financeQlstm/index.js` | `src/api/financeQlstm/index.js` |
| `project-files/src/assets/images/financeQlstm/` | `src/assets/images/financeQlstm/` |

## 3. Route Object

Append to the appropriate route array (likely under `solution` children):

```javascript
{
  path: '/solution/financeQlstm',
  name: 'financeQlstm',
  component: () => import('@/views/solution/financeQlstm/index.vue'),
  meta: { title: 'financeQlstm' },
},
```

## 4. Chinese i18n Object (zh)

Append to `src/utils/lang/zh.js`:

```javascript
financeQlstm: {
  banner: {
    title: 'QLSTM 量子时间序列预测',
    subtitle: '基于量子长短期记忆网络的金融股价预测',
    tag: '天衍量子应用',
  },
  stock: {
    title: '股票选择与训练参数',
    selectLabel: '选择股票',
    hiddenSize: '隐藏层大小',
    nQubits: '量子比特数',
    epochs: '训练轮数',
    startTrain: '开始训练',
    training: '训练中...',
    selectPlaceholder: '请选择股票',
  },
  compare: {
    title: '模型性能对比',
    qlstm: 'QLSTM 量子模型',
    lstm: 'LSTM 经典模型',
    rmse: 'RMSE',
    mae: 'MAE',
    mape: 'MAPE',
    params: '参数量',
    improvement: '提升幅度',
    noData: '暂无对比数据，请先训练模型',
  },
  prediction: {
    title: '预测曲线',
    tabPrediction: '预测对比',
    tabCandle: 'K线数据',
    actual: '实际值',
    qlstm: 'QLSTM',
    lstm: 'LSTM',
    date: '日期',
    price: '股价',
    noData: '暂无预测数据，请先训练模型',
    open: '开盘',
    high: '最高',
    low: '最低',
    close: '收盘',
    volume: '成交量',
  },
  training: {
    title: '训练损失曲线',
    qlstm: 'QLSTM Loss',
    lstm: 'LSTM Loss',
    epoch: '轮次',
    loss: '损失值',
    noData: '暂无训练数据，请先训练模型',
  },
  architecture: {
    title: '模型架构',
    qlstm: 'QLSTM 量子架构',
    lstm: 'LSTM 经典架构',
    nQubits: '量子比特数',
    layers: '层数',
    hiddenSize: '隐藏层大小',
    totalParams: '总参数量',
    vqcStructure: 'VQC 结构',
    numLayers: 'LSTM层数',
    noData: '暂无架构信息',
  },
  message: {
    trainSuccess: '训练完成',
    trainFailed: '训练失败，请重试',
    loadFailed: '数据加载失败',
    networkError: '网络异常，请稍后重试',
    noStock: '请先选择股票',
  },
},
```

## 5. English i18n Object (en)

Append to `src/utils/lang/en.js`:

```javascript
financeQlstm: {
  banner: {
    title: 'QLSTM Quantum Time Series Forecasting',
    subtitle: 'Financial Stock Price Prediction Based on Quantum LSTM',
    tag: 'TianYan Quantum App',
  },
  stock: {
    title: 'Stock Selection & Training Parameters',
    selectLabel: 'Select Stock',
    hiddenSize: 'Hidden Size',
    nQubits: 'Qubits',
    epochs: 'Epochs',
    startTrain: 'Start Training',
    training: 'Training...',
    selectPlaceholder: 'Please select a stock',
  },
  compare: {
    title: 'Model Performance Comparison',
    qlstm: 'QLSTM Quantum Model',
    lstm: 'LSTM Classical Model',
    rmse: 'RMSE',
    mae: 'MAE',
    mape: 'MAPE',
    params: 'Parameters',
    improvement: 'Improvement',
    noData: 'No comparison data yet, please train the model first',
  },
  prediction: {
    title: 'Prediction Curves',
    tabPrediction: 'Prediction Comparison',
    tabCandle: 'Candlestick Data',
    actual: 'Actual',
    qlstm: 'QLSTM',
    lstm: 'LSTM',
    date: 'Date',
    price: 'Price',
    noData: 'No prediction data yet, please train the model first',
    open: 'Open',
    high: 'High',
    low: 'Low',
    close: 'Close',
    volume: 'Volume',
  },
  training: {
    title: 'Training Loss Curves',
    qlstm: 'QLSTM Loss',
    lstm: 'LSTM Loss',
    epoch: 'Epoch',
    loss: 'Loss',
    noData: 'No training data yet, please train the model first',
  },
  architecture: {
    title: 'Model Architecture',
    qlstm: 'QLSTM Quantum Architecture',
    lstm: 'LSTM Classical Architecture',
    nQubits: 'Qubits',
    layers: 'Layers',
    hiddenSize: 'Hidden Size',
    totalParams: 'Total Parameters',
    vqcStructure: 'VQC Structure',
    numLayers: 'LSTM Layers',
    noData: 'No architecture info available',
  },
  message: {
    trainSuccess: 'Training completed',
    trainFailed: 'Training failed, please retry',
    loadFailed: 'Failed to load data',
    networkError: 'Network error. Please try again later.',
    noStock: 'Please select a stock first',
  },
},
```

## 6. Existing npm Dependencies Used

| Dependency | Version | Purpose |
| --- | --- | --- |
| echarts | (existing in qccp-web) | Chart rendering (prediction, candlestick, training curves) |
| element-plus | (existing in qccp-web) | UI components (el-card, el-select, el-button, el-tabs, el-descriptions, el-tag, el-empty, el-input-number) |
| vue-i18n | (existing in qccp-web) | Bilingual text switching |
| vue | 3.x | Framework |
| vue-router | 4.x | Route navigation |

No new dependencies required.

## 7. API Contract

All endpoints proxied via `/qlstm-api` prefix to `http://localhost:8007`.

| Endpoint | Method | Request | Response | Notes |
| --- | --- | --- | --- | --- |
| `/qlstm-api/api/stocks` | GET | - | `{ stocks: string[] }` | List available stock tickers |
| `/qlstm-api/api/train` | POST | `{ stock, seq_len, hidden_size, n_qubits, qlstm_epochs, lstm_epochs }` | `{ status, message, QLSTM_metrics: {RMSE,MAE,MAPE}, LSTM_metrics: {RMSE,MAE,MAPE} }` | Triggers training; may take time |
| `/qlstm-api/api/comparison` | GET | - | `{ QLSTM: {RMSE,MAE,MAPE,params}, LSTM: {RMSE,MAE,MAPE,params}, improvement: {RMSE,MAE,MAPE} }` | Comparison results |
| `/qlstm-api/api/predictions` | GET | - | `{ dates: string[], actual: number[], QLSTM: number[], LSTM: number[] }` | Prediction curve data |
| `/qlstm-api/api/training-curves` | GET | - | `{ QLSTM: number[], LSTM: number[] }` | Per-epoch loss values |
| `/qlstm-api/api/raw-data` | GET | `?stock=AAPL&days=365` | `{ dates: string[], OHLC: [{open,high,low,close}], volume: number[] }` | OHLCV candlestick data |
| `/qlstm-api/api/model-info` | GET | - | `{ QLSTM: {n_qubits,layers,hidden_size,total_params}, LSTM: {hidden_size,num_layers,total_params} }` | Architecture details |

Fallback: When the backend is unavailable, `data.js` provides demo data so the page renders with sample content.

## 8. Footer

Not used. The page does not include `<Footer />`.

## 9. Login / Permission

Not required. This is a public showcase page.

## 10. Build Command

```bash
npm run build
```

## ECharts + el-tabs Critical Note

This page uses ECharts charts inside `el-tabs`. The following measures are implemented to prevent blank charts:

1. Chart containers have explicit CSS `height: 420px` / `height: 400px`
2. `getOrCreateChart()` checks `offsetWidth > 0` before calling `echarts.init()`
3. On tab switch, chart rendering is deferred with `setTimeout(200ms)` + `nextTick`
4. Chart instances are disposed in `onBeforeUnmount`
5. Window resize events trigger `chart.resize()` for responsive behavior
