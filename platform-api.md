# TianYanPlatform 完整 API

## 初始化

```python
from cqlib import TianYanPlatform

platform = TianYanPlatform(
    login_key="your_openid_token",   # 从天衍平台个人中心获取
    auto_login=True,                 # 自动登录
    machine_name="simulator"         # 目标设备
)
```

## 核心方法

### submit_experiment — 一键提交

```python
query_ids = platform.submit_experiment(
    circuit=qcis_string,           # QCIS 字符串或列表（批量≤600）
    language=QuantumLanguage.QCIS, # 量子语言
    name=None,                     # 实验名称
    parameters=None,               # 参数化电路的参数名
    values=None,                   # 参数值
    lab_id=None,                   # 实验集合ID
    lab_name=None,                 # 实验集合名称
    num_shots=12000,               # 采样次数
    machine_name=None,             # 设备名（可覆盖初始化时设置）
    is_verify=True,                # 是否验证电路
    noise=None,                    # 噪声模型列表
    quantum_state=None,            # 是否返回量子态
)
```

### query_experiment — 查询结果

```python
results = platform.query_experiment(
    query_id,                      # submit 返回的 query_id 或列表
    max_wait_time=3600,            # 最大等待秒数
    sleep_time=5,                  # 轮询间隔
    readout_calibration=False,     # 是否读出校准（仅真机）
    machine_config=None,           # 设备配置（校准时需要）
)
```

### 其他方法

| 方法 | 说明 |
|---|---|
| `create_lab(name, remark='')` | 创建实验集合 |
| `save_experiment(lab_id, circuit, ...)` | 保存电路不运行 |
| `run_experiment(exp_id, num_shots=12000)` | 运行已保存实验 |
| `query_quantum_computer_list()` | 查看可用设备 |
| `download_config(read_time, machine)` | 下载设备拓扑配置 |
| `qcis_check_regular(qcis_str)` | 验证 QCIS 语法 |
| `re_execute_task(query_id)` | 重新执行任务 |
| `stop_running_experiments(lab_id)` | 停止运行中实验 |

## 批量提交限制

| 电路数 | 最大 shots | 最大测量比特 |
|---|---|---|
| ≤50 | 100,000 | 15 |
| 51-100 | 50,000 | 30 |
| 101-600 | 10,000 | 全部 |

## 设备列表参考

**模拟器**：simulator(136bit), simulator_8, simulator_12, simulator_24
**真机**：通过 `query_quantum_computer_list()` 获取最新列表

## 噪声模型

```python
# 比特翻转
[{"noise_type": "bit-flip", "params": [0.1]}]
# 相位翻转
[{"noise_type": "phase-flip", "params": [0.1]}]
# 去极化噪声
[{"noise_type": "depolarizing", "params": [0.1]}]
# 退相干（操作时间, T2, T1）
[{"noise_type": "decoherence", "params": [0.5, 200, 30]}]
# 泊松去极化
[{"noise_type": "poisson-depolarizing", "params": [0.1]}]
# 自定义 Pauli
[{"noise_type": "pauli", "params": [[0.01, 0.02, 0.03]]}]
```
