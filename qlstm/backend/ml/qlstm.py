"""
量子长短期记忆网络 (QLSTM) — 基于 cqlib SDK 的时序预测模型
==============================================================
架构思路:
    标准 LSTM 门控: gate = σ(W·x + U·h + b)
    QLSTM 门控:    gate = σ(VQC(x, h) + b)

    每个门 (input/forget/cell/output) 使用独立的变分量子电路 (VQC) 替代线性变换:
    1. 角度编码 (Angle Encoding): 将输入值 (x_t, h_{t-1}) 通过 RY 门编码到量子比特
    2. 变分层 (Variational Layer): RY+RZ 旋转 + CNOT 纠缠，重复 n_layers 次
    3. 测量: 对所有量子比特测量，计算 Z 期望值
    4. 输出: Z 期望值线性投影到门控维度

关键约束 (cqlib SDK):
    - 参数必须在 Circuit 创建时声明
    - assign_parameters 默认返回新电路
    - 测量结果比特反序: bitstring 最右 = Q0
    - 必须调用 measure_all() 后才能模拟
    - 无原生 RZZ 门，需用 CNOT-RZ-CNOT 分解
    - 使用 StatevectorSimulator 进行模拟
"""

from __future__ import annotations

import copy
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator


# ──────────────────────────────────────────────
# 1. VQCBlock — 变分量子电路模块
# ──────────────────────────────────────────────

class VQCBlock(nn.Module):
    """变分量子电路模块，替代线性层

    将输入编码到量子态，经变分层处理后测量 Z 期望值作为输出。

    电路结构:
        编码层: RY(encode_param_i) 对每个量子比特编码输入
        变分层 (×n_layers):
            RY(vary_param) → RZ(vary_param) (每个量子比特)
            CNOT(i, (i+1)%n_qubits) (环状纠缠)
        测量: measure_all() → 计算 Z 期望值

    Parameters
    ----------
    n_qubits : int
        量子比特数，默认 2
    n_layers : int
        变分层重复次数，默认 2
    n_input : int
        输入特征维度，默认 2
        当 n_input > n_qubits 时，自动添加经典预投影层将输入降至 n_qubits 维
    """

    def __init__(self, n_qubits: int = 2, n_layers: int = 2, n_input: int = 2):
        super().__init__()

        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.n_input = n_input  # 原始输入维度
        self.n_encode = n_qubits  # 编码到量子比特的维度 = 量子比特数

        # ── 经典预投影层: 将输入维度降至 n_qubits ──
        # 当 n_input > n_qubits 时需要降维；n_input ≤ n_qubits 时为单位映射
        if n_input != n_qubits:
            self.pre_projection = nn.Linear(n_input, n_qubits)
        else:
            self.pre_projection = None

        # ── 构建参数名列表 ──
        # 编码参数: e_{i} (i=0..n_encode-1)，用于 RY 编码（每个量子比特一个）
        self.encode_param_names: List[str] = [
            f"e_{i}" for i in range(self.n_encode)
        ]

        # 变分参数: v_{layer}_{qubit}，用于 RY+RZ
        self.variational_param_names: List[str] = []
        for layer in range(n_layers):
            for qubit in range(n_qubits):
                self.variational_param_names.append(f"v_{layer}_{qubit}")

        # 所有参数名（必须在 Circuit 创建时声明）
        all_param_names = self.encode_param_names + self.variational_param_names

        # ── 构建量子电路模板 ──
        self._circuit = self._build_circuit(all_param_names)

        # ── PyTorch 可训练参数 ──
        # 变分权重: 初始化为小随机值
        self.variational_weights = nn.Parameter(
            torch.randn(len(self.variational_param_names)) * 0.1
        )

        # 输入缩放因子: 将编码值映射到 [-π, π] 范围（维度 = n_encode）
        self.input_scale = nn.Parameter(torch.ones(self.n_encode))

    def _build_circuit(self, param_names: List[str]) -> Circuit:
        """构建 VQC 量子电路模板

        Parameters
        ----------
        param_names : List[str]
            全部参数名列表（编码 + 变分）

        Returns
        -------
        Circuit
            带有参数化门的量子电路模板
        """
        c = Circuit(self.n_qubits, parameters=param_names)

        # ── 编码层: RY 门编码输入（每个量子比特一个编码参数）──
        for i in range(self.n_encode):
            c.ry(i, Parameter(f"e_{i}"))

        # ── 变分层: RY+RZ 旋转 + CNOT 纠缠 ──
        for layer in range(self.n_layers):
            for qubit in range(self.n_qubits):
                param_name = f"v_{layer}_{qubit}"
                c.ry(qubit, Parameter(param_name))
                c.rz(qubit, Parameter(param_name))
            # 环状纠缠: CNOT(i, (i+1) % n_qubits)
            for qubit in range(self.n_qubits):
                c.cx(qubit, (qubit + 1) % self.n_qubits)

        # ── 测量所有量子比特 ──
        c.measure_all()

        return c

    def _compute_z_expectations(self, measure_probs: Dict[str, float]) -> torch.Tensor:
        """从测量概率分布计算各量子比特的 Z 期望值

        Z 期望值: <Z_i> = Σ_bitstring (1 - 2*bit_i) * P(bitstring)
        其中 bit_i 是 bitstring 中第 i 个量子比特对应的位。

        注意: cqlib 测量结果比特反序，bitstring 最右边 = Q0

        Parameters
        ----------
        measure_probs : Dict[str, float]
            测量概率分布，key 为 bitstring，value 为概率

        Returns
        -------
        torch.Tensor, shape (n_qubits,)
            各量子比特的 Z 期望值
        """
        z_exps = []
        for q in range(self.n_qubits):
            z_exp = 0.0
            for bitstring, prob in measure_probs.items():
                # cqlib 反序: bitstring 最右 = Q0
                # Qq 对应 bitstring[-(q+1)]
                bit = int(bitstring[-(q + 1)])
                # Z 本征值: |0⟩ → +1, |1⟩ → -1
                z_exp += (1 - 2 * bit) * prob
            z_exps.append(z_exp)
        return torch.tensor(z_exps, dtype=torch.float32)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """VQC 前向传播（逐样本模拟）

        Parameters
        ----------
        x : Tensor, shape (batch_size, n_input)
            输入特征

        Returns
        -------
        Tensor, shape (batch_size, n_qubits)
            各量子比特的 Z 期望值
        """
        batch_size = x.shape[0]

        # ── 经典预投影: 降维到 n_qubits ──
        if self.pre_projection is not None:
            x = torch.tanh(self.pre_projection(x))  # tanh 激活保持值域有界

        outputs = []

        # 获取当前变分权重（detached 用于参数绑定）
        var_weights = self.variational_weights.detach()

        for s in range(batch_size):
            # ── 构建参数绑定字典 ──
            param_dict = {}

            # 编码参数: tanh 缩放映射到 [-π, π]
            scaled = torch.tanh(x[s] * self.input_scale) * np.pi
            for i in range(self.n_encode):
                param_dict[f"e_{i}"] = scaled[i].item()

            # 变分参数
            for j, pname in enumerate(self.variational_param_names):
                param_dict[pname] = var_weights[j].item()

            # ── 参数绑定 → 模拟 → 计算 Z 期望值 ──
            bound_circuit = self._circuit.assign_parameters(param_dict)
            sim = StatevectorSimulator(circuit=bound_circuit)
            measure_probs = sim.measure()  # 需先 measure_all()

            z_exps = self._compute_z_expectations(measure_probs)
            outputs.append(z_exps)

        return torch.stack(outputs)  # (batch_size, n_qubits)


# ──────────────────────────────────────────────
# 2. QLSTMCell — 量子 LSTM 单元
# ──────────────────────────────────────────────

class QLSTMCell(nn.Module):
    """量子 LSTM 单元，使用 VQC 替代线性变换

    标准 LSTM 四门: i (input), f (forget), g (cell), o (output)
    每个门使用独立的 VQCBlock 接收 [x_t, h_{t-1}] 输入，
    VQC 输出 (n_qubits 维 Z 期望值) 经线性投影到 n_hidden 维。

    Parameters
    ----------
    n_input : int
        输入特征维度 x_t
    n_hidden : int
        隐藏状态维度 h_t
    n_qubits : int
        VQC 量子比特数，默认 2
    n_layers : int
        VQC 变分层重复次数，默认 2
    """

    def __init__(
        self,
        n_input: int,
        n_hidden: int,
        n_qubits: int = 2,
        n_layers: int = 2,
    ):
        super().__init__()

        self.n_input = n_input
        self.n_hidden = n_hidden

        # VQC 输入维度: [x_t, h_{t-1}] 拼接
        vqc_input_dim = n_input + n_hidden

        # ── 四个独立的 VQC 门控模块 ──
        self.vqc_i = VQCBlock(n_qubits=n_qubits, n_layers=n_layers, n_input=vqc_input_dim)
        self.vqc_f = VQCBlock(n_qubits=n_qubits, n_layers=n_layers, n_input=vqc_input_dim)
        self.vqc_g = VQCBlock(n_qubits=n_qubits, n_layers=n_layers, n_input=vqc_input_dim)
        self.vqc_o = VQCBlock(n_qubits=n_qubits, n_layers=n_layers, n_input=vqc_input_dim)

        # ── 线性投影: VQC 输出 (n_qubits) → 门控维度 (n_hidden) ──
        self.proj_i = nn.Linear(n_qubits, n_hidden)
        self.proj_f = nn.Linear(n_qubits, n_hidden)
        self.proj_g = nn.Linear(n_qubits, n_hidden)
        self.proj_o = nn.Linear(n_qubits, n_hidden)

        # ── 偏置项 ──
        # 遗忘门偏置初始化为 1.0 (类似经典 LSTM 的 forget gate bias trick)
        self.bias_i = nn.Parameter(torch.zeros(n_hidden))
        self.bias_f = nn.Parameter(torch.ones(n_hidden))
        self.bias_g = nn.Parameter(torch.zeros(n_hidden))
        self.bias_o = nn.Parameter(torch.zeros(n_hidden))

    def forward(
        self,
        x_t: torch.Tensor,
        h_prev: torch.Tensor,
        c_prev: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """QLSTM 单元前向传播

        Parameters
        ----------
        x_t : Tensor, shape (batch_size, n_input)
            当前时间步输入
        h_prev : Tensor, shape (batch_size, n_hidden)
            上一时间步隐藏状态
        c_prev : Tensor, shape (batch_size, n_hidden)
            上一时间步细胞状态

        Returns
        -------
        h_t : Tensor, shape (batch_size, n_hidden)
            当前隐藏状态
        c_t : Tensor, shape (batch_size, n_hidden)
            当前细胞状态
        """
        # 拼接 [x_t, h_{t-1}] 作为 VQC 输入
        combined = torch.cat([x_t, h_prev], dim=-1)  # (batch, n_input + n_hidden)

        # ── 四门计算 ──
        # VQC → 线性投影 + 偏置 → 激活函数
        i_gate = torch.sigmoid(
            self.proj_i(self.vqc_i(combined)) + self.bias_i
        )  # (batch, n_hidden)

        f_gate = torch.sigmoid(
            self.proj_f(self.vqc_f(combined)) + self.bias_f
        )  # (batch, n_hidden)

        g_gate = torch.tanh(
            self.proj_g(self.vqc_g(combined)) + self.bias_g
        )  # (batch, n_hidden)

        o_gate = torch.sigmoid(
            self.proj_o(self.vqc_o(combined)) + self.bias_o
        )  # (batch, n_hidden)

        # ── 状态更新 ──
        c_t = f_gate * c_prev + i_gate * g_gate     # 细胞状态
        h_t = o_gate * torch.tanh(c_t)               # 隐藏状态

        return h_t, c_t


# ──────────────────────────────────────────────
# 3. QLSTM — 完整量子 LSTM 时序预测模型
# ──────────────────────────────────────────────

class QLSTM(nn.Module):
    """量子 LSTM 时序预测模型

    结构:
        QLSTMCell (单层) → 全连接预测头

    逐时间步展开 QLSTMCell，取最后时间步隐藏状态做预测。

    Parameters
    ----------
    n_features : int
        输入特征维度
    n_hidden : int
        隐藏状态维度，默认 32
    n_qubits : int
        VQC 量子比特数，默认 2
    n_layers : int
        VQC 变分层重复次数，默认 2
    n_output : int
        输出维度，默认 1
    """

    def __init__(
        self,
        n_features: int,
        n_hidden: int = 32,
        n_qubits: int = 2,
        n_layers: int = 2,
        n_output: int = 1,
    ):
        super().__init__()

        self.n_features = n_features
        self.n_hidden = n_hidden
        self.n_output = n_output

        # QLSTM 单元
        self.qlstm_cell = QLSTMCell(
            n_input=n_features,
            n_hidden=n_hidden,
            n_qubits=n_qubits,
            n_layers=n_layers,
        )

        # 全连接预测头
        self.fc = nn.Sequential(
            nn.Linear(n_hidden, 16),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(16, n_output),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """QLSTM 前向传播

        Parameters
        ----------
        x : Tensor, shape (batch_size, seq_len, n_features)
            输入时序数据

        Returns
        -------
        Tensor, shape (batch_size, n_output)
            预测输出
        """
        batch_size = x.shape[0]
        seq_len = x.shape[1]

        # 初始化隐藏状态和细胞状态为零
        h_t = torch.zeros(batch_size, self.n_hidden, device=x.device, dtype=x.dtype)
        c_t = torch.zeros(batch_size, self.n_hidden, device=x.device, dtype=x.dtype)

        # 逐时间步展开 QLSTM 单元
        for t in range(seq_len):
            x_t = x[:, t, :]  # (batch, n_features)
            h_t, c_t = self.qlstm_cell(x_t, h_t, c_t)

        # 取最后时间步隐藏状态做预测
        out = self.fc(h_t)  # (batch, n_output)
        return out


# ──────────────────────────────────────────────
# 4. 训练函数
# ──────────────────────────────────────────────

def train_qlstm(
    train_loader,
    val_loader,
    n_features: int,
    n_hidden: int = 32,
    n_qubits: int = 2,
    n_layers: int = 2,
    epochs: int = 100,
    lr: float = 0.005,
    device: str = "cpu",
):
    """训练 QLSTM 模型

    使用 MSE 损失 + Adam 优化器，配合 ReduceLROnPlateau 学习率调度
    和早停机制 (patience=15)。

    注意: QLSTM 每步需要量子模拟，训练速度远慢于经典 LSTM。
    建议使用 batch_size ≤ 16 以控制内存和速度。

    Parameters
    ----------
    train_loader : DataLoader
        训练集数据加载器，每批 (x, y) 形状分别为 (B, S, F) 和 (B, 1)
    val_loader : DataLoader
        验证集数据加载器
    n_features : int
        输入特征维度
    n_hidden : int
        隐藏状态维度，默认 32
    n_qubits : int
        VQC 量子比特数，默认 2
    n_layers : int
        VQC 变分层重复次数，默认 2
    epochs : int
        最大训练轮数
    lr : float
        初始学习率
    device : str
        计算设备，'cpu' 或 'cuda'

    Returns
    -------
    model : QLSTM
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
    model = QLSTM(
        n_features=n_features,
        n_hidden=n_hidden,
        n_qubits=n_qubits,
        n_layers=n_layers,
    ).to(device)

    # ---- 损失 & 优化器 ----
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # ---- 学习率调度器 ----
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=8, min_lr=1e-6
    )

    # ---- 早停参数 ----
    early_stop_patience = 15
    best_val_loss = float("inf")
    best_model_state = None
    epochs_no_improve = 0
    best_epoch = 0

    train_losses = []
    val_losses = []

    print("=" * 60)
    print(f"🚀 QLSTM 训练开始 | n_qubits={n_qubits} n_layers={n_layers} "
          f"n_hidden={n_hidden} lr={lr}")
    print("=" * 60)

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
            # 梯度裁剪: 防止量子参数梯度爆炸
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
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

        # ---- 日志输出（每 5 轮或最优轮或第 1 轮） ----
        if epoch % 5 == 0 or epoch == 1 or epochs_no_improve == 0:
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
# 5. 评估函数
# ──────────────────────────────────────────────

def evaluate_qlstm(model, test_loader, scaler, feature_idx: int = -1, device: str = "cpu"):
    """在测试集上评估 QLSTM 模型，返回原始价格尺度下的指标

    与经典 LSTM evaluate_model 保持相同接口。

    Parameters
    ----------
    model : QLSTM
        已训练的 QLSTM 模型
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
    n_samples = predictions_norm.shape[0]
    n_features_total = (
        scaler.n_features_in_
        if hasattr(scaler, "n_features_in_")
        else scaler.scale_.shape[0]
    )

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
        mape = float(
            np.mean(np.abs((actuals[mask] - predictions[mask]) / actuals[mask]))
        ) * 100
    else:
        mape = float("inf")

    metrics = {
        "MSE": round(mse, 6),
        "RMSE": round(rmse, 6),
        "MAE": round(mae, 6),
        "MAPE": round(mape, 4),
    }

    print("📊 QLSTM 测试集评估结果（原始价格尺度）:")
    print(f"   MSE  = {metrics['MSE']:.6f}")
    print(f"   RMSE = {metrics['RMSE']:.6f}")
    print(f"   MAE  = {metrics['MAE']:.6f}")
    print(f"   MAPE = {metrics['MAPE']:.4f}%")

    return metrics, predictions, actuals


# ──────────────────────────────────────────────
# 6. 快速自测入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    """使用随机数据快速验证 QLSTM 模型前向传播与训练流程"""

    from torch.utils.data import DataLoader, TensorDataset

    print("=" * 60)
    print("QLSTM 模型 — 快速自测")
    print("=" * 60)

    # ---- 虚构数据 (小批量以适应量子模拟开销) ----
    seq_len, n_features, n_samples = 5, 3, 16
    X = torch.randn(n_samples, seq_len, n_features)
    y = torch.randn(n_samples, 1)

    # 划分训练 / 验证 / 测试
    n_train, n_val = 10, 3
    train_ds = TensorDataset(X[:n_train], y[:n_train])
    val_ds = TensorDataset(X[n_train : n_train + n_val], y[n_train : n_train + n_val])
    test_ds = TensorDataset(X[n_train + n_val :], y[n_train + n_val :])

    # 小 batch_size: 量子模拟逐样本处理，大批次极慢
    train_loader = DataLoader(train_ds, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=4)
    test_loader = DataLoader(test_ds, batch_size=4)

    # ── 1. 测试 VQCBlock 独立前向 ──
    print("\n--- VQCBlock 前向测试 ---")
    vqc = VQCBlock(n_qubits=2, n_layers=2, n_input=3)
    test_input = torch.randn(4, 3)  # batch=4, input_dim=3
    vqc_out = vqc(test_input)
    print(f"VQCBlock 输入: {test_input.shape}")
    print(f"VQCBlock 输出: {vqc_out.shape} (应为 [4, 2])")
    print(f"VQCBlock 输出值范围: [{vqc_out.min():.4f}, {vqc_out.max():.4f}]")

    # ── 2. 测试 QLSTMCell 独立前向 ──
    print("\n--- QLSTMCell 前向测试 ---")
    cell = QLSTMCell(n_input=n_features, n_hidden=8, n_qubits=2, n_layers=2)
    x_t = torch.randn(4, n_features)
    h_prev = torch.zeros(4, 8)
    c_prev = torch.zeros(4, 8)
    h_out, c_out = cell(x_t, h_prev, c_prev)
    print(f"QLSTMCell h_out: {h_out.shape} (应为 [4, 8])")
    print(f"QLSTMCell c_out: {c_out.shape} (应为 [4, 8])")

    # ── 3. 测试 QLSTM 完整模型前向 ──
    print("\n--- QLSTM 完整模型前向测试 ---")
    model = QLSTM(n_features=n_features, n_hidden=8, n_qubits=2, n_layers=2, n_output=1)
    test_seq = torch.randn(4, seq_len, n_features)
    pred = model(test_seq)
    print(f"QLSTM 输入: {test_seq.shape}")
    print(f"QLSTM 输出: {pred.shape} (应为 [4, 1])")
    print(f"QLSTM 参数量: {sum(p.numel() for p in model.parameters())}")

    # ── 4. 训练测试 (少量 epoch) ──
    print("\n--- QLSTM 训练测试 ---")
    model, train_losses, val_losses, best_epoch = train_qlstm(
        train_loader, val_loader,
        n_features=n_features,
        n_hidden=8,
        n_qubits=2,
        n_layers=2,
        epochs=3,        # 自测只跑 3 轮
        lr=0.005,
        device="cpu",
    )
    print(f"训练完成: best_epoch={best_epoch}, "
          f"最终 train_loss={train_losses[-1]:.6f}, val_loss={val_losses[-1]:.6f}")

    # ── 5. 评估测试 ──
    print("\n--- QLSTM 评估测试 ---")
    from sklearn.preprocessing import MinMaxScaler

    dummy_data = np.random.rand(100, n_features)
    scaler = MinMaxScaler().fit(dummy_data)

    metrics, preds, actuals = evaluate_qlstm(
        model, test_loader, scaler, feature_idx=-1, device="cpu"
    )

    print(f"\n✅ 自测完成：best_epoch={best_epoch}, 预测形状={preds.shape}")
