"""
Pydantic数据模型
- 请求/响应schema定义
- 所有API响应字段名使用大写（关键：RMSE, MAE, MAPE, QLSTM, LSTM, OHLC）
"""

from pydantic import BaseModel, Field
from typing import Optional


# ============= 请求模型 =============

class TrainRequest(BaseModel):
    """训练请求"""
    stock: str = Field(default="AAPL", description="股票代码")
    seq_len: int = Field(default=20, description="时序窗口长度")
    hidden_size: int = Field(default=8, description="隐藏层维度")
    n_qubits: int = Field(default=4, description="量子比特数")
    qlstm_epochs: int = Field(default=30, description="QLSTM训练轮数")
    lstm_epochs: int = Field(default=50, description="LSTM训练轮数")


# ============= 响应模型 =============

class MetricsModel(BaseModel):
    """评估指标（字段名大写）"""
    RMSE: float
    MAE: float
    MAPE: float


class TrainResponse(BaseModel):
    """训练响应"""
    status: str
    message: str
    QLSTM_metrics: MetricsModel
    LSTM_metrics: MetricsModel


class ModelParamsInfo(BaseModel):
    """模型参数信息"""
    n_qubits: Optional[int] = None
    layers: Optional[int] = None
    hidden_size: int
    total_params: int


class ComparisonResponse(BaseModel):
    """对比结果响应"""
    QLSTM: MetricsModel
    LSTM: MetricsModel
    improvement: dict


class PredictionsResponse(BaseModel):
    """预测曲线响应"""
    dates: list
    actual: list
    QLSTM: list
    LSTM: list


class TrainingCurvesResponse(BaseModel):
    """训练损失曲线响应"""
    QLSTM: list
    LSTM: list


class OHLCItem(BaseModel):
    """K线数据项（字段名大写）"""
    open: float
    high: float
    low: float
    close: float


class RawDataResponse(BaseModel):
    """原始数据响应"""
    dates: list
    OHLC: list
    volume: list


class StocksResponse(BaseModel):
    """可用股票列表响应"""
    stocks: list


class ModelInfoResponse(BaseModel):
    """模型架构信息响应"""
    QLSTM: dict
    LSTM: dict
