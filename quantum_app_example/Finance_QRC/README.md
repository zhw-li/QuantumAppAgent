# 量子储备池计算金融预测平台 (Finance-QRC)

Quantum Reservoir Computing vs Classic Reservoir Computing for stock price prediction.

## 概述

本平台实现了量子储备池计算(QRC)与经典储备池计算(Classic RC / Echo State Network)在股票价格预测任务上的对比。量子储备池使用 cqlib SDK 构建固定参数量子电路作为储备池，仅训练经典读出层，实现了极端参数效率。

## 核心算法

### 量子储备池计算 (QRC)
1. **输入编码**: RY 角度编码，将股票特征缩放至 [0, π] 后通过 RY 门编码到量子比特
2. **量子储备池**: 随机初始化的 RY/RZ 旋转 + CNOT 环形纠缠（参数固定，不参与训练）
3. **测量**: 对每个量子比特测量 Pauli-Z 期望值 → n_qubits 维特征
4. **非线性增强**: [<Z_q>, <Z_q>², mean(x)] → 2×n_qubits+1 维读出特征
5. **读出层**: 岭回归(Ridge Regression)从储备池状态预测目标价格

### 经典储备池计算 (Classic RC / ESN)
1. **储备池**: 随机稀疏循环矩阵 W_res（谱半径 < 1 保证稳定性）
2. **状态更新**: h_t = tanh(W_res @ h_{t-1} + W_in @ x_t)
3. **读出层**: 岭回归从储备池状态预测目标价格

## 实验结果 (5 stocks, 3 seeds 平均 ± std)

| 股票 | Classic RC RMSE | QRC RMSE | RMSE改进 | 参数效率 |
|------|----------------|----------|----------|----------|
| AAPL | 4.60 ± 0.21 | 7.53 ± 1.15 | -63.6% | 99.53% |
| MSFT | 5.23 ± 0.04 | 7.60 ± 0.46 | -45.2% | 99.53% |
| **JPM** | **8.61 ± 0.40** | **5.97 ± 0.92** | **+30.1%** | 99.53% |
| JNJ | 1.23 ± 0.005 | 1.74 ± 0.16 | -41.2% | 99.53% |
| **V** | **7.56 ± 0.36** | **6.29 ± 0.78** | **+16.2%** | 99.53% |

**关键发现**: QRC 在 JPM 和 V 上显著超越 Classic RC（RMSE 改进 16-30%），仅使用 0.47% 的参数（46 vs 9702）。非线性特征增强对 QRC 性能至关重要。结果为 3 seeds（42/123/456）平均，含标准差；详见 `artifacts/baseline_report.json` 与 `artifacts/quantum_report.json`。

## 技术栈

### 量子算法
- **cqlib SDK**: 量子电路构建、StatevectorSimulator 模拟
- **numpy / sklearn**: 岭回归读出层

### 后端
- **FastAPI**: 9 个 API 端点
- **uvicorn**: ASGI 服务器
- **端口**: 8009

### 前端（CDN 预览版）
- **Vue 3 CDN** + **Element Plus CDN** + **ECharts CDN**
- 独立 HTML 页面，无需构建

### 天衍云集成版
- **Vue 3 SFC** + Element Plus + Vue I18n
- qccp-web 兼容页面，中英双语
- 4 个子组件: PredictionChart, MetricsCard, ReservoirScatter, CircuitInfo

## 快速启动

```bash
# 安装依赖
pip install cqlib yfinance scikit-learn numpy fastapi uvicorn

# 启动后端 + 前端
cd backend
uvicorn main:app --host 0.0.0.0 --port 8009

# 访问 http://localhost:8009/
```

## 复现实验报告

```bash
cd backend
# 复现 5 股票 × 3 seeds 的报告数据（写入 artifacts/）
python run_experiment.py --tier demo --n_qubits 4 --depth 2 --window_size 5 --seeds 42 123 456
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/health | GET | 健康检查 |
| /api/stocks | GET | 可用股票列表 |
| /api/params | GET | 默认参数和范围 |
| /api/solve | POST | 运行 QRC vs Classic RC 对比 |
| /api/result/{ticker} | GET | 获取缓存结果 |
| /api/compare | GET | 多股对比摘要 |
| /api/circuit | GET | 量子电路信息 + QCIS |
| /api/reservoir-states | GET | 储备池状态可视化数据 |
| /api/raw-data/{ticker} | GET | 原始 OHLCV 数据 |

## 天衍云集成

详见 `qccp-page-output/quantumReservoir/INTEGRATE.md`

## 项目结构

```
Finance_QRC/
├── backend/
│   ├── main.py           # FastAPI 服务（端口 8009）
│   ├── qrc_model.py      # QRC + ClassicRC 实现
│   ├── data_loader.py    # 数据加载预处理
│   └── run_experiment.py # 实验运行器（生成报告数据）
├── frontend/
│   ├── index.html        # CDN 预览页面
│   └── static/
│       ├── app.js        # Vue 3 应用逻辑
│       └── style.css     # 自定义样式
├── qccp-page-output/
│   └── quantumReservoir/ # 天衍云 SFC 页面
│       ├── project-files/src/views/solution/quantumReservoir/
│       └── INTEGRATE.md
├── artifacts/                    # 标准报告产物
│   ├── requirements.json         # 结构化需求
│   ├── baseline_report.json      # 经典基线报告（含 3-seed std）
│   ├── quantum_report.json       # 量子方法报告（含 3-seed std）
│   └── results/                  # 实验明细 JSON
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
| baseline_report.json | `artifacts/baseline_report.json` | 经典基线（cqlib-sdk 契约） |
| quantum_report.json | `artifacts/quantum_report.json` | 量子方法（cqlib-sdk 契约） |
| verification_report.md | `verification_report.md` | 验证报告 |
| README.md | `README.md` | 本文件 |
| INTEGRATE.md | `qccp-page-output/quantumReservoir/INTEGRATE.md` | 天衍云集成说明 |



## 局限性

- 仅使用模拟器（cqlib StatevectorSimulator），非真实量子硬件
- 4 量子比特限制了储备池状态维度
- 非线性特征增强对 QRC 性能至关重要
- 逐样本状态向量模拟比经典 RC 慢
