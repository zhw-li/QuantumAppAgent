"""
QLSTM 项目全局配置
==================
使用 pydantic-settings 从环境变量加载配置，支持 .env 文件。
所有路径、端口、超参数均可通过环境变量覆盖。
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置项

    优先级: 环境变量 > .env 文件 > 默认值

    Attributes
    ----------
    DATA_PATH : str
        股票 CSV 数据文件路径
    RESULT_DIR : str
        训练结果输出目录（含模型权重、对比 JSON、曲线数据）
    MODEL_DIR : str
        模型权重保存目录，默认与 RESULT_DIR 一致
    HOST : str
        FastAPI 监听地址
    PORT : int
        FastAPI 监听端口
    SEQ_LEN : int
        输入时序窗口长度（须与训练时一致）
    N_FEATURES : int
        输入特征维度（须与训练时一致）
    N_HIDDEN_QUANTUM : int
        QLSTM 隐藏层维度（须与训练时一致）
    N_QUBITS : int
        QLSTM 量子比特数（须与训练时一致）
    N_LAYERS_QUANTUM : int
        QLSTM VQC 变分层层数（须与训练时一致）
    N_HIDDEN_CLASSIC : int
        经典 LSTM 隐藏层维度（须与训练时一致）
    DEVICE : str
        计算设备，'cpu' 或 'cuda'
    """

    # ── 数据与结果路径 ──
    DATA_PATH: str = str(
        Path(__file__).resolve().parents[4] / "dataset" / "AAPL.csv"
    )
    RESULT_DIR: str = str(
        Path(__file__).resolve().parents[4] / "qlstm" / "results"
    )
    MODEL_DIR: str = ""  # 默认与 RESULT_DIR 一致

    # ── 服务配置 ──
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # ── 模型超参数（须与训练时一致，用于加载权重时重建模型结构）──
    SEQ_LEN: int = 20
    N_FEATURES: int = 9  # data_loader 输出的 9 维特征
    N_HIDDEN_QUANTUM: int = 16
    N_QUBITS: int = 2
    N_LAYERS_QUANTUM: int = 2
    N_HIDDEN_CLASSIC: int = 64
    N_LAYERS_CLASSIC: int = 2
    DEVICE: str = "cpu"

    model_config = {
        "env_prefix": "QLSTM_",  # 环境变量前缀: QLSTM_DATA_PATH, QLSTM_PORT ...
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def model_post_init(self, __context) -> None:
        """初始化后处理：若 MODEL_DIR 未设置则默认指向 RESULT_DIR"""
        if not self.MODEL_DIR:
            object.__setattr__(self, "MODEL_DIR", self.RESULT_DIR)

        # 确保结果目录存在
        os.makedirs(self.RESULT_DIR, exist_ok=True)
        os.makedirs(self.MODEL_DIR, exist_ok=True)


# ── 全局单例 ──
settings = Settings()
