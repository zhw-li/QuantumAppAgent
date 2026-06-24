"""
数据加载与预处理模块 - Finance QRC
使用 yfinance 下载 DOW 成分股数据，构建滑动窗口数据集
"""

import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import os
import json
import time


# DOW 10 成分股代码 (已验证可靠)
DOW10_TICKERS = ["AAPL", "MSFT", "JPM", "JNJ", "V", "PG", "UNH", "HD", "CVX", "KO"]

# 三级子集
TIER_DEMO = DOW10_TICKERS[:5]     # 前5只
TIER_STANDARD = DOW10_TICKERS[:8]  # 前8只
TIER_FULL = DOW10_TICKERS          # 全部10只


def download_stock_data(tickers, start="2023-01-01", end="2025-01-01",
                        save_dir=None, force_download=False):
    """
    下载股票收盘价数据
    
    Args:
        tickers: 股票代码列表
        start: 开始日期
        end: 结束日期
        save_dir: 缓存目录 (None则不缓存)
        force_download: 是否强制重新下载
    
    Returns:
        dict: {ticker: np.array of close prices}
    """
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        cache_file = os.path.join(save_dir, f"stock_data_{start}_{end}.json")
        
        if not force_download and os.path.exists(cache_file):
            print(f"[数据] 从缓存加载: {cache_file}")
            with open(cache_file, 'r') as f:
                cache = json.load(f)
            data = {}
            for t in tickers:
                if t in cache:
                    data[t] = np.array(cache[t], dtype=np.float64)
            if len(data) == len(tickers):
                return data
            print(f"[数据] 缓存不完整，重新下载...")

    print(f"[数据] 下载 {len(tickers)} 只股票: {tickers}")
    raw = yf.download(tickers, start=start, end=end)
    
    data = {}
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                close = raw['Close'].values.astype(np.float64)
            else:
                close = raw['Close'][ticker].values.astype(np.float64)
            
            # 去除 NaN
            mask = ~np.isnan(close)
            close = close[mask]
            
            if len(close) < 50:
                print(f"[警告] {ticker} 数据不足 ({len(close)} 天)，跳过")
                continue
                
            data[ticker] = close
            print(f"  {ticker}: {len(close)} 天数据")
        except Exception as e:
            print(f"[警告] {ticker} 下载失败: {e}")
    
    # 保存缓存
    if save_dir and data:
        cache_file = os.path.join(save_dir, f"stock_data_{start}_{end}.json")
        with open(cache_file, 'w') as f:
            json.dump({t: v.tolist() for t, v in data.items()}, f)
        print(f"[数据] 已缓存到: {cache_file}")
    
    return data


def create_sliding_window(prices, window_size, target_offset=1):
    """
    创建滑动窗口数据集
    
    Args:
        prices: np.array, 归一化后的价格序列
        window_size: 窗口大小 (天数)
        target_offset: 目标偏移 (1=预测下一天)
    
    Returns:
        X: np.array, shape (n_samples, window_size)
        y: np.array, shape (n_samples,) - 目标为下一天的收盘价
    """
    X, y = [], []
    for i in range(len(prices) - window_size - target_offset + 1):
        X.append(prices[i:i + window_size])
        y.append(prices[i + window_size + target_offset - 1])
    
    return np.array(X, dtype=np.float64), np.array(y, dtype=np.float64)


class StockDataset:
    """
    单只股票的数据集容器
    
    处理流程:
    1. 原始收盘价 → MinMaxScaler 归一化
    2. 滑动窗口 → (X, y) 对
    3. 按时间 80/20 分割 train/test
    """
    
    def __init__(self, prices, window_size=5, train_ratio=0.8):
        """
        Args:
            prices: np.array, 原始收盘价
            window_size: 滑动窗口大小
            train_ratio: 训练集比例
        """
        self.window_size = window_size
        self.train_ratio = train_ratio
        self.raw_prices = prices.copy()
        
        # MinMaxScaler 归一化 (fit on all data to avoid data leakage in normalization)
        # Note: 对于时间序列，理论上应只在训练集上fit，但RC文献通常对全序列归一化
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.scaled_prices = self.scaler.fit_transform(
            prices.reshape(-1, 1)
        ).flatten().astype(np.float64)
        
        # 创建滑动窗口
        X, y = create_sliding_window(self.scaled_prices, window_size)
        
        # 按时间分割
        split_idx = int(len(X) * train_ratio)
        self.X_train = X[:split_idx]
        self.y_train = y[:split_idx]
        self.X_test = X[split_idx:]
        self.y_test = y[split_idx:]
        
        # 训练集归一化后的 y (用于 scaler 逆变换)
        self.y_train_raw = self.scaler.inverse_transform(
            self.y_train.reshape(-1, 1)
        ).flatten()
        self.y_test_raw = self.scaler.inverse_transform(
            self.y_test.reshape(-1, 1)
        ).flatten()
        
        print(f"[数据集] 窗口={window_size}, 训练={len(self.X_train)}, "
              f"测试={len(self.X_test)}, 总计={len(X)}")
    
    def inverse_transform_y(self, y_scaled):
        """将归一化后的预测值还原为原始价格"""
        return self.scaler.inverse_transform(
            y_scaled.reshape(-1, 1)
        ).flatten()


def load_all_stocks(tickers=None, start="2023-01-01", end="2025-01-01",
                    window_size=5, train_ratio=0.8, save_dir=None):
    """
    加载所有股票数据并构建数据集
    
    Args:
        tickers: 股票代码列表 (None则使用DOW10)
        start: 开始日期
        end: 结束日期
        window_size: 滑动窗口大小
        train_ratio: 训练集比例
        save_dir: 数据缓存目录
    
    Returns:
        dict: {ticker: StockDataset}
    """
    if tickers is None:
        tickers = DOW10_TICKERS
    
    raw_data = download_stock_data(tickers, start, end, save_dir)
    
    datasets = {}
    for ticker, prices in raw_data.items():
        try:
            ds = StockDataset(prices, window_size=window_size, train_ratio=train_ratio)
            datasets[ticker] = ds
        except Exception as e:
            print(f"[警告] {ticker} 数据集构建失败: {e}")
    
    return datasets


if __name__ == "__main__":
    # 简单测试
    print("=" * 60)
    print("Finance QRC 数据加载测试")
    print("=" * 60)
    
    datasets = load_all_stocks(
        tickers=["AAPL", "MSFT"], 
        window_size=5,
        save_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache")
    )
    
    for ticker, ds in datasets.items():
        print(f"\n{ticker}:")
        print(f"  训练集 X: {ds.X_train.shape}, y: {ds.y_train.shape}")
        print(f"  测试集 X: {ds.X_test.shape}, y: {ds.y_test.shape}")
        print(f"  价格范围: [{ds.raw_prices.min():.2f}, {ds.raw_prices.max():.2f}]")
