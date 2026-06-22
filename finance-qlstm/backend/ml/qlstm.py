"""
QLSTM（量子长短期记忆网络）
- 用VQC（变分量子线路）替换LSTM的4个门
- VQCBlock: 输入编码 → 变分拟设 → Z期望测量
- QLSTMCell: 遗忘门、输入门、候选门、输出门各用一个VQC
- QLSTM: 堆叠QLSTMCell + FC预测头

关键注意事项：
1. cqlib参数必须在Circuit创建时声明
2. cqlib比特串顺序：bits[qubit]，不是bits[-1-qubit]
3. VQC逐样本前向传播（因量子模拟器不支持batch）
4. 使用torch.float64保证数值稳定性
"""

import torch
import torch.nn as nn
from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator


class VQCBlock(nn.Module):
    """变分量子线路模块

    替换LSTM中每个门的线性变换：
    1. 线性投影：n_input → n_qubits（将输入编码到量子比特数）
    2. RY编码门：将经典数据编码到量子态
    3. RY+RZ变分层 + CNOT环形纠缠
    4. Z期望测量：每个量子比特 → n_qubits个输出
    5. 线性投影：n_qubits → n_output

    Args:
        n_qubits: 量子比特数（默认4）
        n_input: 输入特征维度
        n_output: 输出维度（与hidden_size相同）
        layers: 变分层层数
    """

    def __init__(self, n_qubits: int, n_input: int, n_output: int, layers: int = 2):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_input = n_input
        self.n_output = n_output
        self.layers = layers

        # 经典→量子：输入投影
        self.input_proj = nn.Linear(n_input, n_qubits, dtype=torch.float64)

        # 量子→经典：输出投影
        self.output_proj = nn.Linear(n_qubits, n_output, dtype=torch.float64)

        # 变分参数（可训练）
        n_var_params = layers * n_qubits * 2  # 每层每个qubit有ry和rz两个参数
        self.var_params = nn.Parameter(
            torch.randn(n_var_params, dtype=torch.float64) * 0.1
        )

        # 构建量子线路模板（参数符号化）
        self._build_circuit()

    def _build_circuit(self):
        """构建量子线路模板，参数在运行时绑定"""
        n_qubits = self.n_qubits
        layers = self.layers

        # 编码参数
        self.enc_params = [Parameter(f"enc_{i}") for i in range(n_qubits)]

        # 变分参数
        self.var_param_names = []
        for layer in range(layers):
            for q in range(n_qubits):
                self.var_param_names.append(Parameter(f"theta_{layer}_{q}_ry"))
                self.var_param_names.append(Parameter(f"theta_{layer}_{q}_rz"))

        # 所有参数在Circuit创建时声明（cqlib要求）
        all_params = self.enc_params + self.var_param_names
        self.circuit = Circuit(n_qubits, parameters=all_params)

        # 编码层：RY门
        for i in range(n_qubits):
            self.circuit.ry(i, self.enc_params[i])

        # 变分层：RY+RZ + CNOT环形纠缠
        idx = 0
        for layer in range(layers):
            for q in range(n_qubits):
                self.circuit.ry(q, self.var_param_names[idx])
                idx += 1
                self.circuit.rz(q, self.var_param_names[idx])
                idx += 1
            # CNOT环形纠缠
            for q in range(n_qubits - 1):
                self.circuit.cx(q, q + 1)
            if n_qubits > 1:
                self.circuit.cx(n_qubits - 1, 0)

        # 测量所有量子比特
        self.circuit.measure_all()

    def _run_circuit(self, enc_values: torch.Tensor) -> torch.Tensor:
        """运行量子线路，计算Z期望值

        Args:
            enc_values: 编码参数值 (n_qubits,)

        Returns:
            Z期望值张量 (n_qubits,)
        """
        n_qubits = self.n_qubits
        var_values = self.var_params.data

        # 绑定参数值
        params = {}
        for i, p in enumerate(self.enc_params):
            params[p] = float(enc_values[i].detach().cpu())
        for i, p in enumerate(self.var_param_names):
            params[p] = float(var_values[i].detach().cpu())

        # 参数绑定并运行模拟
        bound = self.circuit.assign_parameters(params)
        probs = StatevectorSimulator(circuit=bound).measure()

        # 计算Z期望值
        # 关键：cqlib比特串顺序 bits[qubit]，不是bits[-1-qubit]
        expectations = []
        for q in range(n_qubits):
            exp = sum(
                (1 - 2 * int(bits[q])) * float(prob)
                for bits, prob in probs.items()
            )
            expectations.append(exp)

        return torch.tensor(expectations, dtype=torch.float64)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播（逐样本处理）

        Args:
            x: (batch, n_input) 或 (n_input,)

        Returns:
            (batch, n_output) 或 (n_output,)
        """
        # 保存原始形状
        original_dim = x.dim()
        if original_dim == 1:
            x = x.unsqueeze(0)  # (1, n_input)

        batch_size = x.shape[0]
        results = []

        for b in range(batch_size):
            # 输入投影
            encoded = self.input_proj(x[b])  # (n_qubits,)
            # 运行量子线路
            expectations = self._run_circuit(encoded)  # (n_qubits,)
            # 输出投影
            output = self.output_proj(expectations)  # (n_output,)
            results.append(output)

        result = torch.stack(results)  # (batch, n_output)

        if original_dim == 1:
            result = result.squeeze(0)  # (n_output,)

        return result


class QLSTMCell(nn.Module):
    """量子LSTM单元

    用4个VQC替换LSTM的4个门：
    - 遗忘门 (forget gate)
    - 输入门 (input gate)
    - 候选记忆 (cell candidate)
    - 输出门 (output gate)

    每个VQC接收 concat(x, h) 作为输入

    Args:
        input_size: 输入特征维度
        hidden_size: 隐藏状态维度
        n_qubits: 量子比特数
        layers: VQC变分层层数
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        n_qubits: int = 4,
        layers: int = 2,
    ):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        combined_size = input_size + hidden_size

        # 4个VQC门
        self.vqc_forget = VQCBlock(n_qubits, combined_size, hidden_size, layers)
        self.vqc_input = VQCBlock(n_qubits, combined_size, hidden_size, layers)
        self.vqc_cell = VQCBlock(n_qubits, combined_size, hidden_size, layers)
        self.vqc_output = VQCBlock(n_qubits, combined_size, hidden_size, layers)

    def forward(
        self, x: torch.Tensor, hidden: tuple
    ) -> tuple:
        """前向传播

        Args:
            x: (batch, input_size) 当前时间步输入
            hidden: (h, c) 前一时刻隐藏状态
                h: (batch, hidden_size)
                c: (batch, hidden_size)

        Returns:
            (h_new, c_new): 新的隐藏状态
        """
        h, c = hidden

        # 拼接输入和隐藏状态
        combined = torch.cat([x, h], dim=-1)  # (batch, input_size + hidden_size)

        # 遗忘门
        f = torch.sigmoid(self.vqc_forget(combined))
        # 输入门
        i = torch.sigmoid(self.vqc_input(combined))
        # 候选记忆
        g = torch.tanh(self.vqc_cell(combined))
        # 输出门
        o = torch.sigmoid(self.vqc_output(combined))

        # 更新细胞状态和隐藏状态
        c_new = f * c + i * g
        h_new = o * torch.tanh(c_new)

        return h_new, c_new


class QLSTM(nn.Module):
    """量子长短期记忆网络

    结构：
    - 堆叠QLSTMCell层
    - FC预测头：hidden_size → 1

    Args:
        input_size: 输入特征维度
        hidden_size: 隐藏状态维度
        n_qubits: 量子比特数
        layers: VQC变分层层数
        num_layers: QLSTM堆叠层数（默认1）
    """

    def __init__(
        self,
        input_size: int = 6,
        hidden_size: int = 8,
        n_qubits: int = 4,
        layers: int = 2,
        num_layers: int = 1,
    ):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.n_qubits = n_qubits
        self.layers = layers
        self.num_layers = num_layers

        # 第一层QLSTMCell
        self.cells = nn.ModuleList()
        self.cells.append(
            QLSTMCell(input_size, hidden_size, n_qubits, layers)
        )

        # 后续层（如果num_layers > 1）
        for _ in range(1, num_layers):
            self.cells.append(
                QLSTMCell(hidden_size, hidden_size, n_qubits, layers)
            )

        # 预测头
        self.fc = nn.Linear(hidden_size, 1, dtype=torch.float64)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播

        Args:
            x: (batch, seq_len, input_size)

        Returns:
            (batch, 1) 预测值
        """
        batch_size = x.shape[0]
        seq_len = x.shape[1]

        # 初始化隐藏状态
        h = torch.zeros(batch_size, self.hidden_size, dtype=torch.float64, device=x.device)
        c = torch.zeros(batch_size, self.hidden_size, dtype=torch.float64, device=x.device)

        # 逐时间步处理
        for t in range(seq_len):
            x_t = x[:, t, :]  # (batch, input_size)

            # 逐层处理
            for layer_idx, cell in enumerate(self.cells):
                if layer_idx > 0:
                    x_t = h  # 后续层以上一层的输出为输入
                h, c = cell(x_t, (h, c))

        # 最后一个时间步的隐藏状态通过FC预测
        pred = self.fc(h)  # (batch, 1)
        return pred

    def count_parameters(self) -> int:
        """统计可训练参数数量"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
