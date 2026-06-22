"""
API路由定义
- 7个端点：训练、对比、预测曲线、训练曲线、原始数据、股票列表、模型信息
- 所有响应字段名使用大写（RMSE, MAE, MAPE, QLSTM, LSTM, OHLC）
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

from app.models.schemas import (
    TrainRequest,
    TrainResponse,
    MetricsModel,
    ComparisonResponse,
    PredictionsResponse,
    TrainingCurvesResponse,
    RawDataResponse,
    StocksResponse,
    ModelInfoResponse,
)
from app.services.prediction_service import prediction_service

router = APIRouter(prefix="/api", tags=["QLSTM Stock Prediction"])


@router.post("/train", response_model=TrainResponse)
async def train_models(request: TrainRequest, background_tasks: BackgroundTasks = None):
    """训练QLSTM和Classic LSTM模型

    同步执行训练，返回完整结果。
    """
    try:
        results = prediction_service.train(request.model_dump())
        return TrainResponse(
            status="success",
            message=f"训练完成: {request.stock}",
            QLSTM_metrics=MetricsModel(**results["QLSTM_metrics"]),
            LSTM_metrics=MetricsModel(**results["LSTM_metrics"]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"训练失败: {str(e)}")


@router.get("/comparison", response_model=ComparisonResponse)
async def get_comparison(stock: str = "AAPL"):
    """获取QLSTM vs LSTM对比结果"""
    data = prediction_service.get_comparison(stock)
    if data is None:
        raise HTTPException(status_code=404, detail=f"未找到 {stock} 的训练结果，请先训练")
    return data


@router.get("/predictions", response_model=PredictionsResponse)
async def get_predictions(stock: str = "AAPL"):
    """获取预测曲线数据"""
    data = prediction_service.get_predictions(stock)
    if data is None:
        raise HTTPException(status_code=404, detail=f"未找到 {stock} 的预测结果，请先训练")
    return data


@router.get("/training-curves", response_model=TrainingCurvesResponse)
async def get_training_curves(stock: str = "AAPL"):
    """获取训练损失曲线"""
    data = prediction_service.get_training_curves(stock)
    if data is None:
        raise HTTPException(status_code=404, detail=f"未找到 {stock} 的训练曲线，请先训练")
    return data


@router.get("/raw-data", response_model=RawDataResponse)
async def get_raw_data(stock: str = "AAPL", days: int = 365):
    """获取原始股票数据（K线图）"""
    try:
        data = prediction_service.get_raw_stock_data(stock, days)
        return data
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stocks", response_model=StocksResponse)
async def get_stocks():
    """获取可用股票列表"""
    return {"stocks": prediction_service.get_stocks()}


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info(hidden_size: int = 8, n_qubits: int = 4):
    """获取模型架构信息"""
    return prediction_service.get_model_info(hidden_size, n_qubits)
