"""
QLSTM 时间序列预测系统 — FastAPI 应用入口
==========================================
功能:
    - 创建 FastAPI 实例
    - 配置 CORS（开发环境允许所有来源）
    - 注册 API 路由
    - Lifespan 事件: 启动时预加载模型
    - 健康检查端点

启动方式:
    开发: python main.py
    生产: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.services.prediction_service import prediction_service

# ── 日志配置 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════
#  Lifespan — 应用生命周期管理
# ══════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动时加载模型，关闭时释放资源"""
    # ── 启动阶段 ──
    logger.info("=" * 60)
    logger.info("🚀 QLSTM 预测系统启动中...")
    logger.info(f"   数据路径: {settings.DATA_PATH}")
    logger.info(f"   结果目录: {settings.RESULT_DIR}")
    logger.info(f"   模型目录: {settings.MODEL_DIR}")
    logger.info(f"   监听地址: {settings.HOST}:{settings.PORT}")
    logger.info("=" * 60)

    # 预加载模型（如权重存在则加载，否则仅记录警告）
    try:
        prediction_service.load_models()
        logger.info("✅ 模型预加载完成")
    except Exception as e:
        logger.warning(f"⚠️ 模型预加载失败（服务仍可启动）: {e}")

    yield  # 应用运行中...

    # ── 关闭阶段 ──
    logger.info("🔄 QLSTM 预测系统关闭")
    # 清除缓存
    prediction_service.invalidate_cache()


# ══════════════════════════════════════════════
#  创建 FastAPI 实例
# ══════════════════════════════════════════════

app = FastAPI(
    title="QLSTM 时序预测系统",
    description=(
        "量子长短期记忆网络 (QLSTM) 股票价格时序预测系统 API\n\n"
        "## 功能\n"
        "- 📊 经典 LSTM 与 QLSTM 模型对比\n"
        "- 🔮 未来价格预测\n"
        "- 📈 训练曲线可视化\n"
        "- 📋 测试集预测结果\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── CORS 中间件（开发环境允许所有来源）──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 开发环境允许所有来源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],          # 允许所有 HTTP 方法
    allow_headers=["*"],          # 允许所有请求头
)


# ── 注册路由 ──
app.include_router(router)


# ══════════════════════════════════════════════
#  健康检查端点
# ══════════════════════════════════════════════

@app.get("/", tags=["系统"])
async def root():
    """根路径 — 健康检查"""
    return {
        "service": "QLSTM 时序预测系统",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "models_loaded": prediction_service._models_loaded,
    }


# ══════════════════════════════════════════════
#  直接运行入口
# ══════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,       # 开发模式: 文件变更自动重载
        log_level="info",
    )
