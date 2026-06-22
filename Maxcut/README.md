# MaxCut QAOA 量子优化求解平台

基于 cqlib SDK 的 QAOA（量子近似优化算法）求解图最大割问题的全栈平台。

## 项目结构

```
Maxcut/
├── main.py              # FastAPI 应用入口（端口 8006）
├── requirements.txt     # Python 依赖
├── maxcut_solver.py     # QAOA MaxCut 求解器（cqlib 实现）
├── graph_utils.py       # 图定义、QUBO 建模、暴力搜索
├── static/
│   ├── index.html       # Vue 3 CDN 前端页面
│   ├── app.js           # 前端逻辑（ECharts 可视化）
│   └── style.css        # 前端样式
└── README.md
```

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8006
```

访问 http://localhost:8006/static/index.html 使用 Web 界面。

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/graphs` | 列出所有预设图 |
| GET | `/api/graph/{name}` | 获取指定预设图数据 |
| POST | `/api/solve` | 运行 QAOA 求解 MaxCut |
| POST | `/api/brute-force` | 运行暴力搜索最优解 |

### 求解请求示例

```bash
# QAOA 求解
curl -X POST http://localhost:8006/api/solve \
  -H "Content-Type: application/json" \
  -d '{"graph_name": "simple_4", "depth": 2, "restarts": 5, "maxiter": 300}'

# 暴力搜索
curl -X POST http://localhost:8006/api/brute-force \
  -H "Content-Type: application/json" \
  -d '{"graph_name": "simple_4"}'

# 自定义图
curl -X POST http://localhost:8006/api/solve \
  -H "Content-Type: application/json" \
  -d '{"edges": [[0,1,1],[1,2,1],[2,0,1]], "n_nodes": 3, "depth": 2}'
```

## 预设图

| 名称 | 节点数 | 边数 | 描述 | 最优切割值 |
|------|--------|------|------|-----------|
| simple_4 | 4 | 4 | 三角形 + 悬挂节点 | 3 |
| medium_6 | 6 | 8 | 环 + 对角线 | 8 |
| large_8 | 8 | 16 | 稠密图 | 11 |

## 算法原理

### MaxCut 问题

给定无向图 G=(V,E,w)，将顶点分为两个不相交的子集 S₀ 和 S₁，使跨越两个子集的边权重之和最大。

### QUBO 建模

- 二值变量 x_i 表示顶点 i 的分区
- 切割值: cut(x) = Σ_{(i,j)∈E} w_{ij} · (x_i + x_j - 2·x_i·x_j)
- QUBO 最小化: f(x) = Σ_{(i,j)∈E} w_{ij} · (2·x_i·x_j - x_i - x_j) = -cut(x)
- 最优切割值 = -min f(x)

### QAOA 实现

- 量子比特数 = 图节点数
- 电路结构: H⊗n → [Cost(γ) · Mixer(β)]^p → 测量
- ZZ 门分解: CNOT(qi,qj) → RZ(qj, 2·γ·Q_ij) → CNOT(qi,qj)
- 优化器: COBYLA + 多次随机重启
- 后处理: 从概率分布中搜索 top-k 可行解

### 关键 cqlib 模式

- `from cqlib import Circuit, Parameter` — 顶级导入
- `from cqlib.simulator import StatevectorSimulator` — 子模块导入
- `Circuit(n_qubits, parameters=names)` — 参数在创建时声明
- `circuit.assign_parameters(dict)` — 返回新电路
- `circuit.measure_all()` — 测量前必须调用
- 比特串顺序: `bits[i] = qubit i`（正向，非 Qiskit 反向）

## 验证结果

三个预设图均已验证 QAOA 达到最优解（cost gap = 0%）：

| 图 | QAOA 割值 | 暴力搜索最优 | 代价偏差 | 量子比特 | QAOA深度 |
|----|----------|-------------|---------|---------|---------|
| simple_4 | 3.0 | 3.0 | 0.0% | 4 | p=2 |
| medium_6 | 8.0 | 8.0 | 0.0% | 6 | p=2 |
| large_8 | 11.0 | 11.0 | 0.0% | 8 | p=3 |

## 天衍云平台集成

项目包含 qccp-web 天衍云平台集成页面，位于 `qccp-page-output/maxcutQaoa/`：

```
qccp-page-output/maxcutQaoa/
├── project-files/
│   └── src/
│       ├── views/solution/maxcutQaoa/
│       │   ├── index.vue          # 主页面 SFC
│       │   └── components/        # 子组件
│       │       ├── GraphPanel.vue # 图可视化
│       │       ├── ResultPanel.vue # 结果展示
│       │       └── ComparePanel.vue # 对比面板
│       └── api/maxcutQaoa/
│           └── index.js           # API 接口
└── INTEGRATE.md                   # 集成说明
```

集成步骤详见 `INTEGRATE.md`，包含路由配置、i18n 中英文条目、API 契约等。

## 返回结果字段

```json
{
  "qaoa_cut": 3,
  "optimal_cut": 3,
  "cost_gap_percent": 0.0,
  "best_partition": [0, 1, 0, 1],
  "cut_edges": [[0, 1, 1], [2, 1, 1], [2, 3, 1]],
  "best_probability": 0.25,
  "circuit_depth": 2,
  "n_qubits": 4,
  "qaoa_params": {"gamma_0": 1.23, "beta_0": 0.45, "gamma_1": 2.34, "beta_1": 0.67},
  "optimization_history": [...],
  "top_probabilities": [
    {"bitstring": "0101", "probability": 0.25, "cut_value": 3}
  ],
  "elapsed_time": 2.5,
  "brute_force": {"optimal_cut": 3, "n_evaluated": 16},
  "qubo": {"norm_factor": 2.0, "qubo_expectation": -3.0}
}
```
