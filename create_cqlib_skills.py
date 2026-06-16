#!/usr/bin/env python3
"""Create all cqlib skill SKILL.md files"""
import os

SKILLS_DIR = os.path.expanduser("~/.evoscientist/skills")

SKILLS = {}

# ===================== cqlib-qaoa =====================
SKILLS["cqlib-qaoa"] = """---
name: cqlib-qaoa
description: "Implement QAOA (Quantum Approximate Optimization Algorithm) using cqlib SDK. Use when: solving combinatorial optimization problems (MaxCut, TSP, Unit Commitment, portfolio optimization), encoding QUBO/Ising models as quantum circuits, building QAOA ansatz with alternating mixing and cost unitaries, running variational optimization loops with cqlib StatevectorSimulator, or submitting QAOA circuits to TianYan quantum cloud. Triggers on keywords: QAOA, 量子优化, 组合优化, QUBO, Ising, MaxCut, 机组组合, 投资组合, 变分优化, cost Hamiltonian, mixer Hamiltonian."
---

# cqlib-qaoa — QAOA 量子近似优化算法

使用 cqlib SDK 实现 QAOA，求解组合优化问题。

**前置 skill**：`cqlib-sdk`（Circuit、Parameter、StatevectorSimulator 基础用法）

## 执行流程

1. 将业务问题建模为 QUBO/Ising 模型
2. 构造代价哈密顿量 H_C，编码为量子门
3. 构建 QAOA ansatz（p 层交替 H_C 和 H_M）
4. 用经典优化器（scipy）最小化期望值
5. 从最优参数采样，搜索最优可行解
6. 验证结果 vs 暴力搜索

---

## 一、QUBO/Ising 建模

QUBO 形式：`min x^T Q x`，x ∈ {0,1}^n

Ising 形式：`min Σ J_ij z_i z_j + Σ h_i z_i`，z ∈ {-1,+1}

转换：`z_i = 1 - 2x_i`

### QUBO → Ising 转换规则

```
x_i x_j → (1-z_i)(1-z_j)/4 = (1 - z_i - z_j + z_i z_j)/4
x_i     → (1-z_i)/2
常数    → 常数
```

---

## 二、代价哈密顿量编码

H_C 中的 Z_i Z_j 项用 CNOT-RZ-CNOT 分解（cqlib 无原生 RZZ 门）：

```python
def add_zz_interaction(circuit, q_i, q_j, coefficient, gamma):
    """添加 ZZ 相互作用: exp(-i * coefficient * gamma * Z_i Z_j)"""
    angle = 2 * coefficient * gamma
    circuit.cx(q_i, q_j)
    circuit.rz(q_j, angle)
    circuit.cx(q_i, q_j)

def add_z_term(circuit, q_i, coefficient, gamma):
    """添加 Z 项: exp(-i * coefficient * gamma * Z_i)"""
    angle = 2 * coefficient * gamma
    circuit.rz(q_i, angle)
```

---

## 三、完整 QAOA Ansatz 构建

```python
from cqlib import Circuit, Parameter
import numpy as np

def build_qaoa_circuit(n_qubits, qubo_matrix, p=1):
    param_names = []
    for layer in range(p):
        param_names.extend([f'gamma_{layer}', f'beta_{layer}'])

    circuit = Circuit(n_qubits, parameters=param_names)

    # 初始叠加态
    for i in range(n_qubits):
        circuit.h(i)

    for layer in range(p):
        gamma = Parameter(f'gamma_{layer}')
        beta = Parameter(f'beta_{layer}')

        # 代价层：编码 QUBO
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                if qubo_matrix[i][j] != 0:
                    add_zz_interaction(circuit, i, j, qubo_matrix[i][j], gamma)
            if qubo_matrix[i][i] != 0:
                add_z_term(circuit, i, qubo_matrix[i][i], gamma)

        # 混合层：X 旋转
        for i in range(n_qubits):
            circuit.rx(i, 2 * beta)

    circuit.measure_all()
    return circuit, param_names
```

---

## 四、期望值计算

```python
from cqlib import StatevectorSimulator

def compute_expectation(params, circuit, param_names, n_qubits, qubo_matrix):
    param_dict = dict(zip(param_names, params))
    bound_circuit = circuit.assign_parameters(param_dict)
    sim = StatevectorSimulator(circuit=bound_circuit)
    probs = sim.measure()

    expectation = 0.0
    for bitstring, prob in probs.items():
        if prob < 1e-12:
            continue
        x = np.array([1 - 2 * int(bitstring[-1 - i]) for i in range(n_qubits)])
        cost = sum(qubo_matrix[i][j] * (1-x[i])/2 * (1-x[j])/2
                   for i in range(n_qubits) for j in range(n_qubits))
        expectation += prob * cost
    return expectation
```

---

## 五、经典优化循环

```python
from scipy.optimize import minimize

def run_qaoa(n_qubits, qubo_matrix, p=1, num_restarts=10):
    circuit, param_names = build_qaoa_circuit(n_qubits, qubo_matrix, p)
    best_result, best_cost = None, float('inf')
    for _ in range(num_restarts):
        x0 = np.random.uniform(0, np.pi, len(param_names))
        result = minimize(compute_expectation, x0=x0,
            args=(circuit, param_names, n_qubits, qubo_matrix),
            method='COBYLA', options={'maxiter': 500})
        if result.fun < best_cost:
            best_cost, best_result = result.fun, result
    return best_result, circuit, param_names
```

---

## 六、后处理：搜索最优可行解

**关键洞察**：最高概率解 ≠ 最优可行解，必须搜索 top-k。

```python
def find_best_feasible(circuit, param_names, opt_params, n_qubits,
                       qubo_matrix, is_feasible_fn=None, top_k=20):
    param_dict = dict(zip(param_names, opt_params))
    bound_circuit = circuit.assign_parameters(param_dict)
    sim = StatevectorSimulator(circuit=bound_circuit)
    probs = sim.measure()
    sorted_probs = sorted(probs.items(), key=lambda x: -x[1])

    best_solution, best_cost = None, float('inf')
    for bitstring, prob in sorted_probs[:top_k]:
        x = [(1 - int(bitstring[-1-i])) // 2 for i in range(n_qubits)]
        if is_feasible_fn and not is_feasible_fn(x):
            continue
        cost = sum(qubo_matrix[i][j] * x[i] * x[j]
                   for i in range(n_qubits) for j in range(n_qubits))
        if cost < best_cost:
            best_cost, best_solution = cost, x
    return best_solution, best_cost
```

---

## 七、QUBO 编码质量 — 决定性因素

QAOA 成功的关键不是算法参数，而是 QUBO 编码质量。

### 常见陷阱：惩罚项的负系数问题

当约束形如 `(Σ x_i - D)²` 展开为 QUBO 时，产生 `-2λD·x_i` 负线性项。λ 过大让全局最优不可行。

### 解决方案：自适应惩罚权重 + 矩阵归一化

```python
def adaptive_penalty(qubo_matrix, constraint_matrix):
    """自适应 λ + 归一化到 [-1,1]"""
    best_lam = None
    for lam in np.arange(1, 200, 0.5):
        total = qubo_matrix + lam * constraint_matrix
        max_abs = max(abs(total.max()), abs(total.min()), 1e-8)
        normalized = total / max_abs
        # 验证归一化后 QUBO 全局最优是否为可行解...
    return best_lam
```

---

## 关键注意事项

1. **ZZ 门分解**：cqlib 无 RZZ，必须用 CNOT-RZ-CNOT
2. **参数必须创建时声明**：不能事后添加
3. **assign_parameters 返回新电路**：需要接收返回值
4. **测量结果反序**：bitstring 最右 = Q0
5. **最高概率 ≠ 最优可行**：必须 top-k 搜索
6. **QUBO 编码质量是决定性因素**：自适应 λ + 归一化
7. **多层(p>1)提升精度**但增加参数，需更多重启
8. **约束惩罚权重的平衡**：过大造成崎岖景观，过小约束不满足
"""

# ===================== cqlib-vqe =====================
SKILLS["cqlib-vqe"] = """---
name: cqlib-vqe
description: "Implement VQE (Variational Quantum Eigensolver) using cqlib SDK. Use when: computing molecular ground state energy, solving eigenvalue problems with variational quantum circuits, building chemically-inspired ansatz (UCCSD, hardware-efficient), measuring Hamiltonian expectation values with Pauli grouping, or running VQE optimization loops with cqlib StatevectorSimulator. Triggers on keywords: VQE, 变分量子特征求解, 基态能量, 分子能量, UCCSD, Hartree-Fock, Hamiltonian expectation, Pauli measurements, eigenvalue."
---

# cqlib-vqe — 变分量子特征求解器

使用 cqlib SDK 实现 VQE，计算哈密顿量基态能量。

**前置 skill**：`cqlib-sdk`

## 执行流程

1. 定义目标哈密顿量 H（分子/Ising/自定义）
2. 选择变分 ansatz（Hardware-Efficient / UCCSD / 自定义）
3. 构建参数化量子电路
4. 实现期望值计算（Pauli 分组测量）
5. 经典优化器最小化能量
6. 收敛分析 + 结果验证

---

## 一、哈密顿量表示

```python
# H = Σ c_i * P_i, P_i 为 Pauli 串
# pauli_string 格式: "Z0Z1", "X0", "Y1Z2"
hamiltonian = [
    (-1.052, 'Z0Z1'),
    (0.397, 'Z0'),
    (-0.398, 'Z1'),
    (0.011, 'X0X1'),
    (0.011, 'Y0Y1'),
]
```

---

## 二、Ansatz 构建

### Hardware-Efficient Ansatz

```python
from cqlib import Circuit, Parameter

def hardware_efficient_ansatz(n_qubits, n_layers=2):
    param_names = []
    for layer in range(n_layers):
        for q in range(n_qubits):
            param_names.extend([f'ry_{layer}_{q}', f'rz_{layer}_{q}'])

    circuit = Circuit(n_qubits, parameters=param_names)

    for layer in range(n_layers):
        for q in range(n_qubits):
            circuit.ry(q, Parameter(f'ry_{layer}_{q}'))
            circuit.rz(q, Parameter(f'rz_{layer}_{q}'))
        for q in range(n_qubits):
            circuit.cx(q, (q + 1) % n_qubits)
        circuit.barrier_all()

    return circuit, param_names
```

### UCCSD-Inspired Ansatz（化学应用）

```python
def uccsd_ansatz(n_qubits, n_electrons):
    param_names = []
    for i in range(n_electrons):
        for a in range(n_electrons, n_qubits):
            param_names.append(f't1_{i}_{a}')

    circuit = Circuit(n_qubits, parameters=param_names)

    # Hartree-Fock 初态
    for i in range(n_electrons):
        circuit.x(i)
    circuit.barrier_all()

    # 简化单激发: Givens 旋转
    for i in range(n_electrons):
        for a in range(n_electrons, n_qubits):
            t1 = Parameter(f't1_{i}_{a}')
            circuit.cx(i, a)
            circuit.ry(a, t1)
            circuit.cx(i, a)

    return circuit, param_names
```

---

## 三、Pauli 测量

### 单个 Pauli 串期望值

```python
import numpy as np
from cqlib import StatevectorSimulator

def pauli_expectation(circuit, pauli_string, n_qubits):
    meas_circuit = circuit.copy()
    for qubit_idx, pauli_op in pauli_string:
        if pauli_op == 'X':
            meas_circuit.h(qubit_idx)
        elif pauli_op == 'Y':
            meas_circuit.rx(qubit_idx, np.pi / 2)

    meas_circuit.measure_all()
    sim = StatevectorSimulator(circuit=meas_circuit)
    probs = sim.measure()

    expectation = 0.0
    for bitstring, prob in probs.items():
        parity = sum(int(bitstring[-1-q]) for q, _ in pauli_string)
        expectation += (-1)**parity * prob
    return expectation
```

### Pauli 分组（减少测量次数）

```python
def group_paulis(hamiltonian):
    """将可同时测量的 Pauli 串分组"""
    groups = []
    for coeff, pauli_str in hamiltonian:
        placed = False
        for group in groups:
            if is_qwc(group, pauli_str):
                group.append((coeff, pauli_str))
                placed = True
                break
        if not placed:
            groups.append([(coeff, pauli_str)])
    return groups

def is_qwc(group, new_pauli):
    """检查是否 qubit-wise commuting"""
    new_terms = parse_pauli(new_pauli)
    for _, existing in group:
        existing_terms = parse_pauli(existing)
        for q1, p1 in new_terms:
            for q2, p2 in existing_terms:
                if q1 == q2 and p1 != p2:
                    return False
    return True

def parse_pauli(s):
    import re
    return [(int(m.group(2)), m.group(1)) for m in re.finditer(r'([XYZ])(\d+)', s)]
```

### 完整期望值

```python
def hamiltonian_expectation(params, circuit, param_names, hamiltonian, n_qubits):
    param_dict = dict(zip(param_names, params))
    bound_circuit = circuit.assign_parameters(param_dict)
    total = 0.0
    for coeff, pauli_str in hamiltonian:
        terms = parse_pauli(pauli_str)
        exp_val = pauli_expectation(bound_circuit, terms, n_qubits)
        total += coeff * exp_val
    return total
```

---

## 四、优化循环

```python
from scipy.optimize import minimize

def run_vqe(circuit, param_names, hamiltonian, n_qubits, num_restarts=5):
    best_result, best_energy = None, float('inf')
    for _ in range(num_restarts):
        x0 = np.random.uniform(-np.pi, np.pi, len(param_names))
        result = minimize(hamiltonian_expectation, x0=x0,
            args=(circuit, param_names, hamiltonian, n_qubits),
            method='COBYLA', options={'maxiter': 1000})
        if result.fun < best_energy:
            best_energy, best_result = result.fun, result
    return best_result
```

---

## 五、分子哈密顿量示例 (H2)

```python
h2_hamiltonian = [
    (-1.052, 'Z0Z1'),
    (0.397, 'Z0'),
    (-0.398, 'Z1'),
    (0.011, 'X0X1'),
    (0.011, 'Y0Y1'),
]
# 精确基态能量 ≈ -1.137 Hartree
```

---

## 关键注意事项

1. **Pauli 测量需要基变换**: X 前加 H, Y 前加 Rx(π/2)
2. **Pauli 分组减少电路执行次数**: 对易的串可同时测量
3. **UCCSD 参数数量随系统规模急剧增长**: 小系统用完整 UCCSD, 大系统用启发式
4. **Hartree-Fock 初态**: 化学应用中用 X 门制备参考态
5. **测量结果反序**: bitstring 最右 = Q0
6. **assign_parameters 返回新电路**: 每次需接收返回值
7. **数值梯度替代解析梯度**: cqlib 无原生参数移位法则
8. **收敛判断**: 能量变化 < 1e-6 Ha 可视为收敛
"""

# ===================== cqlib-qml =====================
SKILLS["cqlib-qml"] = """---
name: cqlib-qml
description: "Implement Quantum Machine Learning (QML) using cqlib SDK. Use when: building variational quantum classifiers (VQC), quantum regression models, quantum probability layers, encoding classical data into quantum states (angle encoding), training quantum-classical hybrid models with PyTorch + cqlib, or implementing quantum neural networks for classification/regression tasks. Triggers on keywords: QML, 量子机器学习, VQC, 变分量子分类器, 量子分类, 量子回归, quantum classifier, quantum neural network, quantum layer, angle encoding."
---

# cqlib-qml — 量子机器学习

使用 cqlib SDK 实现量子分类器和回归模型。

**前置 skill**：`cqlib-sdk`

## 执行流程

1. 选择数据编码策略（角度编码）
2. 构建变分量子电路（编码层 + 变分层 + 测量）
3. 定义量子概率层（与 PyTorch 集成）
4. 训练混合量子-经典模型
5. 评估与验证

---

## 一、数据编码

### RY+RZ 编码（推荐，表达能力更强）

```python
from cqlib import Circuit, Parameter

def angle_encoding_circuit(n_qubits, n_features):
    enc_params = []
    for i in range(n_features):
        enc_params.extend([f'enc_ry_{i}', f'enc_rz_{i}'])

    circuit = Circuit(n_qubits, parameters=enc_params)
    for i in range(min(n_qubits, n_features)):
        circuit.ry(i, Parameter(f'enc_ry_{i}'))
        circuit.rz(i, Parameter(f'enc_rz_{i}'))
    return circuit, enc_params
```

### RX 编码（更简单）

```python
def rx_encoding_circuit(n_qubits, n_features):
    enc_params = [f'enc_{i}' for i in range(n_features)]
    circuit = Circuit(n_qubits, parameters=enc_params)
    for i in range(min(n_qubits, n_features)):
        circuit.rx(i, Parameter(f'enc_{i}'))
    return circuit, enc_params
```

---

## 二、完整 VQC 电路

```python
def build_vqc_circuit(n_qubits, n_features, n_var_layers=2):
    enc_params, var_params = [], []
    for i in range(n_features):
        enc_params.extend([f'enc_ry_{i}', f'enc_rz_{i}'])
    for layer in range(n_var_layers):
        for q in range(n_qubits):
            var_params.extend([f'var_ry_{layer}_{q}', f'var_rz_{layer}_{q}'])

    circuit = Circuit(n_qubits, parameters=enc_params + var_params)

    # 编码层
    for i in range(min(n_qubits, n_features)):
        circuit.ry(i, Parameter(f'enc_ry_{i}'))
        circuit.rz(i, Parameter(f'enc_rz_{i}'))

    # 变分层
    for layer in range(n_var_layers):
        for q in range(n_qubits):
            circuit.ry(q, Parameter(f'var_ry_{layer}_{q}'))
            circuit.rz(q, Parameter(f'var_rz_{layer}_{q}'))
        for q in range(n_qubits):
            circuit.cx(q, (q + 1) % n_qubits)

    circuit.measure_all()
    return circuit, enc_params, var_params
```

---

## 三、量子概率层 — PyTorch 集成

```python
import torch
import torch.nn as nn
import numpy as np
from cqlib import Circuit, Parameter, StatevectorSimulator

class QuantumProbLayer(nn.Module):
    """量子概率层: 经典特征 → 2^n_qubits 概率分布"""
    def __init__(self, n_qubits, n_features, n_var_layers=2):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_features = n_features
        self.circuit, self.enc_params, self.var_params = \\
            build_vqc_circuit(n_qubits, n_features, n_var_layers)
        self.all_params = self.enc_params + self.var_params
        self.var_weights = nn.Parameter(torch.randn(len(self.var_params)) * 0.1)
        self.input_scale = nn.Parameter(torch.ones(n_features))

    def forward(self, x):
        batch_probs = []
        for sample in x:
            scaled = torch.tanh(sample * self.input_scale) * np.pi
            param_dict = {}
            for i in range(min(self.n_qubits, self.n_features)):
                idx = i * 2
                if idx < len(self.enc_params):
                    param_dict[self.enc_params[idx]] = scaled[i].item()
                if idx + 1 < len(self.enc_params):
                    param_dict[self.enc_params[idx + 1]] = scaled[i].item() * 0.5
            for j, p_name in enumerate(self.var_params):
                param_dict[p_name] = self.var_weights[j].item()

            bound_circuit = self.circuit.assign_parameters(param_dict)
            sim = StatevectorSimulator(circuit=bound_circuit)
            probs = sim.measure()

            n_states = 2 ** self.n_qubits
            prob_vec = torch.zeros(n_states)
            for bitstring, prob in probs.items():
                prob_vec[int(bitstring, 2)] = prob
            batch_probs.append(prob_vec)
        return torch.stack(batch_probs)
```

---

## 四、分类与回归模型

```python
class QuantumClassifier(nn.Module):
    def __init__(self, n_qubits, n_features, n_classes, n_var_layers=2):
        super().__init__()
        self.quantum_layer = QuantumProbLayer(n_qubits, n_features, n_var_layers)
        self.classifier = nn.Linear(2 ** n_qubits, n_classes)

    def forward(self, x):
        return self.classifier(self.quantum_layer(x))

class QuantumRegressor(nn.Module):
    def __init__(self, n_qubits, n_features, n_var_layers=2):
        super().__init__()
        self.quantum_layer = QuantumProbLayer(n_qubits, n_features, n_var_layers)
        self.regressor = nn.Sequential(
            nn.Linear(2 ** n_qubits, 64), nn.ReLU(), nn.Linear(64, 1))

    def forward(self, x):
        return self.regressor(self.quantum_layer(x)).squeeze(-1)
```

---

## 五、时间序列回归（高级）

```python
class QuantumTimeSeriesModel(nn.Module):
    """GRU编码器 + 量子概率层 + 回归头"""
    def __init__(self, input_dim, hidden_dim, n_qubits, n_var_layers=2):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, batch_first=True)
        self.projector = nn.Linear(hidden_dim, n_qubits)
        self.quantum_layer = QuantumProbLayer(n_qubits, n_qubits, n_var_layers)
        self.regressor = nn.Sequential(
            nn.Linear(2 ** n_qubits, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, x):
        _, h_n = self.gru(x)
        features = self.projector(h_n.squeeze(0))
        probs = self.quantum_layer(features)
        return self.regressor(probs).squeeze(-1)
```

---

## 关键注意事项

1. **参数必须创建时声明**: 编码参数和变分参数都要预先声明
2. **assign_parameters 返回新电路**: 每次前向传播需接收返回值
3. **tanh 输入缩放**: 将经典数据映射到 [-pi, pi], 防止梯度消失
4. **量子层计算开销大**: 每个样本需独立模拟
5. **n_qubits 限制**: StatevectorSimulator 内存 2^n, n>20 不可行
6. **概率输出 vs 期望输出**: 概率层 2^n 维; Z 期望值 n 维
7. **测量结果反序**: bitstring 最右 = Q0
8. **梯度传播**: PyTorch autograd 不穿过 cqlib 模拟, 用有限差分
"""

# ===================== cqlib-hybrid =====================
SKILLS["cqlib-hybrid"] = """---
name: cqlib-hybrid
description: "Implement hybrid quantum-classical algorithms using cqlib SDK with PyTorch. Use when: building HQNN (Hybrid Quantum Neural Networks), combining CNN/RNN/Transformer feature extractors with quantum layers, creating parallel quantum circuits for multi-channel processing, integrating quantum probability layers into deep learning pipelines, or designing hybrid architectures for image classification, NLP, or time-series. Triggers on keywords: hybrid quantum-classical, HQNN, 混合量子经典, 量子神经网络, quantum-classical hybrid, parallel quantum layer, CNN+quantum, RNN+quantum, quantum deep learning."
---

# cqlib-hybrid — 混合量子经典算法

使用 cqlib SDK + PyTorch 构建混合量子-经典神经网络。

**前置 skill**：`cqlib-sdk`（基础）、`cqlib-qml`（量子概率层）

## 执行流程

1. 选择经典特征提取器（CNN/RNN/MLP）
2. 设计量子层架构（单路/并行/级联）
3. 实现量子层与 PyTorch 的接口
4. 构建端到端混合模型
5. 训练、评估、调优

---

## 一、架构模式

### 模式 A: 串行混合 (Serial)
经典网络 → 降维 → 量子层 → 经典头

### 模式 B: 并行混合 (Parallel/HQNN-Parallel)
经典特征 → 多个并行量子通道 → 拼接 → 经典头

### 模式 C: 级联混合 (Cascaded)
量子层输出作为下一个经典层输入，交替堆叠

---

## 二、量子层封装（输出 Z 期望值）

```python
import torch
import torch.nn as nn
import numpy as np
from cqlib import Circuit, Parameter, StatevectorSimulator

class HybridQuantumLayer(nn.Module):
    """混合量子层: 经典输入 → 量子电路 → Z期望值输出"""
    def __init__(self, n_qubits, n_features, n_layers=3):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_features = n_features
        self.circuit, self.all_param_names = self._build_circuit(n_layers)
        n_var_params = len(self.all_param_names) - n_features
        self.var_weights = nn.Parameter(torch.randn(n_var_params) * 0.1)
        self.input_scale = nn.Parameter(torch.ones(n_features))

    def _build_circuit(self, n_layers):
        param_names = [f'enc_{i}' for i in range(self.n_features)]
        var_names = []
        for layer in range(n_layers):
            for q in range(self.n_qubits):
                var_names.extend([f'ry_{layer}_{q}', f'rz_{layer}_{q}'])
        param_names.extend(var_names)

        circuit = Circuit(self.n_qubits, parameters=param_names)
        for i in range(min(self.n_qubits, self.n_features)):
            circuit.rx(i, Parameter(f'enc_{i}'))
        for layer in range(n_layers):
            for q in range(self.n_qubits):
                circuit.ry(q, Parameter(f'ry_{layer}_{q}'))
                circuit.rz(q, Parameter(f'rz_{layer}_{q}'))
            for q in range(self.n_qubits):
                circuit.cx(q, (q + 1) % self.n_qubits)
        circuit.measure_all()
        return circuit, param_names

    def forward(self, x):
        outputs = []
        for sample in x:
            scaled = torch.tanh(sample * self.input_scale) * np.pi
            param_dict = {}
            for i in range(min(self.n_qubits, self.n_features)):
                param_dict[f'enc_{i}'] = scaled[i].item()
            var_idx = 0
            for name in self.all_param_names:
                if name.startswith('ry_') or name.startswith('rz_'):
                    param_dict[name] = self.var_weights[var_idx].item()
                    var_idx += 1

            bound_circuit = self.circuit.assign_parameters(param_dict)
            sim = StatevectorSimulator(circuit=bound_circuit)
            probs = sim.measure()

            expectations = []
            for q in range(self.n_qubits):
                exp_z = sum((1 - 2*int(bitstring[-1-q])) * prob
                           for bitstring, prob in probs.items())
                expectations.append(exp_z)
            outputs.append(torch.tensor(expectations, dtype=torch.float32))
        return torch.stack(outputs)
```

---

## 三、HQNN-Parallel 架构（图像分类）

```python
class HQNNParallel(nn.Module):
    """CNN特征提取 → 4个并行量子层 → 分类"""
    def __init__(self, n_classes, n_qubits=5, n_qlayers=3, n_quantum_channels=4):
        super().__init__()
        self.n_quantum_channels = n_quantum_channels
        self.n_qubits = n_qubits

        self.feature_extractor = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten())

        self.projectors = nn.ModuleList([
            nn.Linear(128, n_qubits) for _ in range(n_quantum_channels)])
        self.quantum_layers = nn.ModuleList([
            HybridQuantumLayer(n_qubits, n_qubits, n_qlayers)
            for _ in range(n_quantum_channels)])

        self.classifier = nn.Sequential(
            nn.Linear(n_qubits * n_quantum_channels, 64),
            nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, n_classes))

    def forward(self, x):
        features = self.feature_extractor(x)
        quantum_outputs = []
        for i in range(self.n_quantum_channels):
            projected = self.projectors[i](features)
            q_out = self.quantum_layers[i](projected)
            quantum_outputs.append(q_out)
        combined = torch.cat(quantum_outputs, dim=1)
        return self.classifier(combined)
```

---

## 四、训练策略

### 量子层感知学习率

```python
def create_optimizer(model, classical_lr=1e-3, quantum_lr=1e-2):
    classical_params, quantum_params = [], []
    for name, param in model.named_parameters():
        if 'quantum' in name or 'var_weights' in name or 'input_scale' in name:
            quantum_params.append(param)
        else:
            classical_params.append(param)
    return torch.optim.Adam([
        {'params': classical_params, 'lr': classical_lr},
        {'params': quantum_params, 'lr': quantum_lr}])
```

### 梯度裁剪

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

### 训练加速

1. **减少量子比特数**: n_qubits <= 10
2. **减少变分层**: n_layers = 2-3 通常足够
3. **子采样训练**: 每 epoch 只用部分数据
4. **预训练经典部分**: 冻结量子层先训练经典部分

---

## 五、提交到天衍云

```python
from cqlib import TianYanPlatform

def deploy_quantum_layer_to_cloud(circuit, opt_params, param_names, login_key):
    param_dict = dict(zip(param_names, opt_params))
    bound_circuit = circuit.assign_parameters(param_dict)
    platform = TianYanPlatform(login_key=login_key, machine_name="simulator")
    query_ids = platform.submit_experiment(circuit=bound_circuit.qcis, num_shots=10000)
    return platform.query_experiment(query_ids)
```

---

## 关键注意事项

1. **量子层是计算瓶颈**: 每个样本独立模拟, batch 大时极慢
2. **并行量子通道增加表达力**但线性增加计算时间
3. **Z 期望值 vs 概率输出**: 期望值 n_qubits 维, 概率 2^n 维
4. **tanh 缩放防止梯度爆炸**: 经典→量子接口必须有缩放
5. **量子层学习率通常更大**: 10x 经典层学习率
6. **n_qubits <= 10**: >15 比特模拟器内存不足
7. **测量反序**: Z 期望值计算时 bitstring[-1-q] 对应 qubit q
8. **字典绑定更安全**: 并行通道各自独立参数
"""

# Write all files
for skill_name, content in SKILLS.items():
    path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    with open(path, "w") as f:
        f.write(content)
    size = os.path.getsize(path)
    print(f"Written {skill_name}/SKILL.md: {size} bytes")

# Also ensure cqlib-sdk SKILL.md is correct
sdk_path = os.path.join(SKILLS_DIR, "cqlib-sdk", "SKILL.md")
if os.path.exists(sdk_path):
    size = os.path.getsize(sdk_path)
    print(f"cqlib-sdk/SKILL.md exists: {size} bytes")
else:
    print("cqlib-sdk/SKILL.md MISSING!")

# Also write references for cqlib-sdk
refs_dir = os.path.join(SKILLS_DIR, "cqlib-sdk", "references")
os.makedirs(refs_dir, exist_ok=True)

circuit_api = open(os.path.join(os.path.dirname(__file__) if "__file__" in dir() else ".", "circuit_api_placeholder.md"), "w") if False else None

# Circuit API reference
circuit_ref = """# Circuit 完整 API 参考

## 构造函数
Circuit(qubits: int | Qubit | list[Qubit|int], parameters: list[Parameter|str] | None = None)

## 属性
- qubits: list[Qubit]
- num_qubits: int
- parameters: list[Parameter]
- parameters_value: dict[Parameter, float|int]
- circuit_data / instruction_sequence: list[InstructionData]
- qcis: str (QCIS导出)

## 单比特门: h, x, y, z, s, sd, t, td, x2p, x2m, y2p, y2m
## 参数化门: rx, ry, rz, rxy, xy, u
## 双比特门: cx/cnot, cy, cz, crx, cry, crz, swap
## 三比特门: ccx
## 测量: measure, measure_all
## 屏障: barrier, barrier_all
## 绑定: assign_parameters(values, inplace=False, **kwargs) -> Circuit
## 组合: c1 + c2, c1 += c2
## 导出: .qcis, .to_qasm2(), .as_str(), .draw()
## 加载: Circuit.load(qcis_str)
"""

with open(os.path.join(refs_dir, "circuit-api.md"), "w") as f:
    f.write(circuit_ref)
print("Written cqlib-sdk/references/circuit-api.md")

simulator_ref = """# StatevectorSimulator API

## 构造函数
StatevectorSimulator(circuit, is_fusion=False, fusion_max_qubit=5, omp_threads=0, fusion_th=15)

## 方法
- statevector() -> dict[str, complex]
- probs() -> dict[str, float]
- measure() -> dict[str, float] (需先 measure_all)
- sample(shots=1024, ...) -> dict[str, int]

## 关键: 测量结果反序, bitstring最右=Q0
"""

with open(os.path.join(refs_dir, "simulator-api.md"), "w") as f:
    f.write(simulator_ref)
print("Written cqlib-sdk/references/simulator-api.md")

platform_ref = """# TianYanPlatform API

## 初始化
TianYanPlatform(login_key, auto_login=True, machine_name=None)

## 核心方法
- submit_experiment(circuit, num_shots=12000, ...) -> query_ids
- query_experiment(query_id, max_wait_time=3600, readout_calibration=False) -> results
- create_lab(name) -> lab_id
- save_experiment(lab_id, circuit) -> exp_id
- run_experiment(exp_id, num_shots=12000) -> query_id
- query_quantum_computer_list() -> machines

## 噪声模型
noise=[{"noise_type": "bit-flip|phase-flip|depolarizing|decoherence", "params": [...]}]

## 模拟器: simulator(136bit), simulator_8, simulator_12, simulator_24
"""

with open(os.path.join(refs_dir, "platform-api.md"), "w") as f:
    f.write(platform_ref)
print("Written cqlib-sdk/references/platform-api.md")

print("\nAll skill files written successfully!")
