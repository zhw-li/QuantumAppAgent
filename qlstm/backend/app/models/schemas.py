"""
QLSTM 项目 API 数据模型
========================
定义所有请求/响应的 Pydantic schema，确保接口类型安全与自动文档生成。
"""

import datetime as _dt
from typing import List, Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# 1. 预测相关
# ──────────────────────────────────────────────

class PredictionRequest(BaseModel):
    """未来价格预测请求

    Attributes
    ----------
    start_date : _dt.date | None
        预测起始日期（默认使用数据集最后一天）
    n_days : int
        预测天数，默认 5，范围 [1, 30]
    """
    start_date: Optional[_dt.date] = Field(
        default=None,
        description="预测起始日期，为空则从数据集最后一天开始",
    )
    n_days: int = Field(
        default=5,
        ge=1,
        le=30,
        description="预测未来天数（1~30）",
    )


class PredictionResponse(BaseModel):
    """未来价格预测响应

    Attributes
    ----------
    dates : List[str]
        预测日期列表（YYYY-MM-DD 格式）
    predictions_classic : List[float]
        经典 LSTM 预测价格
    predictions_quantum : List[float]
        QLSTM 预测价格
    confidence : float
        预测置信度（基于验证集 RMSE 的启发值，0~1）
    """
    dates: List[str] = Field(description="预测日期列表")
    predictions_classic: List[float] = Field(description="经典 LSTM 预测价格")
    predictions_quantum: List[float] = Field(description="QLSTM 预测价格")
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="预测置信度 (0~1)",
    )


# ──────────────────────────────────────────────
# 2. 模型对比
# ──────────────────────────────────────────────

class MetricsResponse(BaseModel):
    """单个模型的评估指标

    Attributes
    ----------
    model_name : str
        模型名称（Classic LSTM / QLSTM）
    mse : float
        均方误差
    rmse : float
        均方根误差
    mae : float
        平均绝对误差
    mape : float
        平均绝对百分比误差（%）
    """
    model_name: str
    mse: float
    rmse: float
    mae: float
    mape: float


class ComparisonResponse(BaseModel):
    """两个模型对比结果

    Attributes
    ----------
    classic_metrics : MetricsResponse
        经典 LSTM 指标
    quantum_metrics : MetricsResponse
        QLSTM 指标
    improvement_pct : float
        QLSTM 相对经典 LSTM 的 RMSE 改善百分比（正值=量子更优）
    train_time_classic : float
        经典 LSTM 训练耗时（秒）
    train_time_quantum : float
        QLSTM 训练耗时（秒）
    quantum_iterations : int
        QLSTM 迭代轮次
    best_iteration : int
        最优 QLSTM 迭代编号
    """
    classic_metrics: MetricsResponse
    quantum_metrics: MetricsResponse
    improvement_pct: float = Field(
        description="QLSTM 相对经典 LSTM 的 RMSE 改善百分比"
    )
    train_time_classic: float = Field(default=0.0, description="经典模型训练耗时(秒)")
    train_time_quantum: float = Field(default=0.0, description="量子模型训练耗时(秒)")
    quantum_iterations: int = Field(default=1, description="量子模型迭代轮次")
    best_iteration: int = Field(default=1, description="最优量子模型迭代编号")


# ──────────────────────────────────────────────
# 3. 训练状态
# ──────────────────────────────────────────────

class TrainingStatus(BaseModel):
    """训练状态（当前仅支持查询已完成结果，未来可扩展实时推送）

    Attributes
    ----------
    status : str
        训练状态: idle / training / completed / error
    epoch : int
        当前训练轮次
    total_epochs : int
        总训练轮次
    train_loss : float
        当前训练损失
    val_loss : float
        当前验证损失
    model_name : str
        正在训练的模型名称
    """
    status: str = Field(default="idle", description="训练状态: idle/training/completed/error")
    epoch: int = Field(default=0, description="当前训练轮次")
    total_epochs: int = Field(default=0, description="总训练轮次")
    train_loss: float = Field(default=0.0, description="当前训练损失")
    val_loss: float = Field(default=0.0, description="当前验证损失")
    model_name: str = Field(default="", description="正在训练的模型名称")


# ──────────────────────────────────────────────
# 4. 训练曲线 & 预测结果（通用列表响应）
# ──────────────────────────────────────────────

class TrainingCurvePoint(BaseModel):
    """单个 epoch 的训练/验证损失"""
    epoch: int
    train_loss: float
    val_loss: float


class TrainingCurvesResponse(BaseModel):
    """训练损失曲线数据

    Attributes
    ----------
    classic : List[TrainingCurvePoint]
        经典 LSTM 训练曲线
    quantum : List[TrainingCurvePoint]
        QLSTM 训练曲线（最优迭代）
    """
    classic: List[TrainingCurvePoint]
    quantum: List[TrainingCurvePoint]


class TestPredictionsResponse(BaseModel):
    """测试集预测结果（用于绘图对比）

    Attributes
    ----------
    dates : List[str]
        测试集日期
    actuals : List[float]
        真实收盘价
    classic_predictions : List[float]
        经典 LSTM 预测
    quantum_predictions : List[float]
        QLSTM 预测
    """
    dates: List[str] = Field(description="测试集日期")
    actuals: List[float] = Field(description="真实收盘价")
    classic_predictions: List[float] = Field(description="经典 LSTM 预测值")
    quantum_predictions: List[float] = Field(description="QLSTM 预测值")


class RawDataResponse(BaseModel):
    """原始股票数据（用于前端 K 线/折线图展示）

    Attributes
    ----------
    dates : List[str]
        日期列表
    close : List[float]
        收盘价
    volume : List[float]
        成交量
    open : List[float]
        开盘价
    high : List[float]
        最高价
    low : List[float]
        最低价
    """
    dates: List[str] = Field(description="日期列表")
    close: List[float] = Field(description="收盘价")
    volume: List[float] = Field(description="成交量")
    open: List[float] = Field(default=[], description="开盘价")
    high: List[float] = Field(default=[], description="最高价")
    low: List[float] = Field(default=[], description="最低价")
