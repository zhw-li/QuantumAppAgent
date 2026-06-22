"""
QLSTM股票预测FastAPI应用
- 7个API端点
- 启动时自动训练默认股票（如无缓存结果）
- 端口：8007
"""

import sys
import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 确保项目根目录在sys.path中
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.api.routes import router
from app.core.config import settings
from app.services.prediction_service import prediction_service
from ml.train_pipeline import load_results


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时自动训练默认股票"""
    print("=" * 60)
    print("QLSTM 股票预测平台启动中...")
    print("=" * 60)

    # 检查是否有已保存的默认结果
    default_stock = settings.DEFAULT_STOCK
    existing = load_results(default_stock)

    if existing is not None:
        # 从磁盘加载缓存
        prediction_service._cache[default_stock] = existing
        print(f"已加载 {default_stock} 的训练结果缓存")
    else:
        # 无缓存结果，启动时自动训练默认股票
        print(f"未找到 {default_stock} 的训练结果，启动自动训练...")
        try:
            # 使用后台线程执行训练，不阻塞启动
            import threading

            def _train_default():
                try:
                    prediction_service.train({
                        "stock": default_stock,
                        "seq_len": settings.DEFAULT_SEQ_LEN,
                        "hidden_size": settings.DEFAULT_HIDDEN_SIZE,
                        "n_qubits": settings.DEFAULT_N_QUBITS,
                        "qlstm_epochs": settings.DEFAULT_QLSTM_EPOCHS,
                        "lstm_epochs": settings.DEFAULT_LSTM_EPOCHS,
                    })
                    print(f"\n✓ {default_stock} 自动训练完成！")
                except Exception as e:
                    print(f"\n✗ {default_stock} 自动训练失败: {e}")

            train_thread = threading.Thread(target=_train_default, daemon=True)
            train_thread.start()
        except Exception as e:
            print(f"自动训练启动失败: {e}")

    yield

    # 关闭时清理
    print("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="QLSTM 股票预测平台",
    description="基于量子长短期记忆网络（QLSTM）的股票价格预测，对比经典LSTM",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "app": "QLSTM Stock Prediction",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/train",
            "GET /api/comparison",
            "GET /api/predictions",
            "GET /api/training-curves",
            "GET /api/raw-data",
            "GET /api/stocks",
            "GET /api/model-info",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=False)
