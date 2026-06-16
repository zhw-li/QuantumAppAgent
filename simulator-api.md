# StatevectorSimulator 完整 API

## 构造函数

```python
StatevectorSimulator(
    circuit: Circuit,
    is_fusion: bool = False,       # 门融合优化
    fusion_max_qubit: int = 5,     # 融合最大比特数
    omp_threads: int = 0,          # 0=自动
    fusion_th: int = 15            # 比特数≥15时启用融合
)
```

## 方法

| 方法 | 返回类型 | 说明 |
|---|---|---|
| `statevector()` | `dict[str, complex]` | 完整状态向量 |
| `probs()` | `dict[str, float]` | 全空间概率分布 |
| `measure()` | `dict[str, float]` | 仅测量比特概率（需先 measure_all） |
| `sample(shots=1024, is_sorted=False, sample_block_th=10, is_raw_data=False, rng_seed=None)` | `dict[str, int]` | 采样 |

## 调用依赖

```
statevector() → probs() → measure() → sample()
```

每个方法自动调用前置方法（如果尚未计算）。

## 比特顺序注意

测量结果的 bit string 是**反序**的：
- `'01'` → Q1=0, Q0=1（最右边=最低位=Q0）
- 计算 Z 期望值时：`bit=0 → +1, bit=1 → -1`

## SimpleSimulator

```python
from cqlib.simulator import SimpleSimulator

sim = SimpleSimulator(circuit=c)
counts = sim.sample(shots=1024)
```

SimpleSimulator 不计算状态向量，直接基于概率采样，速度更快但无法获取状态向量和梯度。
