# Circuit 完整 API 参考

## 构造函数

```python
Circuit(qubits: int | Qubit | list[Qubit|int],
        parameters: list[Parameter|str] | None = None)
```

## 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `qubits` | `list[Qubit]` | 所有量子比特 |
| `num_qubits` | `int` | 比特数 |
| `parameters` | `list[Parameter]` | 所有已声明参数 |
| `parameters_value` | `dict[Parameter, float\|int]` | 参数当前值 |
| `circuit_data` | `list[InstructionData]` | 指令序列 |
| `instruction_sequence` | `list[InstructionData]` | 同 circuit_data |
| `qcis` | `str` | 导出 QCIS 字符串 |

## 单比特门

| 方法 | 说明 |
|---|---|
| `h(q)` | Hadamard |
| `x(q)` | Pauli-X |
| `y(q)` | Pauli-Y |
| `z(q)` | Pauli-Z |
| `s(q)` | S门(π/2相移) |
| `sd(q)` | S†门 |
| `t(q)` | T门(π/4相移) |
| `td(q)` | T†门 |
| `x2p(q)` | X/2+旋转 |
| `x2m(q)` | X/2-旋转 |
| `y2p(q)` | Y/2+旋转 |
| `y2m(q)` | Y/2-旋转 |

## 参数化单比特门

| 方法 | 参数 | 说明 |
|---|---|---|
| `rx(q, theta)` | theta: float\|Parameter | 绕X轴旋转 |
| `ry(q, theta)` | theta: float\|Parameter | 绕Y轴旋转 |
| `rz(q, theta)` | theta: float\|Parameter | 绕Z轴旋转 |
| `rxy(q, phi, theta)` | phi, theta: float\|Parameter | RXY旋转 |
| `xy(q, theta)` | theta: float\|Parameter | XY旋转 |
| `u(q, theta, phi, lam)` | 三个角度 | 通用U3门 |

## 双/三比特门

| 方法 | 说明 |
|---|---|
| `cx(ctrl, tgt)` | CNOT (别名: cnot) |
| `cy(ctrl, tgt)` | Controlled-Y |
| `cz(ctrl, tgt)` | Controlled-Z |
| `crx(ctrl, tgt, theta)` | Controlled-RX |
| `cry(ctrl, tgt, theta)` | Controlled-RY |
| `crz(ctrl, tgt, theta)` | Controlled-RZ |
| `swap(q1, q2)` | SWAP |
| `ccx(c1, c2, t)` | Toffoli |

## 测量与屏障

| 方法 | 说明 |
|---|---|
| `measure(qubits)` | 测量指定比特 |
| `measure_all()` | 测量所有未测量比特 |
| `barrier(*qubits)` | 插入屏障 |
| `barrier_all()` | 全部比特屏障 |

## 参数绑定

```python
assign_parameters(
    values: dict[str|Parameter, float|int] | Sequence[float|int] = None,
    inplace: bool = False,
    cache_params: bool = False,
    **kwargs
) -> Circuit
```

- 默认 `inplace=False`，返回新电路
- 支持字典绑定、位置绑定、关键字绑定（支持部分绑定）

## 电路操作

| 操作 | 说明 |
|---|---|
| `c1 + c2` | 拼接，返回新电路 |
| `c1 += c2` | 原地追加 |
| `c.copy()` | 深拷贝 |
| `c.depth()` | 电路深度 |
| `c.draw(category)` | 可视化 ('text'/'mpl'/'latex') |
| `c.to_qasm2()` | 导出 QASM2 |
| `Circuit.load(qcis_str)` | 从 QCIS 加载 |
| `c.as_str(qcis_compliant=False)` | 导出字符串 |
