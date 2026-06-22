"""
数据加载与预处理模块
- 从CSV加载股票数据
- 特征工程：收益率、MA5/MA10/MA20、成交量比率
- MinMaxScaler归一化
- 构造时序样本（滑动窗口）
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import torch
from torch.utils.data import Dataset, DataLoader


# 数据集路径（优先使用/dataset沙盒路径，其次使用宿主机路径）
DATASET_DIR = "/dataset" if os.path.exists("/dataset") else "/Users/lizhaowei/code/EvoScientist/dataset"

# 可用股票列表
AVAILABLE_STOCKS = ["AAPL", "BA", "CAT", "CSCO", "HD", "IBM", "JNJ", "JPM", "KO", "MMM", "MSFT", "WMT"]


class StockDataset(Dataset):
    """股票时序数据集，返回 (seq_x, seq_y) 对"""

    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float64)
        self.y = torch.tensor(y, dtype=torch.float64)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def load_stock_data(stock: str = "AAPL") -> pd.DataFrame:
    """从CSV加载股票数据

    Args:
        stock: 股票代码（如 AAPL）

    Returns:
        DataFrame，包含原始OHLCV数据
    """
    filepath = os.path.join(DATASET_DIR, f"{stock}.csv")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"股票数据文件不存在: {filepath}")

    df = pd.read_csv(filepath, parse_dates=["Date"])
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """特征工程：添加技术指标

    原始特征：Close
    新增特征：
    - returns: 日收益率 = Close_t / Close_{t-1} - 1
    - MA5: 5日均线
    - MA10: 10日均线
    - MA20: 20日均线
    - volume_ratio: 成交量比率 = Volume_t / Volume_{t-1}

    Returns:
        添加特征后的DataFrame（前20行因MA20会有NaN，需drop）
    """
    df = df.copy()

    # 日收益率
    df["returns"] = df["Close"].pct_change()

    # 移动平均线
    df["MA5"] = df["Close"].rolling(window=5).mean()
    df["MA10"] = df["Close"].rolling(window=10).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()

    # 成交量比率
    df["volume_ratio"] = df["Volume"].pct_change()

    # 去除NaN行
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def prepare_sequences(
    stock: str = "AAPL",
    seq_len: int = 20,
    train_ratio: float = 0.8,
):
    """数据预处理主函数：加载→特征工程→归一化→构造序列→划分训练/测试集

    Args:
        stock: 股票代码
        seq_len: 时序窗口长度
        train_ratio: 训练集比例

    Returns:
        dict，包含：
        - train_loader, test_loader: DataLoader
        - feature_scaler, target_scaler: MinMaxScaler（用于反归一化）
        - dates_test: 测试集日期列表
        - actual_test: 测试集真实价格（反归一化后）
        - n_features: 特征数
    """
    # 加载数据
    df = load_stock_data(stock)
    dates_all = df["Date"].tolist()

    # 特征工程
    df = add_features(df)
    dates_all = df["Date"].tolist()

    # 选取特征列
    feature_cols = ["Close", "returns", "MA5", "MA10", "MA20", "volume_ratio"]
    n_features = len(feature_cols)

    # 目标列：Close价格
    target_col = "Close"

    # 归一化（特征和目标分别归一化）
    feature_scaler = MinMaxScaler()
    target_scaler = MinMaxScaler()

    features_scaled = feature_scaler.fit_transform(df[feature_cols].values)
    target_scaled = target_scaler.fit_transform(df[[target_col]].values)

    # 构造滑动窗口序列
    X, y, seq_dates = [], [], []
    for i in range(len(features_scaled) - seq_len):
        X.append(features_scaled[i : i + seq_len])  # (seq_len, n_features)
        y.append(target_scaled[i + seq_len])  # (1,)
        seq_dates.append(dates_all[i + seq_len])

    X = np.array(X, dtype=np.float64)  # (N, seq_len, n_features)
    y = np.array(y, dtype=np.float64)  # (N, 1)

    # 训练/测试划分
    split_idx = int(len(X) * train_ratio)

    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    dates_test = seq_dates[split_idx:]

    # 反归一化真实价格
    actual_test = target_scaler.inverse_transform(y_test).flatten().tolist()

    # 创建DataLoader
    train_dataset = StockDataset(X_train, y_train)
    test_dataset = StockDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    return {
        "train_loader": train_loader,
        "test_loader": test_loader,
        "feature_scaler": feature_scaler,
        "target_scaler": target_scaler,
        "dates_test": dates_test,
        "actual_test": actual_test,
        "n_features": n_features,
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
    }


def get_raw_data(stock: str = "AAPL", days: int = 365) -> dict:
    """获取原始股票数据（用于K线图展示）

    Args:
        stock: 股票代码
        days: 返回最近多少天的数据

    Returns:
        dict: {dates, OHLC, volume}
    """
    df = load_stock_data(stock)
    # 取最近days天
    df = df.tail(days).reset_index(drop=True)

    dates = [d.strftime("%Y-%m-%d") for d in df["Date"].tolist()]
    ohlc = [
        {
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
        }
        for _, row in df.iterrows()
    ]
    volume = [int(row["Volume"]) for _, row in df.iterrows()]

    return {"dates": dates, "OHLC": ohlc, "volume": volume}
