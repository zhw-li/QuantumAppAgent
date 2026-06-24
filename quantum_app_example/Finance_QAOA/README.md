# Finance_QAOA — 量子组合投资优化云平台

基于 QAOA 量子近似优化算法的金融投资组合选择平台，与经典 Markowitz 均值-方差优化对比。

## 功能

- **数据概览**: DOW 10成分股价格走势、三级数据规模(demo/standard/full)
- **统计分析**: 年化收益率、波动率、夏普比率、相关性热力图、风险-收益散点图
- **经典优化**: Markowitz 均值-方差优化 + 有效前沿
- **量子优化**: QAOA 组合选择 + Top-k 可行解搜索 + 暴力搜索对比
- **对比分析**: 经典 vs 量子 vs 暴力搜索三方案对比

## 技术栈

- **后端**: FastAPI + cqlib SDK + scipy + pandas + numpy
- **前端预览**: Vue 3 CDN + Element Plus + ECharts
- **天衍云集成**: Vue 3 SFC + Element Plus + i18n

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端 (端口 8006)
cd /quantum_app_example/Finance_QAOA
python -m backend.main

# 访问 http://localhost:8006
```

## 项目结构

```
Finance_QAOA/
├── backend/
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用 + 静态文件挂载
│   ├── qaoa_solver.py     # QAOA 求解器 (cqlib SDK)
│   ├── qubo_model.py      # QUBO 建模 + 自适应惩罚 + 归一化
│   ├── classical_solver.py # Markowitz 经典求解器
│   └── data_loader.py     # 股票数据加载
├── frontend/
│   ├── index.html         # CDN 预览页面
│   └── static/
│       ├── app.js         # Vue 3 应用逻辑
│       └── style.css      # 样式
├── data/                  # 12支DOW成分股CSV数据
├── results/               # 求解结果缓存
├── qccp-page-output/      # 天衍云 Vue SFC 集成文件
└── requirements.txt
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/stocks` | 列出可用股票 |
| GET | `/api/stock/{symbol}/history` | 股票价格历史 |
| GET | `/api/statistics?tier=demo` | 统计数据 |
| POST | `/api/optimize/classical` | Markowitz 优化 |
| POST | `/api/optimize/quantum` | QAOA 优化 |
| POST | `/api/compare` | 经典+量子对比 |
