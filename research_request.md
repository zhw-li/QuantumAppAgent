# QLSTM 量子时间序列预测天衍云平台应用

## 应用目标
使用 /dataset 中的 12 支 DOW 成分股真实数据（2018-2022），构建 QLSTM (Quantum LSTM) vs Classic LSTM 时间序列预测对比平台，部署为天衍云可展示应用。

## 数据
- 路径: /dataset/ (AAPL, BA, CAT, CSCO, HD, IBM, JNJ, JPM, KO, MMM, MSFT, WMT)
- 格式: CSV (Date, Open, High, Low, Close, Adj Close, Volume)
- 时间范围: 2018-01-02 ~ 2022-12-30, 每股约 1258 个交易日
- 用户明确反对合成数据集

## 用户工作流
1. 选择股票
2. 点击训练/预测
3. 查看 QLSTM vs Classic LSTM 预测对比图
4. 查看评估指标对比 (RMSE, MAE, MAPE)
5. 查看训练曲线
6. 查看原始数据

## 输入/输出
- 输入: 股票代码、预测天数、序列长度
- 输出: 预测值、指标对比、训练曲线、原始数据

## 约束
- 天衍云平台展示 (qccp-web SFC)
- cqlib SDK 构建 QLSTM 量子层
- 保存到 /Users/lizhaowei/code/EvoScientist/finance-qlstm
- Lite 代码生成模式

## 主要指标
- RMSE (越低越好)
- 辅助: MAE, MAPE
