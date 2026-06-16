---
name: cqlib-sdk
description: "Master reference for using the cqlib quantum computing SDK (中电信量子). Use when: writing quantum circuits with cqlib, building variational algorithms with Circuit/Parameter/StatevectorSimulator, submitting jobs to TianYan quantum cloud, transpiling circuits for hardware, or any quantum programming task using cqlib. Also use when choosing which cqlib sub-skill to invoke (cqlib-qaoa, cqlib-vqe, cqlib-qml, cqlib-hybrid). Triggers on keywords: cqlib, 量子电路, 量子模拟, TianYan, 天衍, 量子SDK, quantum circuit, StatevectorSimulator, Parameter, QCIS."
---

# cqlib SDK — 量子计算开发工具包

cqlib 是中电信量子集团开发的量子计算 SDK，提供量子电路构建、模拟器、云平台对接和硬件编译等能力。

## 何时使用子 Skill

本 skill 是 cqlib 的基础参考。当需要实现具体量子算法时，应使用对应子 skill：
- **组合优化问题** → `cqlib-qaoa`
- **求解分子基态能量** → `cqlib-vqe`
- **量子分类/回归** → `cqlib-qml`
- **混合量子经典架构** → `cqlib-hybrid`

---

## 核心导入

```python
from cqlib import Circuit, Parameter, Qubit, Measure, Barrier
from cqlib import TianYanPlatform, GuoDunPlatform
from cqlib import StatevectorSimulator, SimpleSimulator
from cqlib.circuits import gates
```

---

## 一、Circuit — 量子电路

详细 API 见 `references/circuit-api.md`。

### 创建电路

```python
# 方式1：指定比特数
c = Circuit(4)

# 方式2：指定比特列表
c = Circuit([0, 1, 2, 3])

# 方式3：带参数（必须在创建时声明）
from cqlib import Parameter
theta = Parameter('theta')
phi = Parameter('phi')
c = Circuit(4, parameters=[theta, phi])
```

**⚠️ 关键**：参数必须在 Circuit 创建时声明，不能事后添加已用于门的参数。

### 添加量子门

```python
# 单比特门
c.h(0)          # Hadamard
c.x(0)          # Pauli-X
c.y(0)          # Pauli-Y
c.z(0)          # Pauli-Z
c.s(0)          # S门
c.sd(0)         # S†门
c.t(0)          # T门
c.td(0)         # T†门

# 参数化单比特门
c.rx(0, theta)  # 绕X旋转
c.ry(0, theta)  # 绕Y旋转
c.rz(0, theta)  # 绕Z旋转
c.u(0, theta, phi, lam)  # 通用U3门

# 双比特门
c.cx(0, 1)      # CNOT（同 c.cnot）
c.cy(0, 1)      # Controlled-Y
c.cz(0, 1)      # Controlled-Z
c.swap(0, 1)    # SWAP

# 三比特门
c.ccx(0, 1, 2)  # Toffoli

# 测量
c.measure(0)       # 测量单个比特
c.measure([0, 1])  # 测量多个比特
c.measure_all()    # 测量所有比特

# 屏障
c.barrier(0, 1)
c.barrier_all()
```

### 参数绑定 — assign_parameters

```python
# ⚠️ 默认返回新电路，不修改原电路！
bound_circuit = c.assign_parameters({'theta': 1.57, 'phi': 0.5})

# 位置绑定（按参数声明顺序）
bound_circuit = c.assign_parameters([1.57, 0.5])

# 关键字绑定（支持部分绑定）
bound_circuit = c.assign_parameters(theta=1.57)

# 原地修改
c.assign_parameters({'theta': 1.57}, inplace=True)
```

### 电路组合与导出

```python
# 电路拼接
combined = circuit_a + circuit_b
circuit_a += circuit_b

# 导出 QCIS 字符串
qcis_str = c.qcis

# 导出 QASM2
qasm_str = c.to_qasm2()

# 从 QCIS 加载
c2 = Circuit.load(qcis_str)

# 可视化
c.draw(category='text')   # 文本
c.draw(category='mpl')    # Matplotlib
c.draw(category='latex')  # LaTeX
```

---

## 二、StatevectorSimulator — 状态向量模拟器

详细 API 见 `references/simulator-api.md`。

```python
sim = StatevectorSimulator(circuit=c)

# 获取完整状态向量
state = sim.statevector()  # dict[str, complex]

# 获取概率分布
probs = sim.probs()        # dict[str, float]

# 获取测量比特的概率分布（需要先 measure_all()）
measure_probs = sim.measure()  # dict[str, float]

# 采样
counts = sim.sample(shots=1024)  # dict[str, int]
```

**⚠️ 关键**：测量结果的比特顺序是**反序**的！
- 比特串 `'01'` 表示 Q1=0, Q0=1（最右边是最低位）
- 使用前需要 `c.measure_all()`

### 计算梯度（变分算法核心）

```python
import numpy as np
from cqlib import Circuit, Parameter, StatevectorSimulator

# 构建参数化电路
theta = Parameter('theta')
c = Circuit(1, parameters=[theta])
c.ry(0, theta)
c.measure_all()

# 计算期望值和梯度
def expectation_with_grad(params, circuit, param_names, qubit_idx=0):
    bound = circuit.assign_parameters(dict(zip(param_names, params)))
    sim = StatevectorSimulator(circuit=bound)
    probs = sim.measure()
    # 计算某个比特的 Z 期望值
    exp_val = sum((1 if bitstring[-1-qubit_idx] == '0' else -1) * p
                   for bitstring, p in probs.items())
    # 数值梯度
    grad = np.zeros(len(params))
    eps = 1e-4
    for i in range(len(params)):
        params_plus = params.copy()
        params_plus[i] += eps
        bound_p = circuit.assign_parameters(dict(zip(param_names, params_plus)))
        exp_plus = compute_exp(bound_p, qubit_idx)
        grad[i] = (exp_plus - exp_val) / eps
    return exp_val, grad
```

---

## 三、TianYanPlatform — 天衍量子云平台

详细 API 见 `references/platform-api.md`。

```python
from cqlib import TianYanPlatform

# 初始化（login_key 从天衍平台个人中心获取）
platform = TianYanPlatform(login_key="your_token", machine_name="simulator")

# 查看可用量子计算机
machines = platform.query_quantum_computer_list()

# 一键提交实验
query_ids = platform.submit_experiment(
    circuit=qcis_string,
    num_shots=10000,
    machine_name="simulator"
)

# 查询结果
results = platform.query_experiment(query_ids)

# 真机读出校准
results = platform.query_experiment(query_ids, readout_calibration=True)
```

### 可用模拟器

| 模拟器名称 | 比特数 | 说明 |
|---|---|---|
| simulator | 136 | 通用模拟器 |
| simulator_8 | 8 | 8比特模拟 |
| simulator_12 | 12 | 12比特模拟 |
| simulator_24 | 24 | 24比特模拟 |

### 噪声模型

```python
# 比特翻转
noise=[{"noise_type": "bit-flip", "params": [0.1]}]
# 相位翻转
noise=[{"noise_type": "phase-flip", "params": [0.1]}]
# 去极化
noise=[{"noise_type": "depolarizing", "params": [0.1]}]
# 退相干（op_time, T2, T1）
noise=[{"noise_type": "decoherence", "params": [0.5, 200, 30]}]
```

---

## 四、电路编译 — transpile_qcis

```python
from cqlib.mapping import transpile_qcis

# 编译到硬件拓扑
result = transpile_qcis(
    qcis_str=circuit.qcis,
    platform=platform,
    objective='size'    # 'size'|'depth'|'no_swap'
)
mapped_circuit, layout, swap_mapping, final_mapping = result
```

### 电路简化

```python
from cqlib.utils import QCIS_Simplify
simplified_qcis = QCIS_Simplify(circuit.qcis)
```

---

## 五、关键注意事项

1. **参数必须在 Circuit 创建时声明** — 不能事后添加已用于门的参数
2. **`assign_parameters` 默认返回新电路** — 需要接收返回值或设置 `inplace=True`
3. **测量比特顺序反序** — bit string `'01'` 表示 Q1=0, Q0=1
4. **`measure()` 需要先调用 `measure_all()`** — 否则无测量结果
5. **QCIS 参数值被裁剪到 [-π, π)** — 当 `qcis_compliant=True` 时
6. **ZZ 相互作用用 CNOT-RZ-CNOT 分解** — cqlib 原生不直接支持 RZZ 门
