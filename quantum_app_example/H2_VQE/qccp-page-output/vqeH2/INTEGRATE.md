# INTEGRATE.md — vqeH2 Page

## 1. Page Info

- **Page Name**: VQE-H2 分子基态能量量子计算
- **pageKey**: `vqeH2`
- **Module**: solution
- **Final Route**: `/solution/vqe-h2`

## 2. File Copy Destinations

| Source | Destination |
|--------|-------------|
| `project-files/src/views/solution/vqeH2/index.vue` | `src/views/solution/vqeH2/index.vue` |
| `project-files/src/api/vqeH2/index.js` | `src/api/vqeH2/index.js` |

## 3. Route Object

Append to the solution children array in `src/router/index.js`:

```js
{
  path: 'vqe-h2',
  name: 'vqeH2',
  component: () => import('@/views/solution/vqeH2/index.vue'),
  meta: {
    title: 'VQE-H2',
    keepAlive: false,
  },
},
```

## 4. Chinese i18n (append to `src/utils/lang/zh.js`)

```js
vqeH2: {
  banner: {
    title: 'VQE-H2 分子基态能量量子计算',
    desc: '基于VQE变分量子特征求解器计算H2氢分子基态能量，与经典精确对角化对比，自动迭代优化直至达到化学精度',
  },
  config: {
    title: '计算配置',
    hint: '选择H2分子键长并设置优化参数',
    selectBond: '选择键长 (Å)',
    optParams: '优化参数',
    maxIter: '最大迭代轮数',
    maxIterDesc: '每轮增加ansatz层数和重启次数，逐步逼近精确值',
    bondLengthUnit: '键长 (Å)',
  },
  info: {
    molecule: '分子',
    basis: '基组',
    mapping: '映射',
    qubits: '量子比特',
    accuracy: '化学精度',
  },
  solve: {
    start: '启动 VQE 量子求解',
    solving: 'VQE 优化计算中...',
  },
  message: {
    solveFailed: '求解失败',
  },
  result: {
    title: '计算结果',
    totalTime: '总耗时',
    vqeEnergy: 'VQE 基态能量',
    classicalEnergy: '经典精确能量',
    gap: '能量差距',
    status: '优化状态',
    reached: '达到化学精度',
    notReached: '未达化学精度',
    iterProcess: '迭代优化过程',
    convergence: '收敛曲线',
    iterDetail: '迭代详情',
    iteration: '轮次',
    layers: 'Ansatz层数',
    restarts: '重启次数',
    nParams: '参数数量',
    energyUnit: '能量 (Hartree)',
    classicalExact: '经典精确',
    iterN: '第{n}轮',
    time: '耗时',
    vqeLabel: 'VQE量子算法',
    classicalLabel: '经典精确对角化',
    pecTitle: 'H2 势能曲线',
  },
},
```

## 5. English i18n (append to `src/utils/lang/en.js`)

```js
vqeH2: {
  banner: {
    title: 'VQE-H2 Molecular Ground State Energy',
    desc: 'Compute H2 ground state energy using VQE variational quantum eigensolver, compare with classical exact diagonalization, auto-iterate until chemical accuracy',
  },
  config: {
    title: 'Configuration',
    hint: 'Select H2 bond lengths and optimization parameters',
    selectBond: 'Select Bond Lengths (Å)',
    optParams: 'Optimization Parameters',
    maxIter: 'Max Iterations',
    maxIterDesc: 'Each iteration increases ansatz layers and restarts to approach exact value',
    bondLengthUnit: 'Bond Length (Å)',
  },
  info: {
    molecule: 'Molecule',
    basis: 'Basis',
    mapping: 'Mapping',
    qubits: 'Qubits',
    accuracy: 'Chemical Accuracy',
  },
  solve: {
    start: 'Start VQE Quantum Solver',
    solving: 'VQE Optimizing...',
  },
  message: {
    solveFailed: 'Solve failed',
  },
  result: {
    title: 'Results',
    totalTime: 'Total Time',
    vqeEnergy: 'VQE Ground Energy',
    classicalEnergy: 'Classical Exact Energy',
    gap: 'Energy Gap',
    status: 'Status',
    reached: 'Chemical Accuracy Reached',
    notReached: 'Not Yet Reached',
    iterProcess: 'Iteration Progress',
    convergence: 'Convergence Curves',
    iterDetail: 'Iteration Details',
    iteration: 'Iter',
    layers: 'Ansatz Layers',
    restarts: 'Restarts',
    nParams: 'Params',
    energyUnit: 'Energy (Hartree)',
    classicalExact: 'Classical Exact',
    iterN: 'Iter {n}',
    time: 'Time',
    vqeLabel: 'VQE Quantum Algorithm',
    classicalLabel: 'Classical Exact Diagonalization',
    pecTitle: 'H2 Potential Energy Curve',
  },
},
```

## 6. Existing Dependencies Used

- `vue`, `vue-i18n`, `element-plus`, `echarts` — all already in project
- `@/utils/axios.js` — already in project

No new npm dependencies needed.

## 7. API Details

| Function | URL | Method | Request | Response |
|----------|-----|--------|---------|----------|
| `getInfo` | `/api/vqe-h2/info` | GET | - | `{ molecule, basis, n_qubits, ... }` |
| `solveVQE` | `/api/vqe-h2/solve` | POST | `{ bond_lengths, max_iterations }` | `{ task_id, results: [...], total_time }` |
| `getEnergyCurve` | `/api/vqe-h2/energy_curve` | GET | - | `{ bond_lengths, classical_energies, vqe_energies }` |

## 8. Verification

```bash
npm run build
```
