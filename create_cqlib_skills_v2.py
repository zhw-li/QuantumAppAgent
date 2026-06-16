#!/usr/bin/env python3
"""Create all cqlib skill SKILL.md files"""
import os, sys

SKILLS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.evoscientist/skills")

def write_skill(name, content):
    path = os.path.join(SKILLS_DIR, name, "SKILL.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  {name}/SKILL.md: {os.path.getsize(path)} bytes")

print(f"Writing skills to {SKILLS_DIR}")

# cqlib-sdk
write_skill("cqlib-sdk", """---
name: cqlib-sdk
description: "Master reference for using the cqlib quantum computing SDK. Use when: writing quantum circuits with cqlib, building variational algorithms with Circuit/Parameter/StatevectorSimulator, submitting jobs to TianYan quantum cloud, transpiling circuits for hardware, or any quantum programming task using cqlib. Also use when choosing which cqlib sub-skill to invoke (cqlib-qaoa, cqlib-vqe, cqlib-qml, cqlib-hybrid). Triggers on keywords: cqlib, 量子电路, 量子模拟, TianYan, 天衍, 量子SDK, quantum circuit, StatevectorSimulator, Parameter, QCIS."
---

# cqlib SDK — 量子计算开发工具包

## 何时使用子 Skill

- **组合优化问题** -> `cqlib-qaoa`
- **求解分子基态能量** -> `cqlib-vqe`
- **量子分类/回归** -> `cqlib-qml`
- **混合量子经典架构** -> `cqlib-hybrid`

## 核心导入

```python
from cqlib import Circuit, Parameter, Qubit, Measure, Barrier
from cqlib import TianYanPlatform, GuoDunPlatform
from cqlib import StatevectorSimulator, SimpleSimulator
from cqlib.circuits import gates
```

## 一、Circuit — 量子电路

### 创建

```python
c = Circuit(4)                          # 指定比特数
c = Circuit([0, 1, 2, 3])               # 指定比特列表
c = Circuit(4, parameters=['theta', 'phi'])  # 带参数(必须创建时声明)
```

**关键**: 参数必须在 Circuit 创建时声明。

### 量子门

```python
# 单比特: h, x, y, z, s, sd, t, td, x2p, x2m, y2p, y2m
c.h(0); c.x(0)

# 参数化: rx, ry, rz, u
c.rx(0, theta); c.rz(0, phi); c.u(0, theta, phi, lam)

# 双比特: cx/cnot, cy, cz, swap
c.cx(0, 1); c.cz(0, 1)

# 三比特: ccx (Toffoli)
c.ccx(0, 1, 2)

# 测量与屏障
c.measure_all(); c.barrier_all()
```

### 参数绑定

```python
# 默认返回新电路！
bound = c.assign_parameters({'theta': 1.57})
bound = c.assign_parameters(theta=1.57)  # 关键字,支持部分绑定
c.assign_parameters({'theta': 1.57}, inplace=True)  # 原地
```

### 导出/组合

```python
combined = c1 + c2          # 拼接
qcis_str = c.qcis           # QCIS 字符串
qasm_str = c.to_qasm2()     # OpenQASM 2.0
c2 = Circuit.load(qcis_str) # 从 QCIS 加载
c.draw(category='text')     # 可视化
```

## 二、StatevectorSimulator

```python
sim = StatevectorSimulator(circuit=c)
state = sim.statevector()   # dict[str, complex]
probs = sim.probs()         # dict[str, float]
meas  = sim.measure()       # 需先 measure_all()
counts = sim.sample(shots=1024)
```

**关键**: 测量结果比特反序！`'01'` = Q1=0, Q0=1

## 三、TianYanPlatform

```python
platform = TianYanPlatform(login_key="token", machine_name="simulator")
qids = platform.submit_experiment(circuit=qcis_str, num_shots=10000)
results = platform.query_experiment(qids)
```

模拟器: simulator(136bit), simulator_8/12/24
噪声: `noise=[{"noise_type": "depolarizing", "params": [0.1]}]`

## 四、transpile_qcis

```python
from cqlib.mapping import transpile_qcis
mapped, layout, swap_map, final_map = transpile_qcis(circuit.qcis, platform, objective='size')
```

## 五、关键注意事项

1. 参数必须创建时声明
2. assign_parameters 默认返回新电路
3. 测量比特反序
4. measure() 需先 measure_all()
5. QCIS 参数裁剪到 [-pi, pi)
6. ZZ 分解用 CNOT-RZ-CNOT
""")

# cqlib-qaoa
write_skill("cqlib-qaoa", """---
name: cqlib-qaoa
description: "Implement QAOA using cqlib SDK. Use when: solving combinatorial optimization (MaxCut, TSP, Unit Commitment, portfolio), encoding QUBO/Ising as quantum circuits, building QAOA ansatz, running variational optimization with cqlib StatevectorSimulator, submitting QAOA to TianYan cloud. Triggers on: QAOA, 量子优化, QUBO, Ising, MaxCut, 机组组合, 变分优化."
---

# cqlib-qaoa — QAOA 量子近似优化算法

**前置 skill**: `cqlib-sdk`

## 执行流程

1. 业务问题 -> QUBO/Ising 建模
2. 构造代价哈密顿量, 编码为量子门
3. 构建 QAOA ansatz (p 层 H_C + H_M)
4. 经典优化器最小化期望值
5. 采样搜索最优可行解
6. 验证 vs 暴力搜索

## 代价哈密顿量编码

cqlib 无 RZZ, 用 CNOT-RZ-CNOT:

```python
def add_zz(circuit, qi, qj, coeff, gamma):
    angle = 2 * coeff * gamma
    circuit.cx(qi, qj)
    circuit.rz(qj, angle)
    circuit.cx(qi, qj)

def add_z(circuit, qi, coeff, gamma):
    circuit.rz(qi, 2 * coeff * gamma)
```

## QAOA Ansatz

```python
from cqlib import Circuit, Parameter
import numpy as np

def build_qaoa(n, Q, p=1):
    pn = []
    for l in range(p):
        pn.extend([f'g{l}', f'b{l}'])
    c = Circuit(n, parameters=pn)
    for i in range(n):
        c.h(i)
    for l in range(p):
        g, b = Parameter(f'g{l}'), Parameter(f'b{l}')
        for i in range(n):
            for j in range(i+1, n):
                if Q[i][j] != 0: add_zz(c, i, j, Q[i][j], g)
            if Q[i][i] != 0: add_z(c, i, Q[i][i], g)
        for i in range(n):
            c.rx(i, 2*b)
    c.measure_all()
    return c, pn
```

## 期望值 + 优化

```python
from cqlib import StatevectorSimulator
from scipy.optimize import minimize

def expectation(params, c, pn, n, Q):
    bc = c.assign_parameters(dict(zip(pn, params)))
    probs = StatevectorSimulator(circuit=bc).measure()
    exp = 0.0
    for bs, p in probs.items():
        if p < 1e-12: continue
        x = np.array([1 - 2*int(bs[-1-i]) for i in range(n)])
        cost = sum(Q[i][j]*(1-x[i])/2*(1-x[j])/2 for i in range(n) for j in range(n))
        exp += p * cost
    return exp

def run_qaoa(n, Q, p=1, restarts=10):
    c, pn = build_qaoa(n, Q, p)
    best, best_c = None, float('inf')
    for _ in range(restarts):
        x0 = np.random.uniform(0, np.pi, len(pn))
        r = minimize(expectation, x0, args=(c, pn, n, Q), method='COBYLA', options={'maxiter': 500})
        if r.fun < best_c: best_c, best = r.fun, r
    return best, c, pn
```

## 后处理: top-k 搜索最优可行解

最高概率解 != 最优可行解!

## 关键注意事项

1. ZZ 分解: CNOT-RZ-CNOT
2. 参数创建时声明
3. assign_parameters 返回新电路
4. 测量反序
5. 最高概率 != 最优可行: top-k 搜索
6. QUBO 编码质量是决定性因素: 自适应 lambda + 归一化
7. 多层提升精度但增加参数
8. 惩罚权重平衡
""")

# cqlib-vqe
write_skill("cqlib-vqe", """---
name: cqlib-vqe
description: "Implement VQE using cqlib SDK. Use when: computing molecular ground state energy, solving eigenvalue problems with variational circuits, building UCCSD/hardware-efficient ansatz, measuring Hamiltonian expectation with Pauli grouping, running VQE loops with cqlib StatevectorSimulator. Triggers on: VQE, 变分量子特征求解, 基态能量, 分子能量, UCCSD, Hartree-Fock, Pauli measurements."
---

# cqlib-vqe — 变分量子特征求解器

**前置 skill**: `cqlib-sdk`

## 执行流程

1. 定义哈密顿量 H
2. 选择变分 ansatz
3. 构建参数化电路
4. Pauli 分组测量期望值
5. 经典优化器最小化能量
6. 收敛分析 + 验证

## 哈密顿量

```python
hamiltonian = [
    (-1.052, 'Z0Z1'), (0.397, 'Z0'),
    (-0.398, 'Z1'), (0.011, 'X0X1'), (0.011, 'Y0Y1'),
]
```

## Ansatz

### Hardware-Efficient

```python
from cqlib import Circuit, Parameter

def he_ansatz(n, layers=2):
    pn = []
    for l in range(layers):
        for q in range(n):
            pn.extend([f'ry_{l}_{q}', f'rz_{l}_{q}'])
    c = Circuit(n, parameters=pn)
    for l in range(layers):
        for q in range(n):
            c.ry(q, Parameter(f'ry_{l}_{q}'))
            c.rz(q, Parameter(f'rz_{l}_{q}'))
        for q in range(n):
            c.cx(q, (q+1) % n)
        c.barrier_all()
    return c, pn
```

### UCCSD-Inspired

```python
def uccsd(n, ne):
    pn = []
    for i in range(ne):
        for a in range(ne, n):
            pn.append(f't1_{i}_{a}')
    c = Circuit(n, parameters=pn)
    for i in range(ne):
        c.x(i)  # Hartree-Fock
    c.barrier_all()
    for i in range(ne):
        for a in range(ne, n):
            c.cx(i, a)
            c.ry(a, Parameter(f't1_{i}_{a}'))
            c.cx(i, a)
    return c, pn
```

## Pauli 测量

```python
import numpy as np, re
from cqlib import StatevectorSimulator

def parse_pauli(s):
    return [(int(m.group(2)), m.group(1)) for m in re.finditer(r'([XYZ])(\d+)', s)]

def pauli_exp(circuit, terms, n):
    mc = circuit.copy()
    for qi, op in terms:
        if op == 'X': mc.h(qi)
        elif op == 'Y': mc.rx(qi, np.pi/2)
    mc.measure_all()
    probs = StatevectorSimulator(circuit=mc).measure()
    return sum((-1)**sum(int(bs[-1-q]) for q,_ in terms)*p for bs,p in probs.items())

def h_expectation(params, circuit, pn, H, n):
    bc = circuit.assign_parameters(dict(zip(pn, params)))
    return sum(c * pauli_exp(bc, parse_pauli(ps), n) for c, ps in H)
```

## 关键注意事项

1. X前加H, Y前加Rx(pi/2)做基变换
2. Pauli分组减少测量次数
3. UCCSD参数随规模急剧增长
4. Hartree-Fock初态用X门制备
5. 测量反序
6. assign_parameters返回新电路
7. 数值梯度替代解析梯度
8. 收敛: 能量变化 < 1e-6 Ha
""")

# cqlib-qml
write_skill("cqlib-qml", """---
name: cqlib-qml
description: "Implement Quantum Machine Learning using cqlib SDK. Use when: building VQC classifiers/regressors, quantum probability layers, angle encoding, training hybrid models with PyTorch + cqlib, quantum neural networks. Triggers on: QML, 量子机器学习, VQC, 变分量子分类器, 量子分类, 量子回归, quantum classifier, quantum layer."
---

# cqlib-qml — 量子机器学习

**前置 skill**: `cqlib-sdk`

## 执行流程

1. 选择数据编码策略
2. 构建变分量子电路
3. 定义量子概率层(PyTorch集成)
4. 训练混合模型
5. 评估验证

## 数据编码 — RY+RZ

```python
from cqlib import Circuit, Parameter

def angle_encoding(n_qubits, n_features):
    ep = []
    for i in range(n_features):
        ep.extend([f'ery_{i}', f'erz_{i}'])
    c = Circuit(n_qubits, parameters=ep)
    for i in range(min(n_qubits, n_features)):
        c.ry(i, Parameter(f'ery_{i}'))
        c.rz(i, Parameter(f'erz_{i}'))
    return c, ep
```

## 完整 VQC

```python
def build_vqc(nq, nf, nvl=2):
    ep, vp = [], []
    for i in range(nf): ep.extend([f'ery_{i}', f'erz_{i}'])
    for l in range(nvl):
        for q in range(nq): vp.extend([f'vry_{l}_{q}', f'vrz_{l}_{q}'])
    c = Circuit(nq, parameters=ep+vp)
    for i in range(min(nq, nf)):
        c.ry(i, Parameter(f'ery_{i}')); c.rz(i, Parameter(f'erz_{i}'))
    for l in range(nvl):
        for q in range(nq):
            c.ry(q, Parameter(f'vry_{l}_{q}')); c.rz(q, Parameter(f'vrz_{l}_{q}'))
        for q in range(nq): c.cx(q, (q+1)%nq)
    c.measure_all()
    return c, ep, vp
```

## 量子概率层

```python
import torch, torch.nn as nn
import numpy as np
from cqlib import StatevectorSimulator

class QuantumProbLayer(nn.Module):
    def __init__(self, nq, nf, nvl=2):
        super().__init__()
        self.nq, self.nf = nq, nf
        self.circuit, self.ep, self.vp = build_vqc(nq, nf, nvl)
        self.vw = nn.Parameter(torch.randn(len(self.vp))*0.1)
        self.is_ = nn.Parameter(torch.ones(nf))

    def forward(self, x):
        out = []
        for s in x:
            sc = torch.tanh(s * self.is_) * np.pi
            pd = {}
            for i in range(min(self.nq, self.nf)):
                idx = i*2
                if idx < len(self.ep): pd[self.ep[idx]] = sc[i].item()
                if idx+1 < len(self.ep): pd[self.ep[idx+1]] = sc[i].item()*0.5
            for j, pn in enumerate(self.vp): pd[pn] = self.vw[j].item()
            bc = self.circuit.assign_parameters(pd)
            probs = StatevectorSimulator(circuit=bc).measure()
            ns = 2**self.nq
            pv = torch.zeros(ns)
            for bs, p in probs.items(): pv[int(bs, 2)] = p
            out.append(pv)
        return torch.stack(out)
```

## 分类/回归模型

```python
class QClassifier(nn.Module):
    def __init__(self, nq, nf, nc, nvl=2):
        super().__init__()
        self.ql = QuantumProbLayer(nq, nf, nvl)
        self.head = nn.Linear(2**nq, nc)
    def forward(self, x): return self.head(self.ql(x))

class QRegressor(nn.Module):
    def __init__(self, nq, nf, nvl=2):
        super().__init__()
        self.ql = QuantumProbLayer(nq, nf, nvl)
        self.head = nn.Sequential(nn.Linear(2**nq, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, x): return self.head(self.ql(x)).squeeze(-1)
```

## 时间序列

```python
class QTimeSeries(nn.Module):
    def __init__(self, idim, hdim, nq, nvl=2):
        super().__init__()
        self.gru = nn.GRU(idim, hdim, batch_first=True)
        self.proj = nn.Linear(hdim, nq)
        self.ql = QuantumProbLayer(nq, nq, nvl)
        self.head = nn.Sequential(nn.Linear(2**nq, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x):
        _, hn = self.gru(x)
        return self.head(self.ql(self.proj(hn.squeeze(0)))).squeeze(-1)
```

## 关键注意事项

1. 参数创建时声明
2. assign_parameters 返回新电路
3. tanh缩放防梯度消失
4. 每样本独立模拟开销大
5. n_qubits <= 10
6. 概率 2^n 维 vs 期望 n 维
7. 测量反序
8. PyTorch autograd不穿过cqlib
""")

# cqlib-hybrid
write_skill("cqlib-hybrid", """---
name: cqlib-hybrid
description: "Implement hybrid quantum-classical algorithms with cqlib SDK + PyTorch. Use when: building HQNN, combining CNN/RNN/Transformer with quantum layers, parallel quantum circuits, integrating quantum layers into deep learning, designing hybrid architectures. Triggers on: hybrid quantum-classical, HQNN, 混合量子经典, 量子神经网络, parallel quantum layer, CNN+quantum, quantum deep learning."
---

# cqlib-hybrid — 混合量子经典算法

**前置 skill**: `cqlib-sdk`, `cqlib-qml`

## 执行流程

1. 选择经典特征提取器
2. 设计量子层架构(单路/并行/级联)
3. 实现PyTorch接口
4. 构建端到端混合模型
5. 训练评估调优

## 架构模式

- **串行**: 经典 -> 降维 -> 量子层 -> 经典头
- **并行**: 经典特征 -> N个并行量子通道 -> 拼接 -> 分类头
- **级联**: 交替堆叠经典和量子层

## 量子层(Z期望值输出)

```python
import torch, torch.nn as nn
import numpy as np
from cqlib import Circuit, Parameter, StatevectorSimulator

class HybridQuantumLayer(nn.Module):
    def __init__(self, nq, nf, nl=3):
        super().__init__()
        self.nq, self.nf = nq, nf
        self.circuit, self.pn = self._build(nl)
        nv = len(self.pn) - nf
        self.vw = nn.Parameter(torch.randn(nv)*0.1)
        self.is_ = nn.Parameter(torch.ones(nf))

    def _build(self, nl):
        pn = [f'e{i}' for i in range(self.nf)]
        for l in range(nl):
            for q in range(self.nq): pn.extend([f'ry_{l}_{q}', f'rz_{l}_{q}'])
        c = Circuit(self.nq, parameters=pn)
        for i in range(min(self.nq, self.nf)): c.rx(i, Parameter(f'e{i}'))
        for l in range(nl):
            for q in range(self.nq):
                c.ry(q, Parameter(f'ry_{l}_{q}')); c.rz(q, Parameter(f'rz_{l}_{q}'))
            for q in range(self.nq): c.cx(q, (q+1)%self.nq)
        c.measure_all()
        return c, pn

    def forward(self, x):
        out = []
        for s in x:
            sc = torch.tanh(s * self.is_) * np.pi
            pd = {f'e{i}': sc[i].item() for i in range(min(self.nq, self.nf))}
            vi = 0
            for n in self.pn:
                if n.startswith('ry_') or n.startswith('rz_'): pd[n] = self.vw[vi].item(); vi += 1
            bc = self.circuit.assign_parameters(pd)
            probs = StatevectorSimulator(circuit=bc).measure()
            exps = [sum((1-2*int(bs[-1-q]))*p for bs,p in probs.items()) for q in range(self.nq)]
            out.append(torch.tensor(exps, dtype=torch.float32))
        return torch.stack(out)
```

## HQNN-Parallel

```python
class HQNNParallel(nn.Module):
    def __init__(self, nc, nq=5, nql=3, nch=4):
        super().__init__()
        self.nch, self.nq = nch, nq
        self.fe = nn.Sequential(
            nn.Conv2d(3,32,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32,64,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64,128,3,padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1), nn.Flatten())
        self.proj = nn.ModuleList([nn.Linear(128, nq) for _ in range(nch)])
        self.ql = nn.ModuleList([HybridQuantumLayer(nq, nq, nql) for _ in range(nch)])
        self.cls = nn.Sequential(nn.Linear(nq*nch, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, nc))

    def forward(self, x):
        f = self.fe(x)
        qo = [self.ql[i](self.proj[i](f)) for i in range(self.nch)]
        return self.cls(torch.cat(qo, dim=1))
```

## 训练策略

```python
def create_optimizer(model, clr=1e-3, qlr=1e-2):
    cp, qp = [], []
    for n, p in model.named_parameters():
        if 'quantum' in n or 'vw' in n or 'is_' in n: qp.append(p)
        else: cp.append(p)
    return torch.optim.Adam([{'params': cp, 'lr': clr}, {'params': qp, 'lr': qlr}])
```

加速: n_qubits<=10, n_layers=2-3, 子采样训练, 预训练经典部分。

## 关键注意事项

1. 量子层是计算瓶颈
2. 并行通道增加表达力但线性增加时间
3. Z期望值 n_qubits 维 vs 概率 2^n 维
4. tanh缩放防止梯度爆炸
5. 量子层学习率通常更大(10x)
6. n_qubits <= 10
7. 测量反序
8. 并行通道用字典绑定更安全
""")

print("\nAll cqlib skills created successfully!")
