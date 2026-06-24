# INTEGRATE.md — ucQaoa Page

## 1. Page Info

- **Page Name**: UC-QAOA 机组组合量子优化
- **pageKey**: `ucQaoa`
- **Module**: solution
- **Final Route**: `/solution/uc-qaoa`

## 2. File Copy Destinations

| Source | Destination |
|--------|-------------|
| `project-files/src/views/solution/ucQaoa/index.vue` | `src/views/solution/ucQaoa/index.vue` |
| `project-files/src/api/ucQaoa/index.js` | `src/api/ucQaoa/index.js` |

## 3. Route Object

Append to the solution children array in `src/router/index.js`:

```js
{
  path: 'uc-qaoa',
  name: 'ucQaoa',
  component: () => import('@/views/solution/ucQaoa/index.vue'),
  meta: {
    title: 'UC-QAOA',
    keepAlive: false,
  },
},
```

## 4. Chinese i18n (append to `src/utils/lang/zh.js`)

```js
ucQaoa: {
  banner: {
    title: 'UC-QAOA 机组组合量子优化',
    desc: '基于QAOA量子近似优化算法，求解多时段机组组合(Unit Commitment)问题，实现发电成本最小化',
  },
  step1: {
    title: '选择发电机组',
    hint: '选择 2-4 个发电机组参与优化',
  },
  gen: {
    maxPower: '最大出力',
    costFunc: '成本函数',
    fullCost: '满载成本',
  },
  step2: {
    title: '配置时段负载',
    hint: '设置每个时段的负载需求 (MW)',
    addPeriod: '添加时段',
    remove: '删除',
    qubit: '量子比特',
  },
  step3: {
    title: 'QAOA 参数设置',
    layers: 'QAOA 层数 (p)',
    layersDesc: '层数越多精度越高，但优化参数也越多',
    restarts: '优化重启次数',
    restartsDesc: '更多重启可提高找到全局最优的概率',
  },
  solve: {
    start: '启动 QAOA 量子求解',
    solving: 'QAOA 优化中...',
  },
  message: {
    solveFailed: '求解失败',
    networkError: '网络异常，请稍后重试',
  },
  result: {
    title: '优化结果',
    success: '求解成功',
    infeasible: '无可行解',
    qaoaCost: 'QAOA 总成本',
    classicalCost: '经典最优成本',
    gap: '最优性差距',
    qubits: '量子比特数',
    layers: 'QAOA 层数',
    time: '求解耗时',
    compare: 'QAOA vs 经典最优对比',
    schedule: '调度方案',
    detailTable: '详细调度表',
    costDistribution: '各时段成本分布',
    totalCost: '总成本',
    cost: '成本',
    total: '合计',
    status: '状态',
    on: '开机',
    off: '关机',
    power: '出力',
    period: '时段',
    totalPower: '总出力',
    loadDemand: '负载需求',
    satisfied: '满足',
    unsatisfied: '不足',
    qaoaLabel: 'QAOA 量子算法',
    classicalLabel: '经典最优解',
  },
},
```

## 5. English i18n (append to `src/utils/lang/en.js`)

```js
ucQaoa: {
  banner: {
    title: 'UC-QAOA Unit Commitment Quantum Optimization',
    desc: 'Solve multi-period Unit Commitment problems using QAOA quantum approximate optimization algorithm to minimize generation costs',
  },
  step1: {
    title: 'Select Generators',
    hint: 'Choose 2-4 generators for optimization',
  },
  gen: {
    maxPower: 'Max Power',
    costFunc: 'Cost Function',
    fullCost: 'Full-load Cost',
  },
  step2: {
    title: 'Configure Period Loads',
    hint: 'Set load demand for each period (MW)',
    addPeriod: 'Add Period',
    remove: 'Remove',
    qubit: 'Qubits',
  },
  step3: {
    title: 'QAOA Parameters',
    layers: 'QAOA Layers (p)',
    layersDesc: 'More layers improve accuracy but add more parameters',
    restarts: 'Optimization Restarts',
    restartsDesc: 'More restarts increase probability of finding global optimum',
  },
  solve: {
    start: 'Start QAOA Quantum Solver',
    solving: 'QAOA Optimizing...',
  },
  message: {
    solveFailed: 'Solve failed',
    networkError: 'Network error, please try again',
  },
  result: {
    title: 'Optimization Result',
    success: 'Success',
    infeasible: 'Infeasible',
    qaoaCost: 'QAOA Total Cost',
    classicalCost: 'Classical Optimal Cost',
    gap: 'Optimality Gap',
    qubits: 'Qubit Count',
    layers: 'QAOA Layers',
    time: 'Solve Time',
    compare: 'QAOA vs Classical Optimal',
    schedule: 'Schedule Plan',
    detailTable: 'Detailed Schedule',
    costDistribution: 'Cost Distribution by Period',
    totalCost: 'Total Cost',
    cost: 'Cost',
    total: 'Total',
    status: 'Status',
    on: 'ON',
    off: 'OFF',
    power: 'Power',
    period: 'Period',
    totalPower: 'Total Power',
    loadDemand: 'Load Demand',
    satisfied: 'Met',
    unsatisfied: 'Unmet',
    qaoaLabel: 'QAOA Quantum Algorithm',
    classicalLabel: 'Classical Optimal',
  },
},
```

## 6. Existing Dependencies Used

- `vue` (already in project)
- `vue-i18n` (already in project)
- `element-plus` (already in project)
- `echarts` (already in project)
- `@/utils/axios.js` (already in project)

No new npm dependencies needed.

## 7. API Details

| Function | URL | Method | Request | Response | apiCode |
|----------|-----|--------|---------|----------|---------|
| `getGenerators` | `/api/uc-qaoa/generators` | GET | - | `{ generators: [...], load_options: [400,600,700] }` | N/A |
| `solveQAOA` | `/api/uc-qaoa/solve` | POST | `{ generator_ids, loads, qaoa_layers, restarts }` | `{ task_id, status, schedule, total_cost, qubit_count, ... }` | N/A |
| `solveClassical` | `/api/uc-qaoa/solve-classical` | POST | `{ generator_ids, loads, qaoa_layers, restarts }` | `{ status, schedule, total_cost, bitstring, ... }` | N/A |

Note: apiCode will be assigned by backend team. Currently the backend runs locally on port 8001 without apiCode gating.

## 8. Footer

Not used.

## 9. Login / Nav

No login permission required. No dedicated nav entry; page is accessible via direct URL `/solution/uc-qaoa`.

## 10. Verification

```bash
npm run build
```
