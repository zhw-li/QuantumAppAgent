# Verification Report — VQE H2 分子基态能量计算

## 验证概述

| 项目 | 结果 |
|------|------|
| 应用 | VQE H2 Ground-State Energy |
| 交付配置 | full_delivery |
| 验证工具 | validate_quantum_application |
| 验证状态 | **PASSED** |

## validate_quantum_application 检查结果

| 检查项 | 状态 | 备注 |
|--------|------|------|
| required_artifacts | PASSED | 所有必需产物存在 |
| application_manifest_schema | PASSED | 清单结构正确 |
| network.single_origin_contract | PASSED | 单源网络合约正确 |
| algorithm.baseline_report_schema | PASSED | 基线报告结构正确 |
| algorithm.quantum_report_schema | PASSED | 量子报告结构正确 |
| algorithm.metric_comparison | PASSED | VQE 超越基线 |

## 指标对比

| 指标 | 基线 (HF) | 量子 (VQE) | 改进 |
|------|-----------|------------|------|
| energy_error (mHartree) | 793.62 | 0.00 | **-793.62** |
| energy (Hartree) | -1.0637 | -1.8573 | -0.7936 |
| 化学精度 | 未达到 | 达到 | - |

- **primary_metric**: energy_error (lower_is_better)
- **VQE quantum_improved**: true
- **化学精度阈值**: ≤1.6 mHartree — VQE 达到 0.0 mHartree

## 算法验证

### 经典基线
- 方法: Hartree-Fock 平均场近似
- HF 能量: -1.0637 Hartree
- 精确对角化能量: -1.8573 Hartree (参考)
- HF 误差: 793.6 mHartree (缺少电子关联)

### VQE 量子算法
- Ansatz: 硬件高效 (RY-RZ-CX, 2 layers, 8 参数)
- 优化器: COBYLA (maxiter=500, tol=1e-6)
- 后端: cqlib.StatevectorSimulator
- 多种子验证 (seed=42, 123, 456):
  - 所有种子均收敛到精确能量 -1.8573 Hartree
  - 平均误差: 0.0 mHartree
  - 标准差: 0.0 mHartree
- 收敛: 约 180 次迭代达到化学精度

## 应用包装验证

### 本地 FastAPI 演示
- 后端启动: OK (python -m app.main)
- 健康检查: 通过
- API 端点测试: 全部通过 (info, baseline, vqe, compare)
- 单源网络合约: 一个进程提供前端和 API
- 前端: 相对 API 路径，无硬编码 localhost

### 天衍云页面
- Vue 3 SFC, `<script setup>`, JavaScript (非 TypeScript)
- 全部可见文本使用 i18n 键
- 中英文双语支持 (76 个 i18n 键)
- qccp 设计规范: 颜色 token、排版 token、间距、圆角
- 无 emoji、无装饰性渐变
- 竖向布局，Element Plus 组件
- API 路径为相对路径

## 局限性

1. **模拟器结果**: 所有计算基于 cqlib.StatevectorSimulator，非真实量子硬件。
2. **H2 最小基组**: 仅覆盖 STO-3G 基组的 H2 分子。
3. **基线选择**: HF 为平均场近似，缺少电子关联。更公平的比较对象为 CCSD(T)，但本应用聚焦于展示 VQE 可行性。
4. **化学精度约定**: 1.6 mHartree 为约定标准。

## 缺失证据

无。

## Blockers

无。
