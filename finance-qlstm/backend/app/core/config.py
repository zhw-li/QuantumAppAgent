"""
应用配置
- 全局参数设置
- 默认值定义
"""

import os


class Settings:
    """应用全局配置"""

    # 服务端口
    PORT: int = 8007

    # 默认股票
    DEFAULT_STOCK: str = "AAPL"

    # 数据集路径
    DATASET_DIR: str = "/dataset"

    # 结果保存路径
    RESULTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "results")

    # 训练默认参数
    DEFAULT_SEQ_LEN: int = 20
    DEFAULT_HIDDEN_SIZE: int = 8
    DEFAULT_N_QUBITS: int = 4
    DEFAULT_QLSTM_EPOCHS: int = 30
    DEFAULT_LSTM_EPOCHS: int = 50
    DEFAULT_SEED: int = 42

    # 可用股票列表
    AVAILABLE_STOCKS: list = [
        "AAPL", "BA", "CAT", "CSCO", "HD",
        "IBM", "JNJ", "JPM", "KO", "MMM", "MSFT", "WMT",
    ]


settings = Settings()
