# INTEGRATE.md — maxcutQaoa Page

## 1. Page Identity

| Field | Value |
| --- | --- |
| Page name | QAOA MaxCut 量子优化求解 |
| pageKey | `maxcutQaoa` |
| Module | `solution` |
| Final route | `/solution/maxcut-qaoa` |

## 2. File Copy Destinations

| Source (generated) | Destination (qccp-web) |
| --- | --- |
| `project-files/src/views/solution/maxcutQaoa/index.vue` | `src/views/solution/maxcutQaoa/index.vue` |
| `project-files/src/views/solution/maxcutQaoa/components/GraphPanel.vue` | `src/views/solution/maxcutQaoa/components/GraphPanel.vue` |
| `project-files/src/views/solution/maxcutQaoa/components/ResultPanel.vue` | `src/views/solution/maxcutQaoa/components/ResultPanel.vue` |
| `project-files/src/views/solution/maxcutQaoa/components/ComparePanel.vue` | `src/views/solution/maxcutQaoa/components/ComparePanel.vue` |
| `project-files/src/api/maxcutQaoa/index.js` | `src/api/maxcutQaoa/index.js` |

## 3. Route Object to Append

Append to the `solution` children array in the router configuration:

```js
{
  path: 'maxcut-qaoa',
  name: 'MaxcutQaoa',
  component: () => import('@/views/solution/maxcutQaoa/index.vue'),
  meta: {
    title: 'maxcutQaoa.title',
  },
},
```

## 4. Chinese i18n Object (append to `src/utils/lang/zh.js`)

```js
maxcutQaoa: {
  title: 'QAOA MaxCut 量子优化求解',
  subtitle: '基于量子近似优化算法的最大割问题求解平台',
  selectGraph: '选择图',
  nodeCount: '节点数',
  edgeCount: '边数',
  description: '描述',
  qaoaDepth: 'QAOA深度',
  restarts: '重启次数',
  maxIterations: '最大迭代',
  startSolve: '开始求解',
  bruteForce: '暴力搜索',
  solving: '求解中...',
  tabGraphCut: '图与割集',
  tabOptimization: '优化过程',
  tabProbability: '概率分布',
  tabCompare: '结果对比',
  qaoaCutValue: 'QAOA割值',
  optimalCutValue: '最优割值',
  costGap: '代价差距',
  circuitDepth: '电路深度',
  qubitCount: '量子比特数',
  solveTime: '求解时间',
  partition: '分区',
  cutEdges: '割边',
  iteration: '迭代',
  expectation: '期望值',
  probability: '概率',
  bitstring: '比特串',
  metric: '指标',
  value: '值',
  unit: '单位',
  percent: '%',
  seconds: '秒',
  noResult: '暂无结果，请先求解',
  simple4: '简单4节点图',
  medium6: '中等6节点图',
  large8: '复杂8节点图',
},
```

## 5. English i18n Object (append to `src/utils/lang/en.js`)

```js
maxcutQaoa: {
  title: 'QAOA MaxCut Quantum Optimization',
  subtitle: 'Maximum Cut Problem Solver Based on Quantum Approximate Optimization Algorithm',
  selectGraph: 'Select Graph',
  nodeCount: 'Nodes',
  edgeCount: 'Edges',
  description: 'Description',
  qaoaDepth: 'QAOA Depth',
  restarts: 'Restarts',
  maxIterations: 'Max Iterations',
  startSolve: 'Start Solving',
  bruteForce: 'Brute Force',
  solving: 'Solving...',
  tabGraphCut: 'Graph & Cut',
  tabOptimization: 'Optimization',
  tabProbability: 'Probability',
  tabCompare: 'Comparison',
  qaoaCutValue: 'QAOA Cut Value',
  optimalCutValue: 'Optimal Cut Value',
  costGap: 'Cost Gap',
  circuitDepth: 'Circuit Depth',
  qubitCount: 'Qubits',
  solveTime: 'Solve Time',
  partition: 'Partition',
  cutEdges: 'Cut Edges',
  iteration: 'Iteration',
  expectation: 'Expectation',
  probability: 'Probability',
  bitstring: 'Bitstring',
  metric: 'Metric',
  value: 'Value',
  unit: 'Unit',
  percent: '%',
  seconds: 's',
  noResult: 'No results yet, please solve first',
  simple4: 'Simple 4-Node Graph',
  medium6: 'Medium 6-Node Graph',
  large8: 'Complex 8-Node Graph',
},
```

## 6. Existing npm Dependencies Used

| Package | Purpose |
| --- | --- |
| vue | Vue 3 Composition API |
| element-plus | UI components (el-select, el-tabs, el-button, el-form, el-table, el-empty) |
| echarts | Graph visualization, convergence chart, probability chart |
| vue-i18n | Internationalization (`$t()` / `t()`) |
| vue-router | Route navigation (`useRoute`, `useRouter`) |
| axios (via `@/utils/axios.js`) | HTTP requests |

No new dependencies required.

## 7. API Contracts

| Function | URL | Method | Request Body | Response (res.data) | apiCode |
| --- | --- | --- | --- | --- | --- |
| `getGraphs()` | `/maxcut-qaoa/graphs` | GET | — | `{ code: 200, data: [{ name, label, nodes, edges }] }` | — |
| `getGraph(name)` | `/maxcut-qaoa/graph/${name}` | GET | — | `{ code: 200, data: { nodes: [], edges: [] } }` | — |
| `solveQaoa(data)` | `/maxcut-qaoa/solve` | POST | `{ graphName, depth, restarts, maxiter }` | `{ code: 200, data: { partition, cut_edges, cut_value, optimization_history, probabilities, n_qubits, circuit_depth, elapsed_time } }` | — |
| `bruteForce(data)` | `/maxcut-qaoa/brute-force` | POST | `{ graphName }` | `{ code: 200, data: { optimal_cut, optimal_partition, cut_edges } }` | — |

**Note**: API field names accept both snake_case and camelCase variants (the page handles both patterns with `??` fallbacks). Backend should return `code: 200` on success.

## 8. Footer Used

No. This is a workflow/tool page, not a landing page.

## 9. Login Permission / Nav Entry

No login permission required. No nav entry needed — the page is accessed via direct URL or route link.

## 10. Verification Command

```bash
npm run build
```

This should compile without errors after all files are copied to their destinations and i18n keys are appended.
