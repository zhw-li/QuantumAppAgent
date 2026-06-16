"""
经典 LSTM 模型 — 股票价格时序预测基线
========================================
架构: 2 层 LSTM (hidden=64) + 全连接头 (64→32→1)
用于与 QLSTM (量子长短期记忆) 模型进行对比实验。
"""

import copy
import math

import torch
import torch.nn as nn
import numpy as np


# ──────────────────────────────────────────────
# 1. 模型定义
# ──────────────────────────────────────────────

class ClassicLSTM(nn.Module):
    """经典 LSTM 股票价格预测模型

    Parameters
    ----------
    n_features : int
        输入特征维度 (约 10，含技术指标)
    hidden_size : int
        LSTM 隐藏层维度，默认 64
    num_layers : int
        LSTM 堆叠层数，默认 2
    dropout : float
        LSTM 层间 dropout 概率，默认 0.2
    """

    def __init__(
        self,
        n_features: int = 10,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()

        self.n_features = n_features
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # LSTM 主干：batch_first=True → 输入形状 (batch, seq_len, n_features)
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )

        # 全连接预测头
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Parameters
        ----------
        x : Tensor, shape (batch, seq_len, n_features)

        Returns
        -------
        out : Tensor, shape (batch, 1)
            预测的下一个时间步收盘价（归一化后）
        """
        # LSTM 编码：取最后一个时间步的隐藏状态
        lstm_out, _ = self.lstm(x)          # (batch, seq_len, hidden_size)
        last_hidden = lstm_out[:, -1, :]    # (batch, hidden_size)

        # 全连接映射到标量预测
        out = self.fc(last_hidden)           # (batch, 1)
        return out


# ──────────────────────────────────────────────
# 2. 训练函数
# ──────────────────────────────────────────────

def train_classic_lstm(
    train_loader,
    val_loader,
    n_features: int = 10,
    epochs: int = 100,
    lr: float = 1e-3,
    device: str = "cpu",
):
    """训练经典 LSTM 模型

    使用 MSE 损失 + Adam 优化器，配合 ReduceLROnPlateau 学习率调度
    和早停机制 (patience=20)。

    Parameters
    ----------
    train_loader : DataLoader
        训练集数据加载器，每批 (x, y) 形状分别为 (B, S, F) 和 (B, 1)
    val_loader : DataLoader
        验证集数据加载器
    n_features : int
        输入特征维度
    epochs : int
        最大训练轮数
    lr : float
        初始学习率
    device : str
        计算设备，'cpu' 或 'cuda'

    Returns
    -------
    model : ClassicLSTM
        验证集上最优模型（已加载 best 权重）
    train_losses : list[float]
        每轮训练损失
    val_losses : list[float]
        每轮验证损失
    best_epoch : int
        最优验证损失对应的轮次（从 1 开始计数）
    """

    # ---- 设备 & 模型 ----
    device = torch.device(device)
    model = ClassicLSTM(n_features=n_features).to(device)

    # ---- 损失 & 优化器 ----
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # ---- 学习率调度器：验证损失停滞 10 轮则降低学习率 ----
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=10, min_lr=1e-6
    )

    # ---- 早停参数 ----
    early_stop_patience = 20
    best_val_loss = float("inf")
    best_model_state = None
    epochs_no_improve = 0
    best_epoch = 0

    train_losses = []
    val_losses = []

    for epoch in range(1, epochs + 1):
        # ========== 训练阶段 ==========
        model.train()
        epoch_train_loss = 0.0
        n_train_batches = 0

        for x_batch, y_batch in train_loader:
            x_batch = x_batch.to(device)  # (B, S, F)
            y_batch = y_batch.to(device)  # (B, 1)

            optimizer.zero_grad()
            pred = model(x_batch)         # (B, 1)
            loss = criterion(pred, y_batch)
            loss.backward()
            optimizer.step()

            epoch_train_loss += loss.item()
            n_train_batches += 1

        avg_train_loss = epoch_train_loss / max(n_train_batches, 1)
        train_losses.append(avg_train_loss)

        # ========== 验证阶段 ==========
        model.eval()
        epoch_val_loss = 0.0
        n_val_batches = 0

        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                x_batch = x_batch.to(device)
                y_batch = y_batch.to(device)

                pred = model(x_batch)
                loss = criterion(pred, y_batch)

                epoch_val_loss += loss.item()
                n_val_batches += 1

        avg_val_loss = epoch_val_loss / max(n_val_batches, 1)
        val_losses.append(avg_val_loss)

        # ---- 学习率调度 ----
        scheduler.step(avg_val_loss)

        # ---- 记录最优模型 ----
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_epoch = epoch
            best_model_state = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1

        # ---- 日志输出（每 10 轮或最优轮） ----
        if epoch % 10 == 0 or epoch == 1 or epochs_no_improve == 0:
            current_lr = optimizer.param_groups[0]["lr"]
            print(
                f"[Epoch {epoch:>3d}/{epochs}] "
                f"train_loss={avg_train_loss:.6f}  "
                f"val_loss={avg_val_loss:.6f}  "
                f"lr={current_lr:.2e}  "
                f"best_epoch={best_epoch}"
            )

        # ---- 早停判断 ----
        if epochs_no_improve >= early_stop_patience:
            print(f"\n⏹ 早停触发：验证损失已 {early_stop_patience} 轮未改善")
            break

    # ---- 恢复最优模型权重 ----
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        print(f"✅ 已加载第 {best_epoch} 轮最优模型 (val_loss={best_val_loss:.6f})")

    return model, train_losses, val_losses, best_epoch


# ──────────────────────────────────────────────
# 3. 评估函数
# ──────────────────────────────────────────────

def evaluate_model(model, test_loader, scaler, feature_idx: int = -1, device: str = "cpu"):
    """在测试集上评估模型，返回原始价格尺度下的指标

    Parameters
    ----------
    model : ClassicLSTM
        已训练的模型
    test_loader : DataLoader
        测试集数据加载器
    scaler : fitted scaler
        用于逆归一化的 scaler（须支持 inverse_transform）
    feature_idx : int
        目标特征在特征矩阵中的列索引，默认 -1（最后一列为收盘价）
    device : str
        计算设备

    Returns
    -------
    metrics : dict
        包含 MSE, RMSE, MAE, MAPE 四项指标
    predictions : np.ndarray, shape (N,)
        预测值（原始价格尺度）
    actuals : np.ndarray, shape (N,)
        真实值（原始价格尺度）
    """

    device = torch.device(device)
    model.eval()

    all_preds = []
    all_actuals = []

    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            x_batch = x_batch.to(device)
            pred = model(x_batch)  # (B, 1)

            all_preds.append(pred.cpu().numpy())
            all_actuals.append(y_batch.numpy())

    # 拼接所有批次
    predictions_norm = np.concatenate(all_preds, axis=0)   # (N, 1)
    actuals_norm = np.concatenate(all_actuals, axis=0)     # (N, 1)

    # ---- 逆归一化到原始价格尺度 ----
    # 构造与 scaler 训练时相同形状的虚拟矩阵，仅填充目标列
    n_samples = predictions_norm.shape[0]
    n_features_total = scaler.n_features_in_ if hasattr(scaler, "n_features_in_") else scaler.scale_.shape[0]

    pred_dummy = np.zeros((n_samples, n_features_total))
    actual_dummy = np.zeros((n_samples, n_features_total))

    # 将预测值 / 真实值放入目标列（支持负索引）
    col_idx = feature_idx if feature_idx >= 0 else n_features_total + feature_idx
    pred_dummy[:, col_idx] = predictions_norm[:, 0]
    actual_dummy[:, col_idx] = actuals_norm[:, 0]

    # 逆变换后提取目标列
    predictions = scaler.inverse_transform(pred_dummy)[:, col_idx]
    actuals = scaler.inverse_transform(actual_dummy)[:, col_idx]

    # ---- 计算评估指标 ----
    mse = float(np.mean((predictions - actuals) ** 2))
    rmse = float(math.sqrt(mse))
    mae = float(np.mean(np.abs(predictions - actuals)))

    # MAPE：过滤零值避免除零
    mask = actuals != 0
    if mask.sum() > 0:
        mape = float(np.mean(np.abs((actuals[mask] - predictions[mask]) / actuals[mask]))) * 100
    else:
        mape = float("inf")

    metrics = {
        "MSE": round(mse, 6),
        "RMSE": round(rmse, 6),
        "MAE": round(mae, 6),
        "MAPE": round(mape, 4),  # 百分比，保留 2 位小数
    }

    print("📊 测试集评估结果（原始价格尺度）:")
    print(f"   MSE  = {metrics['MSE']:.6f}")
    print(f"   RMSE = {metrics['RMSE']:.6f}")
    print(f"   MAE  = {metrics['MAE']:.6f}")
    print(f"   MAPE = {metrics['MAPE']:.4f}%")

    return metrics, predictions, actuals


# ──────────────────────────────────────────────
# 4. 快速自测入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    """使用随机数据快速验证模型前向传播与训练流程"""

    from torch.utils.data import DataLoader, TensorDataset

    print("=" * 50)
    print("经典 LSTM 模型 — 快速自测")
    print("=" * 50)

    # ---- 虚构数据 ----
    seq_len, n_features, n_samples = 20, 10, 200
    X = torch.randn(n_samples, seq_len, n_features)
    y = torch.randn(n_samples, 1)

    # 划分训练 / 验证 / 测试
    n_train, n_val = 140, 30
    train_ds = TensorDataset(X[:n_train], y[:n_train])
    val_ds = TensorDataset(X[n_train : n_train + n_val], y[n_train : n_train + n_val])
    test_ds = TensorDataset(X[n_train + n_val :], y[n_train + n_val :])

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32)
    test_loader = DataLoader(test_ds, batch_size=32)

    # ---- 训练 ----
    model, train_losses, val_losses, best_epoch = train_classic_lstm(
        train_loader, val_loader,
        n_features=n_features,
        epochs=10,       # 自测只用少量轮次
        lr=1e-3,
        device="cpu",
    )

    # ---- 评估（使用简易 scaler 模拟） ----
    from sklearn.preprocessing import MinMaxScaler

    # 拟合一个假 scaler（实际项目中应由数据预处理模块提供）
    dummy_data = np.random.rand(100, n_features)
    scaler = MinMaxScaler().fit(dummy_data)

    metrics, preds, actuals = evaluate_model(
        model, test_loader, scaler, feature_idx=-1, device="cpu"
    )

    print(f"\n✅ 自测完成：best_epoch={best_epoch}, 预测形状={preds.shape}")
