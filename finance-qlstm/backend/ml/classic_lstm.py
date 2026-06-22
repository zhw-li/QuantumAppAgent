"""
经典LSTM基线模型
- 标准PyTorch nn.LSTM
- 与QLSTM使用相同的hidden_size进行公平对比
"""

import torch
import torch.nn as nn


class ClassicLSTM(nn.Module):
    """经典LSTM股票预测模型

    结构：
    - LSTM层：input_size → hidden_size
    - 全连接层：hidden_size → 1（预测下一个收盘价）

    Args:
        input_size: 输入特征维度（默认6：Close, returns, MA5, MA10, MA20, volume_ratio）
        hidden_size: 隐藏层维度（与QLSTM保持一致）
        num_layers: LSTM堆叠层数
    """

    def __init__(self, input_size: int = 6, hidden_size: int = 8, num_layers: int = 1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dtype=torch.float64,
        )
        self.fc = nn.Linear(hidden_size, 1, dtype=torch.float64)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播

        Args:
            x: (batch, seq_len, input_size)

        Returns:
            (batch, 1) 预测值
        """
        # LSTM输出
        lstm_out, _ = self.lstm(x)
        # 取最后一个时间步的输出
        last_out = lstm_out[:, -1, :]
        # 全连接映射到1维
        pred = self.fc(last_out)
        return pred

    def count_parameters(self) -> int:
        """统计可训练参数数量"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
