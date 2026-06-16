"""
QLSTM 项目 API 路由
====================
定义所有 RESTful 接口，挂载到 /api 前缀下。
每个路由仅负责参数校验与响应格式化，业务逻辑委托给 PredictionService。

路由列表:
    GET  /api/comparison       — 获取模型对比指标
    GET  /api/predictions      — 获取测试集预测结果
    GET  /api/training-curves  — 获取训练/验证损失曲线
    GET  /api/raw-data         — 获取原始股票数据
    POST /api/predict          — 预测未来 n 天价格
    GET  /api/status           — 获取训练状态
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    ComparisonResponse,
    PredictionRequest,
    PredictionResponse,
    RawDataResponse,
    TestPredictionsResponse,
    TrainingCurvesResponse,
    TrainingStatus,
)
from app.services.prediction_service import prediction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["QLSTM 预测系统"])


# ──────────────────────────────────────────────
# GET /api/comparison — 模型对比指标
# ──────────────────────────────────────────────

@router.get(
    "/comparison",
    response_model=ComparisonResponse,
    summary="获取模型对比指标",
    description="返回经典 LSTM 与 QLSTM 的 MSE/RMSE/MAE/MAPE 对比及改善百分比",
)
async def get_comparison() -> ComparisonResponse:
    """获取经典 LSTM 与 QLSTM 的性能对比数据"""
    try:
        return prediction_service.get_comparison()
    except Exception as e:
        logger.error(f"获取对比指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对比指标失败: {str(e)}")


# ──────────────────────────────────────────────
# GET /api/predictions — 测试集预测结果
# ──────────────────────────────────────────────

@router.get(
    "/predictions",
    response_model=TestPredictionsResponse,
    summary="获取测试集预测结果",
    description="返回测试集上两个模型的预测值与真实值，用于对比绘图",
)
async def get_predictions() -> TestPredictionsResponse:
    """获取测试集预测结果（真实值 + 两个模型预测值）"""
    try:
        return prediction_service.get_predictions()
    except Exception as e:
        logger.error(f"获取预测结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取预测结果失败: {str(e)}")


# ──────────────────────────────────────────────
# GET /api/training-curves — 训练损失曲线
# ──────────────────────────────────────────────

@router.get(
    "/training-curves",
    response_model=TrainingCurvesResponse,
    summary="获取训练损失曲线",
    description="返回两个模型的训练/验证损失随 epoch 变化的数据",
)
async def get_training_curves() -> TrainingCurvesResponse:
    """获取训练/验证损失曲线数据"""
    try:
        return prediction_service.get_training_curves()
    except Exception as e:
        logger.error(f"获取训练曲线失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取训练曲线失败: {str(e)}")


# ──────────────────────────────────────────────
# GET /api/raw-data — 原始股票数据
# ──────────────────────────────────────────────

@router.get(
    "/raw-data",
    response_model=RawDataResponse,
    summary="获取原始股票数据",
    description="返回原始 CSV 中的日期、收盘价、成交量，供前端图表展示",
)
async def get_raw_data(days: int = 0) -> RawDataResponse:
    """获取原始股票数据（日期、收盘价、成交量）"""
    try:
        return prediction_service.get_raw_data(days=days)
    except Exception as e:
        logger.error(f"获取原始数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取原始数据失败: {str(e)}")


# ──────────────────────────────────────────────
# POST /api/predict — 预测未来价格
# ──────────────────────────────────────────────

@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="预测未来 n 天价格",
    description="使用经典 LSTM 和 QLSTM 自回归预测未来 n 天的收盘价",
)
async def predict_future(request: PredictionRequest) -> PredictionResponse:
    """预测未来 n 天价格

    Parameters
    ----------
    request : PredictionRequest
        包含起始日期和预测天数

    Returns
    -------
    PredictionResponse
        预测日期、两个模型预测值、置信度
    """
    try:
        # 将 start_date 转为 datetime
        start_dt = None
        if request.start_date is not None:
            start_dt = datetime.combine(request.start_date, datetime.min.time())

        result = prediction_service.predict_future(
            n_days=request.n_days,
            start_date=start_dt,
        )
        return PredictionResponse(**result)
    except RuntimeError as e:
        # 模型未加载等可预期错误
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"预测失败: {e}")
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")


# ──────────────────────────────────────────────
# GET /api/status — 训练状态
# ──────────────────────────────────────────────

@router.get(
    "/status",
    response_model=TrainingStatus,
    summary="获取训练状态",
    description="返回当前训练状态（idle/training/completed/error）及相关信息",
)
async def get_training_status() -> TrainingStatus:
    """获取训练状态"""
    try:
        return prediction_service.get_training_status()
    except Exception as e:
        logger.error(f"获取训练状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取训练状态失败: {str(e)}")
