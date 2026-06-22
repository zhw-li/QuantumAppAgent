"""
业务逻辑服务层
- 封装训练、预测、数据查询等核心业务
- 管理结果缓存
- 统一响应格式（字段名大写）
"""

import os
import sys
import threading
import traceback

# 确保ml模块可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.train_pipeline import run_training, load_results, RESULTS_DIR
from ml.data_loader import get_raw_data, AVAILABLE_STOCKS
from ml.qlstm import QLSTM
from ml.classic_lstm import ClassicLSTM


class PredictionService:
    """预测服务：管理训练、结果缓存、数据查询"""

    def __init__(self):
        # 内存缓存：stock → results dict
        self._cache = {}
        # 训练状态锁（防止并发训练同一股票）
        self._training_lock = threading.Lock()
        # 当前训练状态
        self._training_status = {}

    def get_results(self, stock: str) -> dict | None:
        """获取训练结果（优先内存缓存，其次磁盘）

        Args:
            stock: 股票代码

        Returns:
            结果字典或None
        """
        # 先查内存缓存
        if stock in self._cache:
            return self._cache[stock]

        # 再查磁盘
        results = load_results(stock)
        if results is not None:
            self._cache[stock] = results
        return results

    def train(self, request: dict) -> dict:
        """执行训练

        Args:
            request: 训练请求参数

        Returns:
            训练结果字典
        """
        stock = request.get("stock", "AAPL")

        with self._training_lock:
            self._training_status[stock] = "training"

        try:
            results = run_training(
                stock=stock,
                seq_len=request.get("seq_len", 20),
                hidden_size=request.get("hidden_size", 8),
                n_qubits=request.get("n_qubits", 4),
                qlstm_epochs=request.get("qlstm_epochs", 30),
                lstm_epochs=request.get("lstm_epochs", 50),
                seed=42,
            )

            # 更新缓存
            self._cache[stock] = results

            with self._training_lock:
                self._training_status[stock] = "completed"

            return results

        except Exception as e:
            with self._training_lock:
                self._training_status[stock] = f"failed: {str(e)}"
            traceback.print_exc()
            raise

    def get_comparison(self, stock: str = "AAPL") -> dict | None:
        """获取对比结果

        Args:
            stock: 股票代码

        Returns:
            对比数据字典，包含 QLSTM, LSTM, improvement（字段名大写）
        """
        results = self.get_results(stock)
        if results is None:
            return None

        return {
            "QLSTM": {
                "RMSE": results["QLSTM_metrics"]["RMSE"],
                "MAE": results["QLSTM_metrics"]["MAE"],
                "MAPE": results["QLSTM_metrics"]["MAPE"],
                "params": results["QLSTM_params"],
            },
            "LSTM": {
                "RMSE": results["LSTM_metrics"]["RMSE"],
                "MAE": results["LSTM_metrics"]["MAE"],
                "MAPE": results["LSTM_metrics"]["MAPE"],
                "params": results["LSTM_params"],
            },
            "improvement": results["improvement"],
        }

    def get_predictions(self, stock: str = "AAPL") -> dict | None:
        """获取预测曲线数据

        Args:
            stock: 股票代码

        Returns:
            {dates, actual, QLSTM, LSTM}（字段名大写）
        """
        results = self.get_results(stock)
        if results is None:
            return None

        return {
            "dates": results["dates_test"],
            "actual": results["actual_test"],
            "QLSTM": results["QLSTM_predictions"],
            "LSTM": results["LSTM_predictions"],
        }

    def get_training_curves(self, stock: str = "AAPL") -> dict | None:
        """获取训练损失曲线

        Args:
            stock: 股票代码

        Returns:
            {QLSTM: [...], LSTM: [...]}（字段名大写）
        """
        results = self.get_results(stock)
        if results is None:
            return None

        return {
            "QLSTM": results["QLSTM_train_losses"],
            "LSTM": results["LSTM_train_losses"],
        }

    def get_raw_stock_data(self, stock: str = "AAPL", days: int = 365) -> dict:
        """获取原始股票数据（K线图）

        Args:
            stock: 股票代码
            days: 天数

        Returns:
            {dates, OHLC, volume}（字段名大写）
        """
        return get_raw_data(stock, days)

    def get_stocks(self) -> list:
        """获取可用股票列表"""
        return AVAILABLE_STOCKS

    def get_model_info(self, hidden_size: int = 8, n_qubits: int = 4) -> dict:
        """获取模型架构信息

        Args:
            hidden_size: 隐藏层维度
            n_qubits: 量子比特数

        Returns:
            {QLSTM: {...}, LSTM: {...}}（字段名大写）
        """
        # QLSTM信息
        qlstm_model = QLSTM(
            input_size=6,
            hidden_size=hidden_size,
            n_qubits=n_qubits,
            layers=2,
            num_layers=1,
        )
        qlstm_params = qlstm_model.count_parameters()

        # LSTM信息
        lstm_model = ClassicLSTM(
            input_size=6,
            hidden_size=hidden_size,
            num_layers=1,
        )
        lstm_params = lstm_model.count_parameters()

        return {
            "QLSTM": {
                "n_qubits": n_qubits,
                "layers": 2,
                "hidden_size": hidden_size,
                "total_params": qlstm_params,
            },
            "LSTM": {
                "hidden_size": hidden_size,
                "num_layers": 1,
                "total_params": lstm_params,
            },
        }

    def clear_cache(self, stock: str = None):
        """清除缓存

        Args:
            stock: 指定股票则只清除该股票缓存，None则清除全部
        """
        if stock:
            self._cache.pop(stock, None)
        else:
            self._cache.clear()


# 全局服务实例
prediction_service = PredictionService()
