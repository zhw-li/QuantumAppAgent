# UC_QAOA — 机组组合量子优化平台

基于 QAOA（Quantum Approximate Optimization Algorithm，量子近似优化算法）求解机组组合（Unit Commitment）问题，实现发电成本最小化，与经典暴力搜索对比。

## 概述

本平台使用 cqlib SDK 实现 QAOA 算法求解机组组合问题。机组组合是电力系统的经典优化问题：决定各发电机组在各时段的开关状态（ON/OFF），在满足负载平衡约束下最小化总燃料成本。问题被建模为 QUBO（二次无约束二值优化），经归一化后由 QAOA 在量子电路上求解，与暴力枚举的经典精确解对比。

## 核心算法

### 量子方法 (QAOA)
1. **QUBO 建模**: H = Σ x[i,t]·C_i + λ·(D_t − Σ x[i,t]·P_i)²（燃料成本 + 负载平衡惩罚）
2. **归一化**: QUBO 矩阵归一化到 [−1,1] 改善 QAOA 优化景观
3. **量子电路**: p 层 QAOA ansatz（H 初始化 → 代价哈密顿量 ZZ/Z 项 → 混合哈密顿量 RX）
4. **优化器**: COBYLA（scipy），多 restart
5. **可行解搜索**: 从 top-k 采样中搜索最优可行解（最高概率解 ≠ 最优可行解）

### 经典基线（暴力枚举）
- 枚举所有 2^n 比特串，按燃料成本排序，取最低成本的可行解（n≤8 可行）

## 实验结果（3 规模，QAOA p=2, restarts=5）

| 规模 | qubit | QAOA 成本 | 经典最优 | gap(%) | 可行 |
|------|-------|----------|---------|--------|------|
| 2×2 | 4 | 19724.44 | 19724.44 | **0.0%** | ✅ |
| 3×2 | 6 | 28067.22 | 28067.22 | **0.0%** | ✅ |
| 4×2 | 8 | 28674.86 | 28067.22 | 2.16% | ✅ |

**关键发现**: QAOA 在小规模（4-6 qubit）上找到精确最优解（gap 0%），在 8 qubit 上保持可行且近最优（gap 2.16%）。所有规模均返回满足负载平衡的可行解（3/3）。详见 `artifacts/quantum_report.json`。

## 技术栈

### 量子算法
- **cqlib SDK**: 量子电路（Circuit/Parameter）、StatevectorSimulator
- **numpy/scipy**: QUBO 建模、COBYLA 优化

### 后端
- **FastAPI**: 4 个 API 端点，端口 8001

### 前端（CDN 预览版）
- Vue 3 CDN + Element Plus CDN + ECharts CDN

### 天衍云集成版
- Vue 3 SFC + Element Plus + Vue I18n，详见 `qccp-page-output/ucQaoa/INTEGRATE.md`

## 快速启动

```bash
pip install cqlib numpy scipy fastapi uvicorn
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001
# 访问 http://localhost:8001/
```

## 复现实验报告

```bash
# 3 规模实测（每规模数秒）
curl -X POST http://localhost:8001/api/solve -H "Content-Type: application/json" \
  -d '{"generator_ids":["A","B"],"loads":[400,600],"qaoa_layers":2,"restarts":5}'
curl -X POST http://localhost:8001/api/solve -H "Content-Type: application/json" \
  -d '{"generator_ids":["A","B","C"],"loads":[700,700],"qaoa_layers":2,"restarts":5}'
curl -X POST http://localhost:8001/api/solve -H "Content-Type: application/json" \
  -d '{"generator_ids":["A","B","C","D"],"loads":[700,700],"qaoa_layers":2,"restarts":5}'
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/generators` | 发电机组列表 + 负载选项 |
| POST | `/api/solve` | QAOA 求解（含暴力对比） |
| POST | `/api/solve-classical` | 经典暴力搜索 |
| GET | `/api/validate` | 验证配置（qubit 数） |

## 标准产物（7 件套）

| 产物 | 路径 | 说明 |
|------|------|------|
| requirements.json | `artifacts/requirements.json` | 结构化需求 |
| solution_plan.md | `solution_plan.md` | 交付计划与门禁 |
| baseline_report.json | `artifacts/baseline_report.json` | 经典基线（暴力枚举） |
| quantum_report.json | `artifacts/quantum_report.json` | 量子方法（QAOA，3 规模） |
| verification_report.md | `verification_report.md` | 验证报告 |
| README.md | `README.md` | 本文件 |
| INTEGRATE.md | `qccp-page-output/ucQaoa/INTEGRATE.md` | 天衍云集成说明 |

## 项目结构

```
UC_QAOA/
├── backend/
│   ├── main.py            # FastAPI 服务（端口 8001，含 QAOA 算法）
│   └── requirements.txt
├── frontend/
│   ├── index.html         # CDN 预览页面
│   ├── css/style.css
│   └── js/app.js
├── qccp-page-output/ucQaoa/   # 天衍云 SFC 页面
├── artifacts/             # 标准报告产物
├── solution_plan.md
├── verification_report.md
└── README.md
```

## 局限性

- 仅模拟器（cqlib StatevectorSimulator），非真实硬件
- 8 qubit 出现 2.16% gap，反映 QAOA 在更大组合问题上的启发式局限
- 暴力基线仅 n≤20 可行；更大规模需其他经典启发式基线
