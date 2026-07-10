# VQE H2 分子基态能量计算 — 天衍量子应用

## 概述

本应用使用变分量子本征求解器 (VQE) 计算 H2 分子在 STO-3G 基组下的基态能量，并与经典 Hartree-Fock 基线进行对比。VQE 量子算法成功捕获了电子关联效应，达到化学精度要求。

## 量子 vs 经典结果

| 方法 | 能量 (Hartree) | 与精确值误差 (mHartree) |
|------|----------------|------------------------|
| Hartree-Fock (经典基线) | -1.0637 | 793.62 |
| VQE (量子算法) | **-1.8573** | **0.00** |
| 精确对角化 (参考) | -1.8573 | 0.00 (定义) |

**VQE 相对经典基线改进 793.6 mHartree，达到化学精度 (≤1.6 mHartree)。**

## 算法配置

- **分子**: H2 (STO-3G, 键长 0.735 Å)
- **量子比特**: 2 (Bravyi-Kitaev parity mapping)
- **Ansatz**: 硬件高效 (RY-RZ-CX, 2 layers, 8 参数)
- **优化器**: COBYLA (maxiter=500, tol=1e-6)
- **后端**: cqlib.StatevectorSimulator
- **电路深度**: 6

## 项目结构

```
vqe_h2/
├── algorithms/
│   ├── __init__.py
│   ├── hamiltonian.py      # H2 Hamiltonian 定义
│   ├── baseline.py         # 经典基线 (HF + 精确对角化)
│   └── vqe.py              # VQE 量子算法
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 后端
│   └── static/
│       └── index.html      # 本地演示页面
├── qccp_page/              # 天衍云页面 (Vue SFC)
│   ├── project-files/src/
│   ├── locales/
├── application_brief.md
├── requirements.json
├── application_manifest.json
├── solution_plan.md
├── algorithm_route.md
├── validation_plan.md
├── baseline_report.json
├── quantum_report.json
├── convergence.json
├── README.md
├── INTEGRATE.md
└── verification_report.md
```

## 快速开始

### 运行算法

```bash
# 经典基线
cd /code/cqlib_app/vqe_h2 && python -m algorithms.baseline

# VQE 量子算法
cd /code/cqlib_app/vqe_h2 && python -m algorithms.vqe
```

### 启动本地演示

```bash
cd /code/cqlib_app/vqe_h2 && python -m app.main
# 浏览器访问本地服务端口
```

### API 端点

端点详情见 `application_manifest.json` 的 `local_demo.endpoints` 字段。

## 依赖

- cqlib (量子计算 SDK)
- numpy
- scipy
- fastapi
- uvicorn

## 局限性

- 所有结果基于模拟器 (cqlib.StatevectorSimulator)，非真实硬件
- 仅覆盖 H2 分子最小基组 (STO-3G)
- 化学精度阈值 (1.6 mHartree) 为约定标准
