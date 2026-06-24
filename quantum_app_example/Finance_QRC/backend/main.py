"""
Finance QRC FastAPI 后端服务

量子储备池计算 (QRC) vs 经典储备池计算 (Classic RC) 股票价格预测平台
端口: 8009
"""

import os
import sys
import json
import time
import numpy as np
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import DOW10_TICKERS, StockDataset, download_stock_data
from qrc_model import QuantumRC, ClassicRC, compute_metrics

# 项目路径
_PROJECT_ROOT = os.environ.get(
    "FINANCE_QRC_ROOT",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_CACHE_DIR = os.path.join(_PROJECT_ROOT, "data", "cache")
RESULTS_DIR = os.path.join(_PROJECT_ROOT, "artifacts", "results")

# 确保目录存在
os.makedirs(DATA_CACHE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ========== 全局缓存 ==========
# 实验结果缓存: key = f"{ticker}_{n_qubits}_{depth}_{window}_{n_reservoir}_{spectral_radius}_{ridge_alpha}_{seed}"
results_cache: Dict[str, dict] = {}

# 股票数据缓存: {ticker: StockDataset} (window_size 不同时重建)
dataset_cache: Dict[str, StockDataset] = {}

# OHLCV 原始数据缓存: {ticker: DataFrame-like dict}
ohlcv_cache: Dict[str, dict] = {}


# ========== Pydantic 模型 ==========

class SolveRequest(BaseModel):
    ticker: str = "AAPL"
    n_qubits: int = 4
    depth: int = 2
    window_size: int = 5
    n_reservoir: int = 100
    spectral_radius: float = 0.9
    ridge_alpha: float = 1.0
    seed: int = 42
    force: bool = False


class ParamsResponse(BaseModel):
    n_qubits: Dict[str, Any]
    depth: Dict[str, Any]
    window_size: Dict[str, Any]
    n_reservoir: Dict[str, Any]
    spectral_radius: Dict[str, Any]
    ridge_alpha: Dict[str, Any]


# ========== 辅助函数 ==========

def _cache_key(ticker: str, n_qubits: int, depth: int, window_size: int,
               n_reservoir: int, spectral_radius: float, ridge_alpha: float,
               seed: int) -> str:
    """生成结果缓存键"""
    return f"{ticker}_{n_qubits}_{depth}_{window_size}_{n_reservoir}_{spectral_radius}_{ridge_alpha}_{seed}"


def _get_dataset(ticker: str, window_size: int = 5) -> StockDataset:
    """获取股票数据集 (带缓存)"""
    cache_key = f"{ticker}_w{window_size}"
    if cache_key in dataset_cache:
        return dataset_cache[cache_key]

    # 下载收盘价数据
    data = download_stock_data(
        [ticker], start="2023-01-01", end="2025-01-01",
        save_dir=DATA_CACHE_DIR
    )
    if ticker not in data:
        raise ValueError(f"无法下载 {ticker} 的数据")

    ds = StockDataset(data[ticker], window_size=window_size, train_ratio=0.8)
    dataset_cache[cache_key] = ds
    return ds


def _get_ohlcv_data(ticker: str, days: int = 365) -> dict:
    """获取 OHLCV 原始数据 (带缓存)"""
    cache_key = f"{ticker}_ohlcv"
    if cache_key in ohlcv_cache:
        raw = ohlcv_cache[cache_key]
        # 截取最近 days 天
        n = min(days, len(raw["dates"]))
        return {
            "ticker": ticker,
            "dates": raw["dates"][-n:],
            "close": raw["close"][-n:],
            "volume": raw["volume"][-n:],
            "open": raw["open"][-n:],
            "high": raw["high"][-n:],
            "low": raw["low"][-n:],
        }

    # 下载 OHLCV 数据
    import yfinance as yf
    raw_df = yf.download(ticker, start="2023-01-01", end="2025-01-01")

    if raw_df.empty:
        raise ValueError(f"无法下载 {ticker} 的 OHLCV 数据")

    # yfinance 返回 MultiIndex columns 的情况处理
    if hasattr(raw_df.columns, 'levels') and len(raw_df.columns.levels) > 1:
        raw_df = raw_df.xs(ticker, axis=1, level=1) if ticker in raw_df.columns.get_level_values(1) else raw_df.iloc[:, :6]

    dates = [str(d.date()) if hasattr(d, 'date') else str(d) for d in raw_df.index]

    # 处理 NaN
    close = raw_df['Close'].values.astype(float).tolist()
    volume = raw_df['Volume'].values.astype(float).tolist()
    open_vals = raw_df['Open'].values.astype(float).tolist()
    high = raw_df['High'].values.astype(float).tolist()
    low = raw_df['Low'].values.astype(float).tolist()

    ohlcv_data = {
        "dates": dates,
        "close": close,
        "volume": volume,
        "open": open_vals,
        "high": high,
        "low": low,
    }
    ohlcv_cache[cache_key] = ohlcv_data

    n = min(days, len(dates))
    return {
        "ticker": ticker,
        "dates": dates[-n:],
        "close": close[-n:],
        "volume": volume[-n:],
        "open": open_vals[-n:],
        "high": high[-n:],
        "low": low[-n:],
    }


def _run_experiment(ticker: str, n_qubits: int, depth: int, window_size: int,
                    n_reservoir: int, spectral_radius: float, ridge_alpha: float,
                    seed: int) -> dict:
    """运行 QRC vs ClassicRC 实验"""
    # 获取数据集
    ds = _get_dataset(ticker, window_size=window_size)
    X_train, y_train = ds.X_train, ds.y_train
    X_test, y_test = ds.X_test, ds.y_test
    y_test_raw = ds.y_test_raw

    # 测试集日期 (基于原始价格序列索引)
    # 原始价格: len(ds.raw_prices) = n_samples + window_size + target_offset
    # test 起始在 (len(X) * 0.8) + window_size 处
    total_windows = len(ds.X_train) + len(ds.X_test)
    test_start_idx = len(ds.X_train) + window_size
    test_dates = []
    for i in range(len(ds.X_test)):
        idx = test_start_idx + i
        if idx < len(ds.raw_prices):
            test_dates.append(str(idx))  # 用索引作为占位，后续可能替换

    result = {
        "ticker": ticker,
        "params": {
            "n_qubits": n_qubits,
            "depth": depth,
            "window_size": window_size,
            "n_reservoir": n_reservoir,
            "spectral_radius": spectral_radius,
            "ridge_alpha": ridge_alpha,
            "seed": seed,
        },
    }

    # ===== Classic RC =====
    try:
        crc = ClassicRC(
            n_reservoir=n_reservoir,
            spectral_radius=spectral_radius,
            sparsity=0.1,
            input_scaling=1.0,
            ridge_alpha=ridge_alpha,
            seed=seed,
            use_nonlinear_features=True,
        )
        t0 = time.time()
        crc.fit(X_train, y_train)
        crc_train_time = time.time() - t0

        y_pred_crc_scaled = crc.predict(X_test)
        y_pred_crc = ds.inverse_transform_y(y_pred_crc_scaled)
        crc_metrics = compute_metrics(y_test_raw, y_pred_crc)

        result["classic"] = {
            "RMSE": crc_metrics["RMSE"],
            "MAE": crc_metrics["MAE"],
            "MAPE": crc_metrics["MAPE"],
            "train_time": round(crc_train_time, 4),
            "n_params": int(crc.n_params),
            "predictions": y_pred_crc.tolist(),
            "actual": y_test_raw.tolist(),
            "dates": test_dates,
        }
    except Exception as e:
        print(f"[错误] ClassicRC 失败 ({ticker}): {e}")
        result["classic"] = {"error": str(e)}

    # ===== Quantum RC =====
    try:
        qrc = QuantumRC(
            n_qubits=n_qubits,
            reservoir_depth=depth,
            ridge_alpha=ridge_alpha,
            seed=seed,
            use_nonlinear_features=True,
        )
        t0 = time.time()
        qrc.fit(X_train, y_train)
        qrc_train_time = time.time() - t0

        y_pred_qrc_scaled = qrc.predict(X_test)
        y_pred_qrc = ds.inverse_transform_y(y_pred_qrc_scaled)
        qrc_metrics = compute_metrics(y_test_raw, y_pred_qrc)

        result["quantum"] = {
            "RMSE": qrc_metrics["RMSE"],
            "MAE": qrc_metrics["MAE"],
            "MAPE": qrc_metrics["MAPE"],
            "train_time": round(qrc_train_time, 4),
            "n_params": int(qrc.n_params),
            "predictions": y_pred_qrc.tolist(),
            "actual": y_test_raw.tolist(),
            "dates": test_dates,
        }
    except Exception as e:
        print(f"[错误] QuantumRC 失败 ({ticker}): {e}")
        import traceback
        traceback.print_exc()
        result["quantum"] = {"error": str(e)}

    # ===== 比较 =====
    if "classic" in result and "quantum" in result:
        if "error" not in result["classic"] and "error" not in result["quantum"]:
            crc_rmse = result["classic"]["RMSE"]
            qrc_rmse = result["quantum"]["RMSE"]
            crc_mae = result["classic"]["MAE"]
            qrc_mae = result["quantum"]["MAE"]
            crc_mape = result["classic"]["MAPE"]
            qrc_mape = result["quantum"]["MAPE"]

            rmse_imp = ((crc_rmse - qrc_rmse) / crc_rmse * 100) if crc_rmse > 0 else 0.0
            mae_imp = ((crc_mae - qrc_mae) / crc_mae * 100) if crc_mae > 0 else 0.0
            mape_imp = ((crc_mape - qrc_mape) / crc_mape * 100) if crc_mape > 0 else 0.0

            classic_params = result["classic"]["n_params"]
            quantum_params = result["quantum"]["n_params"]
            param_eff = ((classic_params - quantum_params) / classic_params * 100) if classic_params > 0 else 0.0

            result["comparison"] = {
                "rmse_improvement": round(rmse_imp, 2),
                "mae_improvement": round(mae_imp, 2),
                "mape_improvement": round(mape_imp, 2),
                "param_efficiency": round(param_eff, 2),
                "quantum_wins": rmse_imp > 0,
            }

    return result


# ========== FastAPI 应用 ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动时预加载默认数据"""
    print("[Finance-QRC] 服务启动, 预加载 AAPL 数据...")
    try:
        _get_dataset("AAPL", window_size=5)
        print("[Finance-QRC] AAPL 数据预加载成功")
    except Exception as e:
        print(f"[Finance-QRC] AAPL 预加载失败 (非致命): {e}")
    yield
    print("[Finance-QRC] 服务关闭")


app = FastAPI(
    title="Finance QRC API",
    description="量子储备池计算 vs 经典储备池计算 - 股票价格预测平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== API 端点 ==========

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "finance-qrc"}


@app.get("/api/stocks")
async def list_stocks():
    """列出可用股票"""
    return {
        "stocks": DOW10_TICKERS,
        "default": "AAPL",
    }


@app.get("/api/params")
async def get_params():
    """获取默认参数和范围"""
    return {
        "n_qubits": {"default": 4, "options": [4, 6, 8]},
        "depth": {"default": 2, "options": [2, 3]},
        "window_size": {"default": 5, "options": [5, 10, 20]},
        "n_reservoir": {"default": 100, "min": 50, "max": 500},
        "spectral_radius": {"default": 0.9, "min": 0.1, "max": 0.99},
        "ridge_alpha": {"default": 1.0, "min": 0.01, "max": 100.0},
    }


@app.post("/api/solve")
async def solve(req: SolveRequest):
    """运行 QRC vs ClassicRC 对比实验"""
    key = _cache_key(
        req.ticker, req.n_qubits, req.depth, req.window_size,
        req.n_reservoir, req.spectral_radius, req.ridge_alpha, req.seed,
    )

    # 检查缓存
    if not req.force and key in results_cache:
        print(f"[缓存] 命中: {key}")
        return results_cache[key]

    # 验证股票代码
    if req.ticker not in DOW10_TICKERS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的股票代码: {req.ticker}, 可用: {DOW10_TICKERS}"
        )

    # 运行实验
    print(f"[求解] 开始: {key}")
    try:
        result = _run_experiment(
            ticker=req.ticker,
            n_qubits=req.n_qubits,
            depth=req.depth,
            window_size=req.window_size,
            n_reservoir=req.n_reservoir,
            spectral_radius=req.spectral_radius,
            ridge_alpha=req.ridge_alpha,
            seed=req.seed,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"实验运行失败: {str(e)}")

    # 缓存结果
    results_cache[key] = result

    # 持久化到磁盘
    result_file = os.path.join(RESULTS_DIR, f"{key}.json")
    try:
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[警告] 结果保存失败: {e}")

    return result


@app.get("/api/result/{ticker}")
async def get_result(ticker: str):
    """获取已缓存的股票结果"""
    # 在缓存中查找该 ticker 的最新结果
    matched = {k: v for k, v in results_cache.items() if v.get("ticker") == ticker}

    if not matched:
        # 尝试从磁盘加载
        for fname in os.listdir(RESULTS_DIR):
            if fname.startswith(ticker) and fname.endswith(".json"):
                try:
                    with open(os.path.join(RESULTS_DIR, fname), 'r') as f:
                        r = json.load(f)
                    if r.get("ticker") == ticker:
                        key = fname[:-5]
                        results_cache[key] = r
                        matched[key] = r
                except Exception:
                    pass

    if not matched:
        raise HTTPException(status_code=404, detail=f"未找到 {ticker} 的结果，请先通过 /api/solve 运行实验")

    # 返回第一个匹配结果
    return list(matched.values())[0]


@app.get("/api/compare")
async def compare_results():
    """比较所有已缓存股票的结果"""
    # 从缓存收集所有唯一 ticker 的结果
    seen_tickers = set()
    stock_results = []

    for key, result in results_cache.items():
        ticker = result.get("ticker")
        if ticker in seen_tickers:
            continue
        seen_tickers.add(ticker)

        classic = result.get("classic", {})
        quantum = result.get("quantum", {})
        comparison = result.get("comparison", {})

        if "error" in classic or "error" in quantum:
            continue

        stock_results.append({
            "ticker": ticker,
            "classic_rmse": classic.get("RMSE", 0),
            "quantum_rmse": quantum.get("RMSE", 0),
            "improvement": comparison.get("rmse_improvement", 0),
            "quantum_wins": comparison.get("quantum_wins", False),
        })

    # 如果没有缓存结果，也尝试从磁盘加载
    if not stock_results:
        for fname in os.listdir(RESULTS_DIR):
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(RESULTS_DIR, fname), 'r') as f:
                    r = json.load(f)
                ticker = r.get("ticker")
                if ticker and ticker not in seen_tickers:
                    seen_tickers.add(ticker)
                    classic = r.get("classic", {})
                    quantum = r.get("quantum", {})
                    comparison = r.get("comparison", {})
                    if "error" not in classic and "error" not in quantum:
                        stock_results.append({
                            "ticker": ticker,
                            "classic_rmse": classic.get("RMSE", 0),
                            "quantum_rmse": quantum.get("RMSE", 0),
                            "improvement": comparison.get("rmse_improvement", 0),
                            "quantum_wins": comparison.get("quantum_wins", False),
                        })
            except Exception:
                pass

    # 汇总统计
    if stock_results:
        classic_rmses = [s["classic_rmse"] for s in stock_results]
        quantum_rmses = [s["quantum_rmse"] for s in stock_results]
        improvements = [s["improvement"] for s in stock_results]
        quantum_wins_count = sum(1 for s in stock_results if s["quantum_wins"])

        summary = {
            "total_stocks": len(stock_results),
            "quantum_wins": quantum_wins_count,
            "avg_classic_rmse": round(float(np.mean(classic_rmses)), 2),
            "avg_quantum_rmse": round(float(np.mean(quantum_rmses)), 2),
            "avg_improvement": round(float(np.mean(improvements)), 2),
        }
    else:
        summary = {
            "total_stocks": 0,
            "quantum_wins": 0,
            "avg_classic_rmse": 0,
            "avg_quantum_rmse": 0,
            "avg_improvement": 0,
        }

    return {"stocks": stock_results, "summary": summary}


@app.get("/api/circuit")
async def get_circuit_info(
    n_qubits: int = Query(4, description="量子比特数"),
    depth: int = Query(2, description="储备池深度"),
):
    """获取量子储备池电路信息"""
    try:
        # 创建 QuantumRC 实例以获取电路信息
        # 需要先初始化 (需要 input_dim，用 window_size=5 作为默认)
        qrc = QuantumRC(n_qubits=n_qubits, reservoir_depth=depth, seed=42)
        # 手动初始化 (用默认 window_size=5)
        qrc._initialize(input_dim=5)

        # 统计门数量
        gate_counts = {"ry": 0, "rz": 0, "cx": 0, "measure": 0}

        # 输入编码 RY: n_qubits 个
        gate_counts["ry"] += n_qubits

        # 储备池层: depth × (RY + RZ per qubit + CNOT ring)
        for layer in range(depth):
            gate_counts["ry"] += n_qubits   # RY per qubit per layer
            gate_counts["rz"] += n_qubits   # RZ per qubit per layer
            gate_counts["cx"] += n_qubits   # CNOT ring per layer

        # 测量: n_qubits
        gate_counts["measure"] = n_qubits

        # 构建一个示例电路获取 QCIS
        input_angles = np.random.uniform(0, np.pi, size=n_qubits)
        circuit = qrc._build_circuit(input_angles)
        circuit.measure_all()

        # 尝试转换为 QCIS
        qcis_str = ""
        try:
            from cqlib.transpiler import transpile_qcis
            qcis_str = transpile_qcis(circuit)
        except Exception:
            # 如果 transpile 不可用，用 circuit 字符串表示
            qcis_str = str(circuit)

        # 计算电路深度 (近似)
        circuit_depth = 1 + depth * 3  # input_ry(1) + depth × (ry + rz + cnot_layer)

        return {
            "n_qubits": n_qubits,
            "depth": depth,
            "n_parameters": qrc.count_circuit_params(),
            "gate_counts": gate_counts,
            "circuit_depth": circuit_depth,
            "qcis": qcis_str,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"电路信息获取失败: {str(e)}")


@app.get("/api/reservoir-states")
async def get_reservoir_states(
    ticker: str = Query("AAPL", description="股票代码"),
    n_qubits: int = Query(4, description="量子比特数"),
    depth: int = Query(2, description="储备池深度"),
    window_size: int = Query(5, description="滑动窗口大小"),
    n_samples: int = Query(50, description="采样数量"),
):
    """获取储备池状态可视化数据"""
    try:
        ds = _get_dataset(ticker, window_size=window_size)
        X_test = ds.X_test
        n_samples = min(n_samples, len(X_test))

        # ===== Quantum Reservoir States =====
        qrc = QuantumRC(n_qubits=n_qubits, reservoir_depth=depth, seed=42,
                        use_nonlinear_features=True)
        # 先 fit 以初始化参数
        qrc._initialize(input_dim=X_test.shape[1])

        quantum_states = []
        for i in range(n_samples):
            x_flat = X_test[i].flatten()
            state = qrc._get_reservoir_state(x_flat)
            # 取前 n_qubits 维 (Pauli-Z 期望值)
            quantum_states.append(state[:n_qubits].tolist())

        # ===== Classic Reservoir States =====
        crc = ClassicRC(n_reservoir=100, seed=42, spectral_radius=0.9,
                        use_nonlinear_features=True)
        crc._initialize(input_dim=X_test.shape[1])

        classic_states = []
        for i in range(n_samples):
            x_flat = X_test[i].flatten()
            state = crc._get_reservoir_state(x_flat)
            # 取前 n_qubits 维便于可视化对比
            classic_states.append(state[:n_qubits].tolist())

        # 输入值 (原始价格)
        input_values = []
        y_test_raw = ds.y_test_raw
        for i in range(n_samples):
            if i < len(y_test_raw):
                input_values.append(float(y_test_raw[i]))

        return {
            "ticker": ticker,
            "quantum_states": quantum_states,
            "classic_states": classic_states,
            "input_values": input_values,
            "n_qubits": n_qubits,
            "n_reservoir_nodes": 100,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"储备池状态获取失败: {str(e)}")


@app.get("/api/raw-data/{ticker}")
async def get_raw_data(
    ticker: str,
    days: int = Query(365, description="天数"),
):
    """获取原始股票数据"""
    if ticker not in DOW10_TICKERS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的股票代码: {ticker}, 可用: {DOW10_TICKERS}"
        )

    try:
        return _get_ohlcv_data(ticker, days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据获取失败: {str(e)}")


# ========== 静态文件 & 前端挂载 ==========

# 静态文件 (前端 JS/CSS 等)
frontend_static = os.path.join(_PROJECT_ROOT, "frontend", "static")
if os.path.isdir(frontend_static):
    app.mount("/static", StaticFiles(directory=frontend_static), name="static")

# 前端 HTML
frontend_dir = os.path.join(_PROJECT_ROOT, "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


# ========== 启动入口 ==========

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Finance QRC API Server")
    print(f"项目根目录: {_PROJECT_ROOT}")
    print(f"数据缓存: {DATA_CACHE_DIR}")
    print(f"结果目录: {RESULTS_DIR}")
    print(f"可用股票: {DOW10_TICKERS}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8009)
