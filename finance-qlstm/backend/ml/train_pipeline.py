"""
训练流水线
- 经典LSTM训练
- QLSTM训练
- 评估指标计算（RMSE, MAE, MAPE）
- 结果保存与加载
"""

import json
import os
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ml.data_loader import StockDataset, prepare_sequences
from ml.classic_lstm import ClassicLSTM
from ml.qlstm import QLSTM


# 结果保存目录
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")


def set_seed(seed: int = 42):
    """设置随机种子，确保可复现性"""
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """计算评估指标

    Args:
        y_true: 真实值（反归一化后）
        y_pred: 预测值（反归一化后）

    Returns:
        {"RMSE": float, "MAE": float, "MAPE": float}
    """
    # 避免除零：MAPE中过滤接近零的真实值
    mask = np.abs(y_true) > 1e-6
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    if mask.sum() > 0:
        mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
    else:
        mape = 0.0

    return {"RMSE": rmse, "MAE": mae, "MAPE": mape}


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    target_scaler,
    X_test: np.ndarray,
    y_test: np.ndarray,
    epochs: int = 50,
    lr: float = 0.001,
    patience: int = 15,
    model_name: str = "model",
) -> dict:
    """通用训练函数

    Args:
        model: 模型
        train_loader: 训练数据DataLoader
        test_loader: 测试数据DataLoader
        target_scaler: 目标归一化器（用于反归一化）
        X_test: 测试集输入
        y_test: 测试集标签
        epochs: 训练轮数
        lr: 学习率
        patience: 早停耐心值
        model_name: 模型名称（用于日志）

    Returns:
        {"metrics": {"RMSE": ..., "MAE": ..., "MAPE": ...},
         "predictions": [...],
         "train_losses": [...],
         "params": int}
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    train_losses = []
    best_loss = float("inf")
    best_state = None
    no_improve_count = 0

    print(f"\n{'='*50}")
    print(f"开始训练 {model_name}")
    print(f"参数数量: {sum(p.numel() for p in model.parameters() if p.requires_grad)}")
    print(f"{'='*50}")

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        batch_count = 0

        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            batch_count += 1

        avg_loss = epoch_loss / batch_count
        train_losses.append(avg_loss)

        # 早停检查
        if avg_loss < best_loss:
            best_loss = avg_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            no_improve_count = 0
        else:
            no_improve_count += 1

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")

        if no_improve_count >= patience:
            print(f"  早停于 Epoch {epoch+1}，无改善轮数: {no_improve_count}")
            break

    # 恢复最佳模型
    if best_state is not None:
        model.load_state_dict(best_state)

    # 在测试集上评估
    model.eval()
    with torch.no_grad():
        X_test_t = torch.tensor(X_test, dtype=torch.float64)
        y_pred_scaled = model(X_test_t).numpy()

    # 反归一化
    y_pred_real = target_scaler.inverse_transform(y_pred_scaled).flatten()
    y_test_real = target_scaler.inverse_transform(y_test).flatten()

    # 计算指标
    metrics = calculate_metrics(y_test_real, y_pred_real)
    print(f"\n{model_name} 测试指标: RMSE={metrics['RMSE']:.4f}, MAE={metrics['MAE']:.4f}, MAPE={metrics['MAPE']:.2f}%")

    return {
        "metrics": metrics,
        "predictions": y_pred_real.tolist(),
        "train_losses": train_losses,
        "params": sum(p.numel() for p in model.parameters() if p.requires_grad),
    }


def run_training(
    stock: str = "AAPL",
    seq_len: int = 20,
    hidden_size: int = 8,
    n_qubits: int = 4,
    qlstm_epochs: int = 30,
    lstm_epochs: int = 50,
    seed: int = 42,
) -> dict:
    """完整训练流水线：数据准备→训练LSTM→训练QLSTM→保存结果

    Args:
        stock: 股票代码
        seq_len: 时序窗口长度
        hidden_size: 隐藏层维度
        n_qubits: 量子比特数
        qlstm_epochs: QLSTM训练轮数
        lstm_epochs: LSTM训练轮数
        seed: 随机种子

    Returns:
        完整结果字典
    """
    set_seed(seed)

    # 数据准备
    print(f"\n加载数据: {stock}")
    data = prepare_sequences(stock=stock, seq_len=seq_len)

    n_features = data["n_features"]
    train_loader = data["train_loader"]
    test_loader = data["test_loader"]
    target_scaler = data["target_scaler"]
    X_test = data["X_test"]
    y_test = data["y_test"]
    dates_test = data["dates_test"]
    actual_test = data["actual_test"]

    # ========= 训练经典LSTM =========
    set_seed(seed)
    lstm_model = ClassicLSTM(
        input_size=n_features,
        hidden_size=hidden_size,
        num_layers=1,
    )

    # 为LSTM创建batch_size=32的DataLoader
    lstm_train_loader = DataLoader(
        train_loader.dataset, batch_size=32, shuffle=True
    )

    t0 = time.time()
    lstm_result = train_model(
        model=lstm_model,
        train_loader=lstm_train_loader,
        test_loader=test_loader,
        target_scaler=target_scaler,
        X_test=X_test,
        y_test=y_test,
        epochs=lstm_epochs,
        lr=0.001,
        patience=15,
        model_name="Classic LSTM",
    )
    lstm_time = time.time() - t0
    print(f"Classic LSTM 训练耗时: {lstm_time:.1f}s")

    # ========= 训练QLSTM =========
    set_seed(seed)
    qlstm_model = QLSTM(
        input_size=n_features,
        hidden_size=hidden_size,
        n_qubits=n_qubits,
        layers=2,
        num_layers=1,
    )

    # 为QLSTM创建batch_size=16的DataLoader（量子模拟较慢）
    qlstm_train_loader = DataLoader(
        train_loader.dataset, batch_size=16, shuffle=True
    )

    t0 = time.time()
    qlstm_result = train_model(
        model=qlstm_model,
        train_loader=qlstm_train_loader,
        test_loader=test_loader,
        target_scaler=target_scaler,
        X_test=X_test,
        y_test=y_test,
        epochs=qlstm_epochs,
        lr=0.005,
        patience=15,
        model_name="QLSTM",
    )
    qlstm_time = time.time() - t0
    print(f"QLSTM 训练耗时: {qlstm_time:.1f}s")

    # ========= 汇总结果 =========
    # 计算改进百分比
    improvement = {}
    for metric in ["RMSE", "MAE", "MAPE"]:
        lstm_val = lstm_result["metrics"][metric]
        qlstm_val = qlstm_result["metrics"][metric]
        if lstm_val != 0:
            improvement[metric] = round((lstm_val - qlstm_val) / lstm_val * 100, 2)
        else:
            improvement[metric] = 0.0

    results = {
        "stock": stock,
        "seq_len": seq_len,
        "hidden_size": hidden_size,
        "n_qubits": n_qubits,
        "QLSTM_metrics": qlstm_result["metrics"],
        "LSTM_metrics": lstm_result["metrics"],
        "QLSTM_predictions": qlstm_result["predictions"],
        "LSTM_predictions": lstm_result["predictions"],
        "QLSTM_train_losses": qlstm_result["train_losses"],
        "LSTM_train_losses": lstm_result["train_losses"],
        "dates_test": [str(d) if not isinstance(d, str) else d for d in dates_test],
        "actual_test": actual_test,
        "QLSTM_params": qlstm_result["params"],
        "LSTM_params": lstm_result["params"],
        "improvement": improvement,
        "QLSTM_time": round(qlstm_time, 1),
        "LSTM_time": round(lstm_time, 1),
    }

    # 保存结果到文件
    save_results(results, stock)

    return results


def save_results(results: dict, stock: str):
    """保存训练结果到JSON文件

    Args:
        results: 结果字典
        stock: 股票代码
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    filepath = os.path.join(RESULTS_DIR, f"{stock}_results.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"结果已保存: {filepath}")


def load_results(stock: str) -> dict | None:
    """加载已保存的训练结果

    Args:
        stock: 股票代码

    Returns:
        结果字典，若不存在返回None
    """
    filepath = os.path.join(RESULTS_DIR, f"{stock}_results.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
