# INTEGRATE.md — financeQaoa

## Page Info

| Field | Value |
|-------|-------|
| Page name | 量子组合投资优化 (Quantum Portfolio Optimization) |
| pageKey | financeQaoa |
| Module | solution |
| Route | `/solution/finance-qaoa` |

## File Copy Destinations

| Source (under `project-files/`) | Destination in qccp-web |
|--------------------------------|------------------------|
| `src/views/solution/financeQaoa/index.vue` | `src/views/solution/financeQaoa/index.vue` |
| `src/views/solution/financeQaoa/data.js` | `src/views/solution/financeQaoa/data.js` |
| `src/views/solution/financeQaoa/components/DashboardTab.vue` | `src/views/solution/financeQaoa/components/DashboardTab.vue` |
| `src/views/solution/financeQaoa/components/StatisticsTab.vue` | `src/views/solution/financeQaoa/components/StatisticsTab.vue` |
| `src/views/solution/financeQaoa/components/ClassicalTab.vue` | `src/views/solution/financeQaoa/components/ClassicalTab.vue` |
| `src/views/solution/financeQaoa/components/QuantumTab.vue` | `src/views/solution/financeQaoa/components/QuantumTab.vue` |
| `src/views/solution/financeQaoa/components/CompareTab.vue` | `src/views/solution/financeQaoa/components/CompareTab.vue` |
| `src/api/financeQaoa/index.js` | `src/api/financeQaoa/index.js` |

## Route Object

Append to `src/router/index.js` or the relevant route module:

```js
{
  path: '/solution/finance-qaoa',
  name: 'FinanceQaoa',
  component: () => import('@/views/solution/financeQaoa/index.vue'),
  meta: {
    title: 'financeQaoa.hero.title',
    requireAuth: false,
  },
},
```

## Chinese i18n (`src/utils/lang/zh.js`)

Append the following object:

```js
financeQaoa: {
  hero: {
    title: '量子组合投资优化',
    subtitle: '基于QAOA量子算法的金融投资组合优化云平台',
  },
  tabs: {
    dashboard: '数据概览',
    statistics: '统计分析',
    classical: '经典优化',
    quantum: '量子优化',
    compare: '对比分析',
  },
  dashboard: {
    tier: '数据层级',
    tierDemo: '演示 (5支)',
    tierStandard: '标准 (8支)',
    tierFull: '完整 (10支)',
    stockCards: '股票概览',
    latestPrice: '最新价',
    totalReturn: '总回报',
    dataPoints: '数据点',
    priceTrend: '价格趋势',
    selectStock: '选择股票',
  },
  statistics: {
    annualReturn: '年化收益率',
    annualVolatility: '年化波动率',
    sharpeRatio: '夏普比率',
    maxDrawdown: '最大回撤',
    totalReturn: '累计回报',
    correlationHeatmap: '相关性热力图',
    riskReturnScatter: '风险-收益散点图',
    statsTable: '统计数据表',
    stock: '股票',
  },
  classical: {
    title: 'Markowitz 均值-方差优化',
    params: '优化参数',
    selectK: '选取股票数 (k)',
    riskAversion: '风险厌恶系数 (q)',
    run: '运行优化',
    running: '优化中...',
    efficientFrontier: '有效前沿',
    weightDistribution: '权重分布',
    selectedStocks: '选中股票',
    portfolioReturn: '组合收益率',
    portfolioRisk: '组合风险',
    portfolioSharpe: '组合夏普比率',
    riskReturnScatter: '风险-收益散点图',
  },
  quantum: {
    title: 'QAOA 量子组合优化',
    params: 'QAOA参数',
    selectK: '选取股票数 (k)',
    riskAversion: '风险厌恶系数 (q)',
    depth: '电路深度 (p)',
    restarts: '随机重启次数',
    forceRerun: '强制重新运行',
    run: '运行QAOA',
    running: 'QAOA优化中...',
    results: '优化结果',
    selectedStocks: '选中股票',
    costGap: '代价差距',
    optimalEnergy: '最优能量',
    nQubits: '量子比特数',
    penaltyWeight: '惩罚权重',
    normFactor: '归一化因子',
    bitstringDistribution: '比特串概率分布',
    weightDistribution: '权重分布',
    bruteForceComparison: '暴力搜索对比',
    portfolioReturn: '组合收益率',
    portfolioRisk: '组合风险',
    portfolioSharpe: '组合夏普比率',
    bruteForceReturn: '暴力搜索收益率',
    bruteForceRisk: '暴力搜索风险',
    bruteForceSharpe: '暴力搜索夏普比率',
  },
  compare: {
    title: '经典 vs 量子对比分析',
    params: '对比参数',
    selectK: '选取股票数 (k)',
    riskAversion: '风险厌恶系数 (q)',
    depth: '电路深度 (p)',
    restarts: '随机重启次数',
    run: '运行对比',
    running: '对比运行中...',
    metricsTable: '性能指标对比',
    method: '方法',
    classicalMethod: '经典Markowitz',
    quantumMethod: 'QAOA量子',
    bruteForceMethod: '暴力搜索',
    portfolioReturn: '组合收益率',
    portfolioRisk: '组合风险',
    portfolioSharpe: '夏普比率',
    costGap: '代价差距',
    selectedStocks: '选中股票',
    weightComparison: '权重对比',
    efficientFrontier: '有效前沿',
    riskReturnChart: '风险-收益对比图',
  },
  message: {
    loadFailed: '数据加载失败',
    networkError: '网络异常，请稍后重试',
    optimizeSuccess: '优化完成',
    optimizeFailed: '优化失败，请重试',
    noData: '暂无数据',
  },
  common: {
    loading: '加载中...',
    retry: '重试',
    percent: '%',
  },
},
```

## English i18n (`src/utils/lang/en.js`)

Append the following object:

```js
financeQaoa: {
  hero: {
    title: 'Quantum Portfolio Optimization',
    subtitle: 'QAOA-based financial portfolio optimization cloud platform',
  },
  tabs: {
    dashboard: 'Dashboard',
    statistics: 'Statistics',
    classical: 'Classical',
    quantum: 'Quantum',
    compare: 'Compare',
  },
  dashboard: {
    tier: 'Data Tier',
    tierDemo: 'Demo (5 stocks)',
    tierStandard: 'Standard (8 stocks)',
    tierFull: 'Full (10 stocks)',
    stockCards: 'Stock Overview',
    latestPrice: 'Latest Price',
    totalReturn: 'Total Return',
    dataPoints: 'Data Points',
    priceTrend: 'Price Trend',
    selectStock: 'Select Stock',
  },
  statistics: {
    annualReturn: 'Annual Return',
    annualVolatility: 'Annual Volatility',
    sharpeRatio: 'Sharpe Ratio',
    maxDrawdown: 'Max Drawdown',
    totalReturn: 'Total Return',
    correlationHeatmap: 'Correlation Heatmap',
    riskReturnScatter: 'Risk-Return Scatter',
    statsTable: 'Statistics Table',
    stock: 'Stock',
  },
  classical: {
    title: 'Markowitz Mean-Variance Optimization',
    params: 'Optimization Parameters',
    selectK: 'Number of stocks (k)',
    riskAversion: 'Risk aversion (q)',
    run: 'Run Optimization',
    running: 'Optimizing...',
    efficientFrontier: 'Efficient Frontier',
    weightDistribution: 'Weight Distribution',
    selectedStocks: 'Selected Stocks',
    portfolioReturn: 'Portfolio Return',
    portfolioRisk: 'Portfolio Risk',
    portfolioSharpe: 'Portfolio Sharpe',
    riskReturnScatter: 'Risk-Return Scatter',
  },
  quantum: {
    title: 'QAOA Quantum Portfolio Optimization',
    params: 'QAOA Parameters',
    selectK: 'Number of stocks (k)',
    riskAversion: 'Risk aversion (q)',
    depth: 'Circuit depth (p)',
    restarts: 'Random restarts',
    forceRerun: 'Force rerun',
    run: 'Run QAOA',
    running: 'QAOA optimizing...',
    results: 'Optimization Results',
    selectedStocks: 'Selected Stocks',
    costGap: 'Cost Gap',
    optimalEnergy: 'Optimal Energy',
    nQubits: 'Qubits',
    penaltyWeight: 'Penalty Weight',
    normFactor: 'Norm Factor',
    bitstringDistribution: 'Bitstring Probability Distribution',
    weightDistribution: 'Weight Distribution',
    bruteForceComparison: 'Brute Force Comparison',
    portfolioReturn: 'Portfolio Return',
    portfolioRisk: 'Portfolio Risk',
    portfolioSharpe: 'Portfolio Sharpe',
    bruteForceReturn: 'Brute Force Return',
    bruteForceRisk: 'Brute Force Risk',
    bruteForceSharpe: 'Brute Force Sharpe',
  },
  compare: {
    title: 'Classical vs Quantum Comparison',
    params: 'Comparison Parameters',
    selectK: 'Number of stocks (k)',
    riskAversion: 'Risk aversion (q)',
    depth: 'Circuit depth (p)',
    restarts: 'Random restarts',
    run: 'Run Comparison',
    running: 'Comparing...',
    metricsTable: 'Performance Metrics Comparison',
    method: 'Method',
    classicalMethod: 'Classical Markowitz',
    quantumMethod: 'QAOA Quantum',
    bruteForceMethod: 'Brute Force',
    portfolioReturn: 'Portfolio Return',
    portfolioRisk: 'Portfolio Risk',
    portfolioSharpe: 'Sharpe Ratio',
    costGap: 'Cost Gap',
    selectedStocks: 'Selected Stocks',
    weightComparison: 'Weight Comparison',
    efficientFrontier: 'Efficient Frontier',
    riskReturnChart: 'Risk-Return Comparison',
  },
  message: {
    loadFailed: 'Failed to load data',
    networkError: 'Network error. Please try again later.',
    optimizeSuccess: 'Optimization completed',
    optimizeFailed: 'Optimization failed. Please retry.',
    noData: 'No data available',
  },
  common: {
    loading: 'Loading...',
    retry: 'Retry',
    percent: '%',
  },
},
```

## Existing npm Dependencies Used

- `vue` (3.x)
- `vue-i18n`
- `element-plus`
- `echarts`

No new dependencies are required.

## API Endpoints

All endpoints are proxied through the qccp-web backend `/finance-qaoa` prefix to the Finance-QAOA FastAPI service (port 8006).

| Method | URL | Request | Response | apiCode |
|--------|-----|---------|----------|---------|
| GET | `/finance-qaoa/api/health` | - | `{ status, service, port }` | (TBD) |
| GET | `/finance-qaoa/api/stocks` | - | `{ stocks: [...], tiers: {...} }` | (TBD) |
| GET | `/finance-qaoa/api/stock/{symbol}/history` | `?days=365` | `{ symbol, history: [{date, close}] }` | (TBD) |
| GET | `/finance-qaoa/api/statistics` | `?tier=demo` | `{ symbols, annual_returns, annual_volatilities, sharpe_ratios, max_drawdowns, total_returns, correlation, correlation_matrix, annual_covariance, price_history }` | (TBD) |
| POST | `/finance-qaoa/api/optimize/classical` | `{ tier, k, q }` | `{ weights, portfolio_return, portfolio_risk, portfolio_sharpe, efficient_frontier, selected_stocks, top_k_selection, stock_points, symbols, tier }` | (TBD) |
| POST | `/finance-qaoa/api/optimize/quantum` | `{ tier, k, q, depth, restarts, force }` | `{ symbols, tier, k, q, solution, selected_indices, selected_stocks, weights, portfolio_return, portfolio_risk, portfolio_sharpe, cost_gap, optimal_energy, penalty_weight, norm_factor, n_qubits, depth, top_bitstrings, brute_force }` | (TBD) |
| POST | `/finance-qaoa/api/compare` | `{ tier, k, q, depth, restarts }` | `{ symbols, tier, k, q, classical: {...}, quantum: {...}, bruteforce: {...}, efficient_frontier }` | (TBD) |

> **Note:** `apiCode` values must be provided by the backend team. The API module uses `@/utils/axios` which handles `apiCode` headers automatically.

## Footer

Footer is NOT used on this page (it is a workflow/tool page, not a marketing landing page).

## Login Permission

No login is required for this page (`requireAuth: false`).

## Verification

```bash
npm run build
```

The page should build without errors. All i18n keys must resolve in both zh and en locales.
