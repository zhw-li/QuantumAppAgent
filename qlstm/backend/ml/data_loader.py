"""
QLSTM 时间序列预测 — 数据预处理模块

功能:
    1. 加载股票 CSV 数据
    2. 技术指标特征工程（收益率、均线、波动率、RSI、成交量变化率）
    3. MinMaxScaler 归一化（保留 scaler 用于反归一化）
    4. 滑动窗口序列构造 (seq_len → pred_len)
    5. 时序切分 train/val/test（不乱序）
    6. 返回 PyTorch DataLoader

导出:
    - load_and_preprocess()   主入口
    - inverse_transform_close() 反归一化 Close 列
    - get_raw_data()          获取原始 DataFrame（可视化用）
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset

# ──────────────────────────────────────────────
# 常量 / 默认值
# ──────────────────────────────────────────────
_DEFAULT_SEQ_LEN = 20
_DEFAULT_PRED_LEN = 1
_DEFAULT_BATCH_SIZE = 32
_TRAIN_RATIO = 0.7
_VAL_RATIO = 0.15
# TEST_RATIO = 0.15  (剩余部分)

# 特征列名（按构造顺序排列，Close 在 index 0）
FEATURE_COLS: list[str] = [
    "Close",
    "Returns",
    "MA_5",
    "MA_10",
    "MA_20",
    "Volatility_5",
    "Volatility_10",
    "RSI_14",
    "Volume_Change",
]


# ══════════════════════════════════════════════
#  公开接口
# ══════════════════════════════════════════════

def get_raw_data(data_path: str | Path) -> pd.DataFrame:
    """读取原始 CSV，返回按日期升序排列的 DataFrame（仅用于可视化）。

    Parameters
    ----------
    data_path : str | Path
        CSV 文件路径，需包含 Date, Close, Volume 等列。

    Returns
    -------
    pd.DataFrame
        原始数据，Date 已转为 datetime 并设为索引。
    """
    if not os.path.isfile(str(data_path)):
        raise FileNotFoundError(f"数据文件不存在: {data_path}")

    df = pd.read_csv(str(data_path), parse_dates=["Date"])
    _validate_columns(df, {"Date", "Close", "Volume"})
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def inverse_transform_close(
    scaler: MinMaxScaler,
    values: np.ndarray | torch.Tensor,
    feature_idx: int = 0,
) -> np.ndarray:
    """仅对 Close 列做反归一化。

    Parameters
    ----------
    scaler : MinMaxScaler
        训练时拟合的 scaler，必须包含全部特征维度。
    values : array-like, shape (N,) 或 (N, 1)
        归一化后的 Close 列数值。
    feature_idx : int, default 0
        Close 在特征矩阵中的列索引（默认第 0 列）。

    Returns
    -------
    np.ndarray, shape (N,)
        反归一化后的真实价格。
    """
    arr = np.asarray(values, dtype=np.float32).reshape(-1)
    n_features = scaler.n_features_in_
    # 构造与 scaler 维度一致的零矩阵，填入对应列
    dummy = np.zeros((len(arr), n_features), dtype=np.float32)
    dummy[:, feature_idx] = arr
    inv = scaler.inverse_transform(dummy)
    return inv[:, feature_idx]


def load_and_preprocess(
    data_path: str | Path,
    seq_len: int = _DEFAULT_SEQ_LEN,
    pred_len: int = _DEFAULT_PRED_LEN,
    batch_size: int = _DEFAULT_BATCH_SIZE,
) -> Tuple[DataLoader, DataLoader, DataLoader, MinMaxScaler, list[str]]:
    """主入口：加载 → 特征工程 → 归一化 → 序列构造 → DataLoader。

    Parameters
    ----------
    data_path : str | Path
        CSV 路径。
    seq_len : int
        输入窗口长度（历史步数）。
    pred_len : int
        预测步数（当前固定为 1）。
    batch_size : int
        DataLoader 批大小。

    Returns
    -------
    train_loader, val_loader, test_loader : DataLoader
        训练 / 验证 / 测试数据加载器。
    scaler : MinMaxScaler
        已拟合的归一化器，可用于反归一化。
    feature_cols : list[str]
        特征列名列表，顺序与模型输入一致。
    """
    # ---- 1. 加载原始数据 ----
    if not os.path.isfile(str(data_path)):
        raise FileNotFoundError(f"数据文件不存在: {data_path}")

    df = pd.read_csv(str(data_path), parse_dates=["Date"])
    _validate_columns(df, {"Date", "Close", "Volume"})
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ---- 2. 特征工程 ----
    df = _engineer_features(df)

    # ---- 3. 去除 NaN 行（由均线/RSI 产生）----
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    if len(df) < seq_len + pred_len + 10:
        raise ValueError(
            f"有效数据仅 {len(df)} 行，不足以构造 seq_len={seq_len} 的序列"
        )

    # ---- 4. 归一化 ----
    feature_cols = FEATURE_COLS.copy()
    data_matrix = df[feature_cols].values.astype(np.float32)

    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data_matrix).astype(np.float32)

    # ---- 5. 滑动窗口序列 ----
    X, y = _create_sequences(data_scaled, seq_len, pred_len)

    # ---- 6. 时序切分 (不乱序) ----
    n = len(X)
    train_end = int(n * _TRAIN_RATIO)
    val_end = int(n * (_TRAIN_RATIO + _VAL_RATIO))

    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]

    # ---- 7. 构建 DataLoader ----
    train_loader = _make_loader(X_train, y_train, batch_size, shuffle=True)
    val_loader = _make_loader(X_val, y_val, batch_size, shuffle=False)
    test_loader = _make_loader(X_test, y_test, batch_size, shuffle=False)

    return train_loader, val_loader, test_loader, scaler, feature_cols


# ══════════════════════════════════════════════
#  内部函数
# ══════════════════════════════════════════════

def _validate_columns(df: pd.DataFrame, required: set[str]) -> None:
    """校验 DataFrame 是否包含所需列。"""
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"CSV 缺少必要列: {missing}")


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """技术指标特征工程。

    新增列:
        Returns        日收益率 Close_t / Close_{t-1} - 1
        MA_5/10/20     简单移动均线
        Volatility_5/10 滚动标准差（波动率）
        RSI_14         14 日相对强弱指标
        Volume_Change  成交量变化率
    """
    close = df["Close"]

    # 日收益率
    df["Returns"] = close.pct_change()

    # 移动均线
    df["MA_5"] = close.rolling(window=5, min_periods=5).mean()
    df["MA_10"] = close.rolling(window=10, min_periods=10).mean()
    df["MA_20"] = close.rolling(window=20, min_periods=20).mean()

    # 波动率（滚动标准差）
    df["Volatility_5"] = close.pct_change().rolling(window=5, min_periods=5).std()
    df["Volatility_10"] = close.pct_change().rolling(window=10, min_periods=10).std()

    # RSI_14
    df["RSI_14"] = _compute_rsi(close, period=14)

    # 成交量变化率
    df["Volume_Change"] = df["Volume"].pct_change()

    return df


def _compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """计算 RSI (Relative Strength Index)。

    采用 Wilder 平滑方法 (EMA)。

    Parameters
    ----------
    series : pd.Series
        价格序列。
    period : int
        RSI 计算周期，默认 14。

    Returns
    -------
    pd.Series
        RSI 值，范围 0–100。
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    # Wilder 平滑：首值用 SMA，后续用 EMA
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # 全零 loss → RSI = 100
    rsi[avg_loss == 0] = 100.0

    return rsi


def _create_sequences(
    data: np.ndarray,
    seq_len: int,
    pred_len: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """滑动窗口构造监督学习序列。

    Parameters
    ----------
    data : np.ndarray, shape (T, F)
        归一化后的特征矩阵。
    seq_len : int
        输入窗口长度。
    pred_len : int
        预测步长。

    Returns
    -------
    X : np.ndarray, shape (N, seq_len, F)
    y : np.ndarray, shape (N, pred_len)
        预测目标为 Close 列（index 0）在 t+1 … t+pred_len 时刻的值。
    """
    T, F = data.shape
    n_samples = T - seq_len - pred_len + 1
    if n_samples <= 0:
        raise ValueError(
            f"数据长度 T={T} 不足以生成 seq_len={seq_len} + pred_len={pred_len} 的序列"
        )

    X = np.empty((n_samples, seq_len, F), dtype=np.float32)
    y = np.empty((n_samples, pred_len), dtype=np.float32)

    for i in range(n_samples):
        X[i] = data[i : i + seq_len]
        # 目标：Close 列（第 0 列）在 seq_len 之后的 pred_len 步
        y[i] = data[i + seq_len : i + seq_len + pred_len, 0]

    return X, y


def _make_loader(
    X: np.ndarray,
    y: np.ndarray,
    batch_size: int,
    shuffle: bool = False,
) -> DataLoader:
    """将 numpy 数组封装为 DataLoader。"""
    X_t = torch.from_numpy(X)                       # (N, seq_len, F)
    y_t = torch.from_numpy(y)                       # (N, pred_len)
    dataset = TensorDataset(X_t, y_t)

    # drop_last=False 保证测试集样本不丢失
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=False,
        num_workers=0,   # 兼容 Windows / 单机调试
        pin_memory=False,
    )


# ══════════════════════════════════════════════
#  直接运行测试
# ══════════════════════════════════════════════
if __name__ == "__main__":
    DATA_PATH = Path(__file__).resolve().parents[3] / "dataset" / "AAPL.csv"
    print(f"[data_loader] 数据路径: {DATA_PATH}")

    train_loader, val_loader, test_loader, scaler, feature_cols = load_and_preprocess(
        DATA_PATH, seq_len=20, pred_len=1, batch_size=32
    )

    # 统计信息
    total = len(train_loader.dataset) + len(val_loader.dataset) + len(test_loader.dataset)
    print(f"[data_loader] 特征列: {feature_cols}")
    print(f"[data_loader] 样本总数: {total}  "
          f"(train={len(train_loader.dataset)}, "
          f"val={len(val_loader.dataset)}, "
          f"test={len(test_loader.dataset)})")
    print(f"[data_loader] Scaler range: {scaler.data_min_[:3]} → {scaler.data_max_[:3]} (前3列)")

    # 检查一个 batch 的形状
    X_batch, y_batch = next(iter(train_loader))
    print(f"[data_loader] X batch shape: {X_batch.shape}  dtype: {X_batch.dtype}")
    print(f"[data_loader] y batch shape: {y_batch.shape}  dtype: {y_batch.dtype}")

    # 反归一化验证
    close_idx = feature_cols.index("Close")
    recovered = inverse_transform_close(scaler, y_batch[:5, 0].numpy(), close_idx)
    print(f"[data_loader] 反归一化 y[:5]: {recovered}")

    # 原始数据读取验证
    raw = get_raw_data(DATA_PATH)
    print(f"[data_loader] 原始数据: {len(raw)} 行, 日期范围 {raw['Date'].min().date()} → {raw['Date'].max().date()}")
