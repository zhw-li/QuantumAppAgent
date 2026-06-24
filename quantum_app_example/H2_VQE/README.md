# H2_VQE — 氢分子基态能量量子计算平台

基于 VQE（Variational Quantum Eigensolver，变分量子本征求解器）计算 H2 氢分子基态能量，与经典精确对角化对比，自动迭代优化直至达到化学精度。

## 概述

本平台使用 cqlib SDK 实现 VQE 算法，求解氢分子（H2）的电子结构哈密顿量基态能量。采用 STO-3G 基组 + Parity mapping + 2-qubit reduction，将问题映射到 2 个量子比特。VQE 使用 hardware-efficient ansatz（RY-RZ + CNOT）+ COBYLA 优化器，与精确对角化的经典基线逐键长对比，评估量子方法的精度。

## 核心算法

### 量子方法 (VQE)
1. **哈密顿量**: H2 分子 2-qubit Pauli 哈密顿量（g_II·I + g_IZ·Z_0 + g_ZI·Z_1 + g_ZZ·Z_0Z_1 + g_XX·X_0X_1）
2. **Ansatz**: Hardware-efficient（每层 RY-RZ per qubit + CNOT 链），Hartree-Fock 初态（qubit 0 占据）
3. **优化器**: COBYLA（scipy），自适应 restarts（5→10→15）+ maxiter（300→500→700）
4. **测量**: Pauli 期望值经基旋转（H/RX）+ statevector 概率计算
5. **迭代优化**: 逐键长递增 ansatz 层数直至化学精度（< 1.6 mHa）

### 经典基线（精确对角化）
- 将 Pauli 哈密顿量转为 4×4 矩阵（numpy.kron），numpy.linalg.eigvalsh 求最低本征值
- 能量 = 电子基态 + 核排斥能 V_nn = 1/(R·1.8897259886)

## 实验结果（全 13 键长，化学精度 1.6 mHa）

| 键长(Å) | 经典精确(Ha) | VQE(Ha) | 误差(mHa) | 化学精度 |
|---------|------------|---------|-----------|---------|
| 0.50 | -0.496278 | -0.496277 | 0.0005 | ✅ |
| 0.70 | -0.988927 | -0.988927 | 0.0000 | ✅ |
| **0.74** | **-1.142098** | **-1.142098** | **0.0000** | ✅ |
| 0.90 | -0.968984 | -0.968983 | 0.0012 | ✅ |
| 1.50 | -0.881752 | -0.881717 | 0.0354 | ✅ |

**关键发现**: VQE 在全部 13 个键长（0.50–3.00 Å）上达到化学精度（13/13 < 1.6 mHa），平均误差仅 0.0316 mHa，全部 1 层 ansatz 即收敛。平衡键长 0.74 Å 处 VQE 与精确解完全吻合。详见 `artifacts/quantum_report.json`。

## 技术栈

### 量子算法
- **cqlib SDK**: 量子电路构建、StatevectorSimulator 模拟、QCIS 转换
- **numpy/scipy**: 哈密顿量对角化、COBYLA 优化器

### 后端
- **FastAPI**: 3 个 API 端点
- **uvicorn**: ASGI 服务器
- **端口**: 8002

### 前端（CDN 预览版）
- **Vue 3 CDN** + **Element Plus CDN** + **ECharts CDN**
- 独立 HTML 页面，无需构建

### 天衍云集成版
- **Vue 3 SFC** + Element Plus + Vue I18n
- qccp-web 兼容页面，中英双语
- 详见 `qccp-page-output/vqeH2/INTEGRATE.md`

## 快速启动

```bash
# 安装依赖
pip install cqlib numpy scipy fastapi uvicorn

# 启动后端 + 前端
cd backend
uvicorn main:app --host 0.0.0.0 --port 8002

# 访问 http://localhost:8002/
```

## 复现实验报告

```bash
# 启动后端后，调用 /api/solve 跑全键长（约 20s）
curl -X POST http://localhost:8002/api/solve \
  -H "Content-Type: application/json" \
  -d '{"bond_lengths":[0.50,0.60,0.70,0.74,0.75,0.80,0.90,1.00,1.25,1.50,2.00,2.50,3.00],"max_iterations":3}'
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/info` | 平台信息（分子/基组/键长范围/化学精度） |
| POST | `/api/solve` | 执行 VQE 计算（含迭代优化+经典对比） |
| GET | `/api/energy_curve` | 完整势能曲线数据 |

## 项目结构

```
H2_VQE/
├── backend/
│   ├── main.py            # FastAPI 服务（端口 8002，含 VQE 算法）
│   └── requirements.txt
├── frontend/
│   ├── index.html         # CDN 预览页面
│   ├── css/style.css
│   └── js/app.js
├── qccp-page-output/
│   └── vqeH2/             # 天衍云 SFC 页面
│       ├── project-files/src/views/solution/vqeH2/
│       └── INTEGRATE.md
├── artifacts/                    # 标准报告产物
│   ├── requirements.json         # 结构化需求
│   ├── baseline_report.json      # 经典基线（精确对角化）
│   ├── quantum_report.json       # 量子方法（VQE，含逐键长误差）
│   └── vqe_experiment_all_bondlengths.json  # 实验明细
├── solution_plan.md              # 交付计划（阶段/成功信号/验证检查）
├── verification_report.md        # 验证报告（对照需求与实测）
└── README.md
```

## 标准产物（7 件套）

本应用遵循 EvoScientist `experiment-pipeline` 标准，产物齐全：

| 产物 | 路径 | 说明 |
|------|------|------|
| requirements.json | `artifacts/requirements.json` | 结构化需求（任务/数据/主指标/成功信号） |
| solution_plan.md | `solution_plan.md` | 交付计划与阶段门禁 |
| baseline_report.json | `artifacts/baseline_report.json` | 经典基线（精确对角化） |
| quantum_report.json | `artifacts/quantum_report.json` | 量子方法（VQE，cqlib-sdk 契约） |
| verification_report.md | `verification_report.md` | 验证报告 |
| README.md | `README.md` | 本文件 |
| INTEGRATE.md | `qccp-page-output/vqeH2/INTEGRATE.md` | 天衍云集成说明 |

## 局限性

- 仅使用模拟器（cqlib StatevectorSimulator），非真实量子硬件
- H2 仅 2 qubits，hardware-efficient ansatz 完全可表达——VQE 与精确解高度吻合，**该结论不能外推到大分子**
- 使用 statevector 模拟（非采样），无测量统计噪声
- 平衡键长实测取 0.75 Å（表中与 0.74 Å 系数相同的最近键长）
