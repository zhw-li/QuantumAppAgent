"""
Quantum Reservoir Computing (QRC) & Classic RC 模型模块

QRC: 量子储备池计算 - 固定随机量子电路作为储备池，Ridge回归读出
ClassicRC: 经典储备池计算 (Echo State Network) - 随机稀疏循环权重矩阵

关键设计:
- QRC 输入编码: 随机 W_in 投影 + RY 角度编码
- QRC 储备池: 固定随机 RY/RZ + CNOT 环纠缠, 参数冻结永不训练
- QRC 测量: Pauli-Z 期望值 → n_qubits 维特征
- 读出层: sklearn Ridge 回归
- cqlib bitstring 顺序: REVERSE (key[n_qubits-1-q] = qubit q 的值)
"""

import numpy as np
import time
from sklearn.linear_model import Ridge

from cqlib import Circuit
from cqlib.simulator import StatevectorSimulator


class ClassicRC:
    """
    经典储备池计算 (Echo State Network)
    
    储备池: 随机稀疏循环权重矩阵 W_res (谱半径 < 1 保证稳定性)
    输入权重: 随机 W_in 矩阵
    状态更新: h_t = tanh(W_res @ h_{t-1} + W_in @ x_t)
    读出: Ridge 回归从储备池状态到目标
    
    对于滑动窗口输入，将窗口展平后一次性输入（非逐步展开）。
    这是与QRC对齐的公平比较方式。
    """
    
    def __init__(self, n_reservoir=100, spectral_radius=0.9, sparsity=0.1,
                 input_scaling=1.0, ridge_alpha=1.0, seed=42,
                 use_nonlinear_features=True):
        """
        Args:
            n_reservoir: 储备池节点数
            spectral_radius: 谱半径 (必须 < 1 保证回声特性)
            sparsity: 储备池连接稀疏度 (0=全连接, 1=无连接)
            input_scaling: 输入缩放因子
            ridge_alpha: Ridge 回归正则化参数
            seed: 随机种子
            use_nonlinear_features: 是否使用非线性特征增强
                True: 读取层输入 = [h, h^2, mean(input)] (与QRC对齐)
                False: 读取层输入 = [h] (标准ESN)
        """
        self.n_reservoir = n_reservoir
        self.spectral_radius = spectral_radius
        self.sparsity = sparsity
        self.input_scaling = input_scaling
        self.ridge_alpha = ridge_alpha
        self.seed = seed
        self.use_nonlinear_features = use_nonlinear_features
        self.readout = None
        self.training_time = 0.0
        self.n_params = 0
        
        # 延迟初始化 (需要知道 input_dim)
        self.W_res = None
        self.W_in = None
        self._initialized = False
    
    def _initialize(self, input_dim):
        """初始化储备池权重矩阵"""
        rng = np.random.RandomState(self.seed)
        
        # 随机稀疏储备池权重
        W_res = rng.randn(self.n_reservoir, self.n_reservoir) * 0.1
        # 应用稀疏度
        mask = rng.rand(self.n_reservoir, self.n_reservoir) > self.sparsity
        W_res[mask] = 0.0
        
        # 调整谱半径
        eigenvalues = np.linalg.eigvals(W_res)
        max_eigenvalue = np.max(np.abs(eigenvalues))
        if max_eigenvalue > 0:
            W_res = W_res * (self.spectral_radius / max_eigenvalue)
        
        # 随机输入权重
        W_in = rng.uniform(-self.input_scaling, self.input_scaling,
                           size=(self.n_reservoir, input_dim))
        
        self.W_res = W_res.astype(np.float64)
        self.W_in = W_in.astype(np.float64)
        
        # 读取层特征维度
        if self.use_nonlinear_features:
            self._readout_dim = 2 * self.n_reservoir + 1
        else:
            self._readout_dim = self.n_reservoir
        
        self.n_params = (self.n_reservoir * self.n_reservoir * (1 - self.sparsity) 
                         + self.n_reservoir * input_dim 
                         + self._readout_dim + 1)  # +readout weights + bias
        self._initialized = True
        print(f"[ClassicRC] 初始化: reservoir={self.n_reservoir}, "
              f"spectral_radius={self.spectral_radius:.2f}, "
              f"sparsity={self.sparsity:.2f}, "
              f"nonlinear_features={self.use_nonlinear_features}, "
              f"readout_dim={self._readout_dim}, params≈{int(self.n_params)}")
    
    def _get_reservoir_state(self, x_flat):
        """
        计算储备池状态 (含可选非线性特征增强)
        
        对于滑动窗口输入，使用展平的方式:
        h = tanh(W_in @ x_flat)  (单次输入，无循环)
        
        注: 标准ESN是逐步展开的，但为了与QRC公平比较，
        这里也使用单次输入方式（QRC对每个窗口只运行一次电路）。
        如需逐步展开，使用 run_reservoir_sequential 方法。
        """
        # 线性输入变换
        h = self.W_in @ x_flat
        # 非线性激活
        h = np.tanh(h)
        
        # 非线性特征增强 (与QRC对齐)
        if self.use_nonlinear_features:
            squares = h ** 2
            input_mean = np.array([np.mean(x_flat)])
            h_aug = np.concatenate([h, squares, input_mean])
            return h_aug
        else:
            return h
    
    def _run_reservoir_sequential(self, X_window):
        """
        逐步展开储备池 (标准ESN方式)
        
        Args:
            X_window: np.array, shape (window_size, n_features) - 一个窗口的时序数据
        
        Returns:
            h_final: 储备池最终状态
        """
        h = np.zeros(self.n_reservoir, dtype=np.float64)
        for t in range(X_window.shape[0]):
            x_t = X_window[t]
            h = np.tanh(self.W_res @ h + self.W_in @ x_t)
        return h
    
    def fit(self, X_train, y_train, sequential=False):
        """
        训练读出层
        
        Args:
            X_train: np.array, shape (n_samples, window_size) 或 (n_samples, window_size, n_features)
            y_train: np.array, shape (n_samples,)
            sequential: 是否使用逐步展开 (True=标准ESN, False=与QRC对齐的单次输入)
        """
        if X_train.ndim == 2:
            # (n_samples, window_size) → 单特征
            input_dim = X_train.shape[1]
        else:
            # (n_samples, window_size, n_features) → 多特征
            input_dim = X_train.shape[1] * X_train.shape[2]
        
        if not self._initialized:
            self._initialize(input_dim)
        
        start_time = time.time()
        
        # 收集所有储备池状态
        readout_dim = self._readout_dim
        reservoir_states = np.zeros((len(X_train), readout_dim), dtype=np.float64)
        for i in range(len(X_train)):
            if sequential and X_train.ndim == 3:
                h = self._run_reservoir_sequential(X_train[i])
                if self.use_nonlinear_features:
                    squares = h ** 2
                    x_flat = X_train[i].flatten()
                    input_mean = np.array([np.mean(x_flat)])
                    h = np.concatenate([h, squares, input_mean])
                reservoir_states[i] = h
            else:
                x_flat = X_train[i].flatten()
                reservoir_states[i] = self._get_reservoir_state(x_flat)
        
        # Ridge 回归
        self.readout = Ridge(alpha=self.ridge_alpha)
        self.readout.fit(reservoir_states, y_train)
        
        self.training_time = time.time() - start_time
        print(f"[ClassicRC] 训练完成: {self.training_time:.2f}s, "
              f"特征维度={readout_dim}, "
              f"状态范围=[{reservoir_states.min():.4f}, {reservoir_states.max():.4f}]")
    
    def predict(self, X_test, sequential=False):
        """
        预测
        
        Args:
            X_test: np.array, shape (n_samples, window_size) 或 (n_samples, window_size, n_features)
            sequential: 是否使用逐步展开
        
        Returns:
            y_pred: np.array, shape (n_samples,)
        """
        readout_dim = self._readout_dim
        reservoir_states = np.zeros((len(X_test), readout_dim), dtype=np.float64)
        for i in range(len(X_test)):
            if sequential and X_test.ndim == 3:
                h = self._run_reservoir_sequential(X_test[i])
                if self.use_nonlinear_features:
                    squares = h ** 2
                    x_flat = X_test[i].flatten()
                    input_mean = np.array([np.mean(x_flat)])
                    h = np.concatenate([h, squares, input_mean])
                reservoir_states[i] = h
            else:
                x_flat = X_test[i].flatten()
                reservoir_states[i] = self._get_reservoir_state(x_flat)
        
        return self.readout.predict(reservoir_states)


class QuantumRC:
    """
    量子储备池计算 (QRC)
    
    输入编码: 随机 W_in 投影到 n_qubits 维 → RY 角度编码 [0, π]
    量子储备池: 固定随机 RY/RZ 旋转 + CNOT 环纠缠 (参数永不训练)
    测量: Pauli-Z 期望值 → n_qubits 维特征
    读出: Ridge 回归
    
    cqlib bitstring 顺序: REVERSE order
    - key[n_qubits - 1 - q] = qubit q 的测量值
    - <Z_q> = sum(prob * (1 - 2 * int(key[n_qubits-1-q])))
    """
    
    def __init__(self, n_qubits=4, reservoir_depth=2, ridge_alpha=1.0,
                 input_scaling=np.pi, seed=42, use_nonlinear_features=True):
        """
        Args:
            n_qubits: 量子比特数 (决定储备池输出维度)
            reservoir_depth: 储备池层数 (旋转+纠缠的重复次数)
            ridge_alpha: Ridge 回归正则化参数
            input_scaling: 输入缩放 (默认π, 将投影值映射到[0,π])
            seed: 随机种子
            use_nonlinear_features: 是否使用非线性特征增强
                True: 读取层输入 = [<Z_q>, <Z_q>^2, 输入平均值]
                False: 读取层输入 = [<Z_q>] (仅Pauli-Z期望)
                非线性特征可将有效特征维度从 n_qubits 扩展到 2*n_qubits+1,
                显著提升读取层的表达能力, 且不增加任何可训练参数
        """
        self.n_qubits = n_qubits
        self.reservoir_depth = reservoir_depth
        self.ridge_alpha = ridge_alpha
        self.input_scaling = input_scaling
        self.seed = seed
        self.use_nonlinear_features = use_nonlinear_features
        self.readout = None
        self.training_time = 0.0
        self.n_params = 0
        
        # 延迟初始化
        self.W_in = None
        self.reservoir_params = None
        self._initialized = False
    
    def _initialize(self, input_dim):
        """初始化量子储备池参数 (全部冻结, 不参与训练)"""
        rng = np.random.RandomState(self.seed)
        
        # 随机输入投影矩阵 (input_dim → n_qubits)
        self.W_in = rng.uniform(-1, 1, size=(self.n_qubits, input_dim)).astype(np.float64)
        
        # 冻结的储备池旋转参数: (depth, n_qubits, 2) → RY和RZ各一个角度
        self.reservoir_params = rng.uniform(
            0, 2 * np.pi,
            size=(self.reservoir_depth, self.n_qubits, 2)
        ).astype(np.float64)
        
        # 参数计数: W_in + reservoir rotations + readout
        readout_dim = self._readout_dim()
        self.n_params = (self.n_qubits * input_dim  # W_in (frozen)
                         + self.reservoir_depth * self.n_qubits * 2  # reservoir angles (frozen)
                         + readout_dim + 1)  # readout weights + bias (trained)
        
        self._initialized = True
        print(f"[QuantumRC] 初始化: qubits={self.n_qubits}, "
              f"depth={self.reservoir_depth}, "
              f"nonlinear_features={self.use_nonlinear_features}, "
              f"readout_dim={self._readout_dim()}, params={self.n_params}")
    
    def _readout_dim(self):
        """读出层输入维度"""
        if self.use_nonlinear_features:
            # [<Z_q>, <Z_q>^2, mean(input)] → 2*n_qubits + 1
            return 2 * self.n_qubits + 1
        else:
            return self.n_qubits
    
    def _augment_features(self, expectations, x_flat=None):
        """
        非线性特征增强
        
        标准 QRC 读取层只接收 Pauli-Z 期望值 (n_qubits 维)。
        增加 <Z_q>^2 (二阶非线性) 和输入均值, 扩展到 2*n_qubits+1 维。
        这是储备池计算中的标准技巧 (类似 ESN 的 leaky integrator)。
        
        Args:
            expectations: np.array, shape (n_qubits,) - Pauli-Z 期望值
            x_flat: np.array, 展平的输入 (用于残差连接)
        
        Returns:
            features: np.array, 增强后的特征向量
        """
        if self.use_nonlinear_features:
            squares = expectations ** 2
            # 残差连接: 输入的均值 (1维, 提供全局上下文)
            input_mean = np.array([np.mean(x_flat)]) if x_flat is not None else np.array([0.0])
            features = np.concatenate([expectations, squares, input_mean])
        else:
            features = expectations
        return features
    
    def _build_circuit(self, input_angles):
        """
        构建量子电路: 输入编码 + 冻结储备池
        
        Args:
            input_angles: np.array, shape (n_qubits,) - 每个qubit的RY旋转角度
        
        Returns:
            Circuit: cqlib 量子电路
        """
        qc = Circuit(self.n_qubits)
        
        # 1. 输入编码: RY 门 (cqlib API: ry(qubit, theta))
        for q in range(self.n_qubits):
            angle = float(np.clip(input_angles[q], 0, np.pi))
            qc.ry(q, angle)
        
        # 2. 冻结储备池层
        for layer in range(self.reservoir_depth):
            # 随机旋转 (冻结) (cqlib API: ry/rz(qubit, theta))
            for q in range(self.n_qubits):
                qc.ry(q, float(self.reservoir_params[layer, q, 0]))
                qc.rz(q, float(self.reservoir_params[layer, q, 1]))
            
            # CNOT 环纠缠: qubit_i → qubit_{i+1}, last → first
            # cqlib API: cx(control_qubit, target_qubit)
            for q in range(self.n_qubits):
                qc.cx(q, (q + 1) % self.n_qubits)
        
        return qc
    
    def _compute_expectations(self, probs_dict):
        """
        从概率分布计算 Pauli-Z 期望值
        
        cqlib bitstring 顺序: REVERSE order
        key[n_qubits - 1 - q] 对应 qubit q 的测量值
        
        <Z_q> = sum(prob * (1 - 2 * bit_val_q))
        
        Args:
            probs_dict: dict, {bitstring: probability}
        
        Returns:
            expectations: np.array, shape (n_qubits,)
        """
        expectations = np.zeros(self.n_qubits, dtype=np.float64)
        n_q = self.n_qubits
        
        for bitstring, prob in probs_dict.items():
            for q in range(n_q):
                # REVERSE order: key[n_qubits-1-q] = qubit q
                bit_val = int(bitstring[n_q - 1 - q])
                expectations[q] += prob * (1 - 2 * bit_val)
        
        return expectations
    
    def _get_reservoir_state(self, x_flat):
        """
        获取量子储备池状态 (含非线性特征增强)
        
        Args:
            x_flat: np.array, 展平的输入窗口
        
        Returns:
            state: np.array, shape (readout_dim,) - 增强后的储备池特征
        """
        # 输入投影: W_in @ x_flat → n_qubits 维
        projected = self.W_in @ x_flat
        
        # 缩放到 [0, π] (使用 sigmoid 压缩 + π 缩放)
        # 先归一化到 [-1, 1]，再映射到 [0, π]
        input_angles = self.input_scaling * (1.0 / (1.0 + np.exp(-projected)))  # sigmoid → (0, π)
        
        # 构建电路
        circuit = self._build_circuit(input_angles)
        
        # 模拟
        sim = StatevectorSimulator(circuit=circuit)
        probs = sim.probs()
        
        # 计算 Pauli-Z 期望
        expectations = self._compute_expectations(probs)
        
        # 非线性特征增强
        features = self._augment_features(expectations, x_flat)
        
        return features
    
    def fit(self, X_train, y_train):
        """
        训练读出层 (只训练 Ridge 回归，量子储备池参数冻结)
        
        Args:
            X_train: np.array, shape (n_samples, window_size) 或 (n_samples, window_size, n_features)
            y_train: np.array, shape (n_samples,)
        """
        if X_train.ndim == 2:
            input_dim = X_train.shape[1]
        else:
            input_dim = X_train.shape[1] * X_train.shape[2]
        
        if not self._initialized:
            self._initialize(input_dim)
        
        start_time = time.time()
        
        # 逐样本收集储备池状态 (StatevectorSimulator 不支持批量)
        readout_dim = self._readout_dim()
        reservoir_states = np.zeros((len(X_train), readout_dim), dtype=np.float64)
        for i in range(len(X_train)):
            x_flat = X_train[i].flatten()
            reservoir_states[i] = self._get_reservoir_state(x_flat)
            
            if (i + 1) % 50 == 0:
                elapsed = time.time() - start_time
                print(f"  [QRC] 进度: {i+1}/{len(X_train)} ({elapsed:.1f}s)")
        
        # Ridge 回归
        self.readout = Ridge(alpha=self.ridge_alpha)
        self.readout.fit(reservoir_states, y_train)
        
        self.training_time = time.time() - start_time
        print(f"[QuantumRC] 训练完成: {self.training_time:.2f}s, "
              f"状态范围=[{reservoir_states.min():.4f}, {reservoir_states.max():.4f}]")
    
    def predict(self, X_test):
        """
        预测
        
        Args:
            X_test: np.array, shape (n_samples, window_size) 或 (n_samples, window_size, n_features)
        
        Returns:
            y_pred: np.array, shape (n_samples,)
        """
        start_time = time.time()
        readout_dim = self._readout_dim()
        reservoir_states = np.zeros((len(X_test), readout_dim), dtype=np.float64)
        
        for i in range(len(X_test)):
            x_flat = X_test[i].flatten()
            reservoir_states[i] = self._get_reservoir_state(x_flat)
            
            if (i + 1) % 50 == 0:
                elapsed = time.time() - start_time
                print(f"  [QRC] 预测进度: {i+1}/{len(X_test)} ({elapsed:.1f}s)")
        
        return self.readout.predict(reservoir_states)
    
    def count_circuit_params(self):
        """统计量子电路参数数 (全部冻结)"""
        return self.reservoir_depth * self.n_qubits * 2 + self.n_qubits  # reservoir + W_in projection


def compute_metrics(y_true, y_pred, handle_zero_mape=True):
    """
    计算评估指标
    
    Args:
        y_true: 真实值 (原始尺度)
        y_pred: 预测值 (原始尺度)
        handle_zero_mape: 是否处理接近零的MAPE分母
    
    Returns:
        dict: {RMSE, MAE, MAPE}
    """
    y_true = np.array(y_true, dtype=np.float64)
    y_pred = np.array(y_pred, dtype=np.float64)
    
    # RMSE
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    # MAE
    mae = np.mean(np.abs(y_true - y_pred))
    
    # MAPE (处理接近零的分母)
    if handle_zero_mape:
        mask = np.abs(y_true) > 1e-6  # 跳过接近零的真实值
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        else:
            mape = float('inf')
    else:
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    return {
        'RMSE': round(float(rmse), 6),
        'MAE': round(float(mae), 6),
        'MAPE': round(float(mape), 6)
    }


if __name__ == "__main__":
    # 简单测试: 验证 QRC 和 ClassicRC 的基本功能
    print("=" * 60)
    print("QRC / ClassicRC 模型测试")
    print("=" * 60)
    
    np.random.seed(42)
    n_samples = 20
    window_size = 5
    
    # 生成简单测试数据 (正弦波)
    t = np.linspace(0, 4 * np.pi, n_samples + window_size + 1)
    signal = np.sin(t).astype(np.float64)
    
    X = np.array([signal[i:i+window_size] for i in range(n_samples)])
    y = np.array([signal[i+window_size] for i in range(n_samples)])
    
    split = int(0.8 * n_samples)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # 测试 ClassicRC
    print("\n--- ClassicRC ---")
    crc = ClassicRC(n_reservoir=20, seed=42)
    crc.fit(X_train, y_train)
    y_pred_crc = crc.predict(X_test)
    metrics_crc = compute_metrics(y_test, y_pred_crc)
    print(f"指标: {metrics_crc}")
    print(f"参数数: {crc.n_params}")
    
    # 测试 QuantumRC
    print("\n--- QuantumRC ---")
    qrc = QuantumRC(n_qubits=4, reservoir_depth=2, seed=42)
    qrc.fit(X_train, y_train)
    y_pred_qrc = qrc.predict(X_test)
    metrics_qrc = compute_metrics(y_test, y_pred_qrc)
    print(f"指标: {metrics_qrc}")
    print(f"参数数: {qrc.n_params}")
