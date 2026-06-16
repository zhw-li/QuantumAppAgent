"""
QLSTM 预测服务层
================
封装模型加载、预测、指标读取等核心业务逻辑，
为 API 路由层提供统一的数据访问接口。

设计要点:
    - 懒加载: 模型在首次请求时才从磁盘加载，避免启动阻塞
    - 线程安全: 使用 _lock 保证并发安全
    - 数据缓存: 训练结果 JSON / 原始数据仅读取一次并缓存
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch

# ── 项目内部导入 ──
from app.core.config import settings
from app.models.schemas import (
    ComparisonResponse,
    MetricsResponse,
    RawDataResponse,
    TestPredictionsResponse,
    TrainingCurvePoint,
    TrainingCurvesResponse,
    TrainingStatus,
)
from ml.classic_lstm import ClassicLSTM
from ml.data_loader import get_raw_data, inverse_transform_close, load_and_preprocess
from ml.qlstm import QLSTM

logger = logging.getLogger(__name__)


class PredictionService:
    """QLSTM 预测服务

    单例模式: 全局只创建一个实例，由 FastAPI lifespan 管理。
    提供模型加载、未来预测、指标对比、训练曲线、原始数据等接口。

    Attributes
    ----------
    classic_model : ClassicLSTM | None
        已加载的经典 LSTM 模型
    quantum_model : QLSTM | None
        已加载的 QLSTM 模型
    scaler : MinMaxScaler | None
        数据归一化器（训练时拟合，用于预测时反归一化）
    feature_cols : list[str] | None
        特征列名列表
    _comparison_data : dict | None
        缓存的对比结果 JSON
    _raw_data_cache : pd.DataFrame | None
        缓存的原始股票数据
    """

    def __init__(self) -> None:
        # ── 模型实例 ──
        self.classic_model: Optional[ClassicLSTM] = None
        self.quantum_model: Optional[QLSTM] = None
        self.scaler = None
        self.feature_cols: Optional[List[str]] = None

        # ── 缓存 ──
        self._comparison_data: Optional[Dict[str, Any]] = None
        self._raw_data_cache: Optional[pd.DataFrame] = None

        # ── 线程安全锁 ──
        self._lock = threading.Lock()

        # ── 模型加载状态标记 ──
        self._models_loaded = False
        self._training_status = TrainingStatus(status="idle")

    # ══════════════════════════════════════════
    #  模型加载
    # ══════════════════════════════════════════

    def load_models(self) -> None:
        """从磁盘加载训练好的模型权重及数据预处理器

        加载流程:
            1. 通过 data_loader 获取 scaler 和 feature_cols
            2. 构建 ClassicLSTM 并加载 classic_lstm.pth
            3. 构建 QLSTM 并加载 qlstm_best.pth
            4. 将模型设为 eval 模式

        注意: 如果权重文件不存在，仅记录警告，不抛异常（允许未训练时启动服务）
        """
        with self._lock:
            if self._models_loaded:
                logger.info("模型已加载，跳过重复加载")
                return

            logger.info("开始加载模型与数据预处理器...")

            # ── 1. 获取 scaler 和 feature_cols ──
            try:
                _, _, _, scaler, feature_cols = load_and_preprocess(
                    settings.DATA_PATH,
                    seq_len=settings.SEQ_LEN,
                    pred_len=1,
                    batch_size=1,
                )
                self.scaler = scaler
                self.feature_cols = feature_cols
                logger.info(f"数据预处理器加载成功，特征列: {feature_cols}")
            except Exception as e:
                logger.error(f"数据预处理器加载失败: {e}")
                return

            # ── 2. 加载经典 LSTM ──
            classic_path = Path(settings.MODEL_DIR) / "classic_lstm.pth"
            if classic_path.exists():
                try:
                    self.classic_model = ClassicLSTM(
                        n_features=settings.N_FEATURES,
                        hidden_size=settings.N_HIDDEN_CLASSIC,
                        num_layers=settings.N_LAYERS_CLASSIC,
                    )
                    state_dict = torch.load(
                        classic_path, map_location=settings.DEVICE, weights_only=True
                    )
                    self.classic_model.load_state_dict(state_dict)
                    self.classic_model.eval()
                    logger.info(f"经典 LSTM 加载成功: {classic_path}")
                except Exception as e:
                    logger.error(f"经典 LSTM 加载失败: {e}")
                    self.classic_model = None
            else:
                logger.warning(f"经典 LSTM 权重不存在: {classic_path}")

            # ── 3. 加载 QLSTM ──
            quantum_path = Path(settings.MODEL_DIR) / "qlstm_best.pth"
            if quantum_path.exists():
                try:
                    self.quantum_model = QLSTM(
                        n_features=settings.N_FEATURES,
                        n_hidden=settings.N_HIDDEN_QUANTUM,
                        n_qubits=settings.N_QUBITS,
                        n_layers=settings.N_LAYERS_QUANTUM,
                    )
                    state_dict = torch.load(
                        quantum_path, map_location=settings.DEVICE, weights_only=True
                    )
                    self.quantum_model.load_state_dict(state_dict)
                    self.quantum_model.eval()
                    logger.info(f"QLSTM 加载成功: {quantum_path}")
                except Exception as e:
                    logger.error(f"QLSTM 加载失败: {e}")
                    self.quantum_model = None
            else:
                logger.warning(f"QLSTM 权重不存在: {quantum_path}")

            self._models_loaded = True
            self._training_status = TrainingStatus(status="completed")
            logger.info("模型加载流程完成")

    # ══════════════════════════════════════════
    #  未来价格预测
    # ══════════════════════════════════════════

    def predict_future(
        self,
        n_days: int = 5,
        start_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """使用两个模型预测未来 n_days 天的收盘价

        采用自回归方式: 每一步预测值作为下一步输入的一部分，
        逐步滚动预测。技术指标（均线、RSI 等）使用简化估算。

        Parameters
        ----------
        n_days : int
            预测天数
        start_date : datetime | None
            预测起始日期，为 None 则从数据集最后一天开始

        Returns
        -------
        dict
            包含 dates, predictions_classic, predictions_quantum, confidence
        """
        if self.classic_model is None and self.quantum_model is None:
            raise RuntimeError("模型未加载，请先运行训练或检查权重文件")

        # ── 获取最新窗口数据 ──
        raw_df = self._get_raw_data()
        if start_date is None:
            start_date = raw_df["Date"].max() + timedelta(days=1)

        # 重新加载完整的预处理数据以获取归一化后的序列
        _, _, _, scaler, feature_cols = load_and_preprocess(
            settings.DATA_PATH,
            seq_len=settings.SEQ_LEN,
            pred_len=1,
            batch_size=1,
        )
        n_features = len(feature_cols)
        close_idx = list(feature_cols).index("Close")

        # 取最后 seq_len 行的归一化特征
        df = raw_df.copy()
        # 使用与 data_loader 相同的特征工程
        from ml.data_loader import _engineer_features, FEATURE_COLS
        df = _engineer_features(df)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        data_matrix = df[FEATURE_COLS].values.astype(np.float32)
        data_scaled = scaler.transform(data_matrix).astype(np.float32)

        # 取最后 seq_len 行作为初始输入
        if len(data_scaled) < settings.SEQ_LEN:
            raise ValueError(f"数据行数不足 seq_len={settings.SEQ_LEN}")

        current_window = data_scaled[-settings.SEQ_LEN:].copy()  # (seq_len, n_features)

        # ── 逐步自回归预测 ──
        classic_preds = []
        quantum_preds = []
        device = torch.device(settings.DEVICE)

        with torch.no_grad():
            for step in range(n_days):
                # 构造输入: (1, seq_len, n_features)
                x_input = torch.from_numpy(current_window).unsqueeze(0).to(device)

                # 经典 LSTM 预测
                if self.classic_model is not None:
                    pred_c = self.classic_model(x_input)  # (1, 1)
                    classic_preds.append(pred_c.item())

                # QLSTM 预测
                if self.quantum_model is not None:
                    pred_q = self.quantum_model(x_input)  # (1, 1)
                    quantum_preds.append(pred_q.item())

                # 使用经典预测值作为下一步窗口的输入（如果有）
                pred_val = classic_preds[-1] if classic_preds else quantum_preds[-1]

                # 滚动窗口: 去掉第一行，追加预测行
                # 预测行的 Close 列填入预测值，其他特征保持最后一步的值（简化）
                new_row = current_window[-1].copy()
                new_row[close_idx] = pred_val
                current_window = np.vstack([current_window[1:], new_row])

        # ── 反归一化预测值 ──
        def _inverse(preds_list: List[float]) -> List[float]:
            arr = np.array(preds_list).reshape(-1)
            recovered = inverse_transform_close(scaler, arr, feature_idx=close_idx)
            return recovered.tolist()

        classic_prices = _inverse(classic_preds) if classic_preds else []
        quantum_prices = _inverse(quantum_preds) if quantum_preds else []

        # ── 生成预测日期（跳过周末）──
        dates = []
        current_date = start_date
        while len(dates) < n_days:
            if current_date.weekday() < 5:  # 周一~周五
                dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        # ── 置信度估算（基于验证 RMSE 的启发式） ──
        comparison = self._load_comparison_data()
        confidence = 0.5  # 默认置信度
        if comparison:
            try:
                best_rmse = comparison.get("quantum_iterations", [{}])
                if best_rmse:
                    last_iter = best_rmse[-1]
                    val_loss = last_iter.get("val_losses", [1.0])
                    if isinstance(val_loss, list) and val_loss:
                        min_val = min(val_loss)
                        # 简单映射: val_loss 越小置信度越高
                        confidence = max(0.1, min(1.0, 1.0 - min_val * 10))
            except Exception:
                pass

        return {
            "dates": dates,
            "predictions_classic": classic_prices,
            "predictions_quantum": quantum_prices,
            "confidence": round(confidence, 4),
        }

    # ══════════════════════════════════════════
    #  对比指标
    # ══════════════════════════════════════════

    def get_comparison(self) -> ComparisonResponse:
        """读取对比结果 JSON，返回模型指标对比

        Returns
        -------
        ComparisonResponse
            包含经典/量子模型指标及改善百分比的响应
        """
        data = self._load_comparison_data()
        if not data:
            # 返回空响应而非报错（前端可展示"暂无数据"）
            return ComparisonResponse(
                classic_metrics=MetricsResponse(
                    model_name="Classic LSTM", mse=0, rmse=0, mae=0, mape=0
                ),
                quantum_metrics=MetricsResponse(
                    model_name="QLSTM", mse=0, rmse=0, mae=0, mape=0
                ),
                improvement_pct=0.0,
            )

        # ── 经典模型指标 ──
        c_metrics = data.get("classic", {}).get("metrics", {})
        classic_resp = MetricsResponse(
            model_name="Classic LSTM",
            mse=c_metrics.get("MSE", 0),
            rmse=c_metrics.get("RMSE", 0),
            mae=c_metrics.get("MAE", 0),
            mape=c_metrics.get("MAPE", 0),
        )

        # ── 量子模型指标（取最优迭代） ──
        q_iters = data.get("quantum_iterations", [])
        best_q = min(q_iters, key=lambda x: x.get("metrics", {}).get("RMSE", float("inf"))) if q_iters else {}
        q_metrics = best_q.get("metrics", {})
        quantum_resp = MetricsResponse(
            model_name="QLSTM",
            mse=q_metrics.get("MSE", 0),
            rmse=q_metrics.get("RMSE", 0),
            mae=q_metrics.get("MAE", 0),
            mape=q_metrics.get("MAPE", 0),
        )

        # ── 改善百分比 ──
        c_rmse = classic_resp.rmse
        q_rmse = quantum_resp.rmse
        improvement = ((c_rmse - q_rmse) / c_rmse * 100) if c_rmse > 0 else 0.0

        return ComparisonResponse(
            classic_metrics=classic_resp,
            quantum_metrics=quantum_resp,
            improvement_pct=round(improvement, 2),
            train_time_classic=data.get("classic", {}).get("train_time", 0.0),
            train_time_quantum=best_q.get("train_time", 0.0),
            quantum_iterations=len(q_iters),
            best_iteration=best_q.get("iteration", 1),
        )

    # ══════════════════════════════════════════
    #  训练曲线
    # ══════════════════════════════════════════

    def get_training_curves(self) -> TrainingCurvesResponse:
        """返回两个模型的训练/验证损失曲线

        Returns
        -------
        TrainingCurvesResponse
            classic 和 quantum 两条曲线的数据点
        """
        data = self._load_comparison_data()
        if not data:
            return TrainingCurvesResponse(classic=[], quantum=[])

        # ── 经典 LSTM 曲线 ──
        c_data = data.get("classic", {})
        classic_points = self._build_curve_points(
            c_data.get("train_losses", []),
            c_data.get("val_losses", []),
        )

        # ── QLSTM 曲线（最优迭代） ──
        q_iters = data.get("quantum_iterations", [])
        best_q = min(q_iters, key=lambda x: x.get("metrics", {}).get("RMSE", float("inf"))) if q_iters else {}
        quantum_points = self._build_curve_points(
            best_q.get("train_losses", []),
            best_q.get("val_losses", []),
        )

        return TrainingCurvesResponse(
            classic=classic_points,
            quantum=quantum_points,
        )

    # ══════════════════════════════════════════
    #  测试集预测
    # ══════════════════════════════════════════

    def get_predictions(self) -> TestPredictionsResponse:
        """返回测试集上的预测结果（用于前端对比绘图）

        Returns
        -------
        TestPredictionsResponse
            测试集日期、真实值、两个模型的预测值
        """
        data = self._load_comparison_data()
        if not data:
            return TestPredictionsResponse(
                dates=[], actuals=[], classic_predictions=[], quantum_predictions=[]
            )

        # ── 真实值 ──
        actuals = data.get("classic", {}).get("actuals", [])

        # ── 经典 LSTM 预测 ──
        classic_preds = data.get("classic", {}).get("predictions", [])

        # ── QLSTM 预测（最优迭代） ──
        q_iters = data.get("quantum_iterations", [])
        best_q = min(q_iters, key=lambda x: x.get("metrics", {}).get("RMSE", float("inf"))) if q_iters else {}
        quantum_preds = best_q.get("predictions", [])

        # ── 生成测试集日期 ──
        # 从原始数据尾部取 len(actuals) 个日期
        raw_df = self._get_raw_data()
        n_test = len(actuals)
        # 估算测试集起始位置: 总长度 * 0.85 (train 0.7 + val 0.15)
        n_total = len(raw_df)
        test_start_idx = int(n_total * 0.85)
        test_dates = raw_df["Date"].iloc[test_start_idx : test_start_idx + n_test].tolist()
        # 确保日期数量与预测一致
        test_dates_str = [d.strftime("%Y-%m-%d") if isinstance(d, pd.Timestamp) else str(d) for d in test_dates]

        # 截断或填充到一致长度
        min_len = min(len(test_dates_str), len(actuals), len(classic_preds), len(quantum_preds)) if actuals else 0

        return TestPredictionsResponse(
            dates=test_dates_str[:min_len],
            actuals=actuals[:min_len],
            classic_predictions=classic_preds[:min_len],
            quantum_predictions=quantum_preds[:min_len],
        )

    # ══════════════════════════════════════════
    #  原始数据
    # ══════════════════════════════════════════

    def get_raw_data(self, days: int = 0) -> RawDataResponse:
        """返回原始股票数据（日期、收盘价、成交量），供前端图表展示

        Parameters
        ----------
        days : int
            返回最近 days 天的数据；0 表示全部

        Returns
        -------
        RawDataResponse
            日期列表、收盘价列表、成交量列表
        """
        df = self._get_raw_data()
        if days > 0:
            df = df.tail(days)
        dates = df["Date"].tolist()
        dates_str = [
            d.strftime("%Y-%m-%d") if isinstance(d, pd.Timestamp) else str(d)
            for d in dates
        ]
        return RawDataResponse(
            dates=dates_str,
            close=df["Close"].tolist(),
            volume=df["Volume"].tolist(),
            open=df["Open"].tolist() if "Open" in df.columns else [],
            high=df["High"].tolist() if "High" in df.columns else [],
            low=df["Low"].tolist() if "Low" in df.columns else [],
        )

    # ══════════════════════════════════════════
    #  训练状态
    # ══════════════════════════════════════════

    def get_training_status(self) -> TrainingStatus:
        """获取当前训练状态

        当前版本仅返回已完成/空闲状态，
        未来可扩展为从训练进程实时读取。

        Returns
        -------
        TrainingStatus
            训练状态信息
        """
        # 尝试从对比结果推断训练状态
        data = self._load_comparison_data()
        if data:
            c_data = data.get("classic", {})
            q_iters = data.get("quantum_iterations", [])

            if c_data and q_iters:
                # 取最后一次迭代的最终状态
                last_q = q_iters[-1]
                train_losses = last_q.get("train_losses", [])
                val_losses = last_q.get("val_losses", [])
                return TrainingStatus(
                    status="completed",
                    epoch=len(train_losses),
                    total_epochs=len(train_losses),
                    train_loss=train_losses[-1] if train_losses else 0.0,
                    val_loss=val_losses[-1] if val_losses else 0.0,
                    model_name="QLSTM",
                )

        return self._training_status

    # ══════════════════════════════════════════
    #  内部工具方法
    # ══════════════════════════════════════════

    def _load_comparison_data(self) -> Optional[Dict[str, Any]]:
        """从磁盘读取对比结果 JSON（带缓存）

        Returns
        -------
        dict | None
            对比结果数据，文件不存在时返回 None
        """
        if self._comparison_data is not None:
            return self._comparison_data

        result_path = Path(settings.RESULT_DIR) / "comparison_results.json"
        if not result_path.exists():
            logger.warning(f"对比结果文件不存在: {result_path}")
            return None

        try:
            with open(result_path, "r", encoding="utf-8") as f:
                self._comparison_data = json.load(f)
            logger.info(f"对比结果加载成功: {result_path}")
            return self._comparison_data
        except Exception as e:
            logger.error(f"对比结果加载失败: {e}")
            return None

    def _get_raw_data(self) -> pd.DataFrame:
        """获取原始股票数据（带缓存）

        Returns
        -------
        pd.DataFrame
            原始股票数据，含 Date, Close, Volume 列
        """
        if self._raw_data_cache is not None:
            return self._raw_data_cache

        try:
            self._raw_data_cache = get_raw_data(settings.DATA_PATH)
            return self._raw_data_cache
        except Exception as e:
            logger.error(f"原始数据加载失败: {e}")
            # 返回空 DataFrame 以防报错
            return pd.DataFrame(columns=["Date", "Close", "Volume"])

    @staticmethod
    def _build_curve_points(
        train_losses: List[float],
        val_losses: List[float],
    ) -> List[TrainingCurvePoint]:
        """将损失列表转换为 TrainingCurvePoint 列表

        Parameters
        ----------
        train_losses : list[float]
            每轮训练损失
        val_losses : list[float]
            每轮验证损失

        Returns
        -------
        list[TrainingCurvePoint]
        """
        points = []
        n = min(len(train_losses), len(val_losses))
        for i in range(n):
            points.append(
                TrainingCurvePoint(
                    epoch=i + 1,
                    train_loss=round(train_losses[i], 6),
                    val_loss=round(val_losses[i], 6),
                )
            )
        return points

    def invalidate_cache(self) -> None:
        """手动清除缓存（重新训练后调用）"""
        self._comparison_data = None
        self._raw_data_cache = None
        self._models_loaded = False
        logger.info("缓存已清除")


# ── 全局服务实例（由 main.py lifespan 初始化） ──
prediction_service = PredictionService()
