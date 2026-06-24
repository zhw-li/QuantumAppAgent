"""
MaxCut QAOA FastAPI 后端服务

端口: 8006
API端点:
    GET  /api/health       — 健康检查
    GET  /api/graphs       — 列出所有预设图
    GET  /api/graph/{name} — 获取特定预设图数据
    POST /api/solve        — 运行QAOA求解MaxCut
    POST /api/brute-force  — 运行暴力搜索

静态文件: /static/ 前端页面
"""

import os
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph_utils import (
    PRESET_GRAPHS,
    brute_force_maxcut,
    get_cut_edges,
    list_graphs,
)
from maxcut_solver import solve_maxcut_qaoa

# ============================================================
# FastAPI 应用
# ============================================================

app = FastAPI(
    title="MaxCut QAOA 求解平台",
    description="基于cqlib SDK的QAOA MaxCut量子优化求解平台",
    version="1.0.0",
)

# CORS — 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 请求/响应模型
# ============================================================

class SolveRequest(BaseModel):
    """QAOA求解请求"""
    graph_name: Optional[str] = Field(None, description="预设图名称")
    edges: Optional[List[List[int]]] = Field(None, description="自定义边列表 [[src, tgt, weight], ...]")
    n_nodes: Optional[int] = Field(None, description="自定义图节点数（使用自定义边时必填）")
    depth: int = Field(2, ge=1, le=10, description="QAOA层数（p值）")
    restarts: int = Field(5, ge=1, le=20, description="随机重启次数")
    maxiter: int = Field(300, ge=50, le=2000, description="每次重启最大迭代次数")


class BruteForceRequest(BaseModel):
    """暴力搜索请求"""
    graph_name: Optional[str] = Field(None, description="预设图名称")
    edges: Optional[List[List[int]]] = Field(None, description="自定义边列表")
    n_nodes: Optional[int] = Field(None, description="自定义图节点数")


# ============================================================
# API端点
# ============================================================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "MaxCut QAOA Solver",
        "version": "1.0.0",
        "port": 8006,
        "preset_graphs": list(PRESET_GRAPHS.keys()),
    }


@app.get("/api/graphs")
async def get_graphs():
    """列出所有预设图的元信息"""
    return {"graphs": list_graphs()}


@app.get("/api/graph/{name}")
async def get_graph(name: str):
    """获取指定预设图的完整数据"""
    graph = PRESET_GRAPHS.get(name)
    if graph is None:
        raise HTTPException(status_code=404, detail=f"图 '{name}' 不存在，可选: {list(PRESET_GRAPHS.keys())}")
    return graph


@app.post("/api/solve")
async def solve(req: SolveRequest):
    """
    运行QAOA求解MaxCut

    支持两种模式:
        1. 指定 graph_name 使用预设图
        2. 指定 edges + n_nodes 使用自定义图
    """
    # 确定图的边和节点数
    if req.graph_name:
        graph = PRESET_GRAPHS.get(req.graph_name)
        if graph is None:
            raise HTTPException(
                status_code=404,
                detail=f"图 '{req.graph_name}' 不存在，可选: {list(PRESET_GRAPHS.keys())}"
            )
        edges = graph["edges"]
        n_nodes = graph["n_nodes"]
    elif req.edges and req.n_nodes:
        edges = req.edges
        n_nodes = req.n_nodes
    else:
        raise HTTPException(
            status_code=400,
            detail="必须指定 graph_name 或 (edges + n_nodes)"
        )

    # 运行QAOA求解
    try:
        result = solve_maxcut_qaoa(
            edges=edges,
            n_nodes=n_nodes,
            depth=req.depth,
            restarts=req.restarts,
            maxiter=req.maxiter,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"求解失败: {str(e)}")


@app.post("/api/brute-force")
async def brute_force(req: BruteForceRequest):
    """
    运行暴力搜索MaxCut最优解

    注意: 节点数>20时计算量指数增长，谨慎使用
    """
    # 确定图的边和节点数
    if req.graph_name:
        graph = PRESET_GRAPHS.get(req.graph_name)
        if graph is None:
            raise HTTPException(
                status_code=404,
                detail=f"图 '{req.graph_name}' 不存在，可选: {list(PRESET_GRAPHS.keys())}"
            )
        edges = graph["edges"]
        n_nodes = graph["n_nodes"]
    elif req.edges and req.n_nodes:
        edges = req.edges
        n_nodes = req.n_nodes
    else:
        raise HTTPException(
            status_code=400,
            detail="必须指定 graph_name 或 (edges + n_nodes)"
        )

    # 节点数过多警告
    if n_nodes > 20:
        raise HTTPException(
            status_code=400,
            detail=f"节点数 {n_nodes} 过大，暴力搜索需要评估 2^{n_nodes} = {2**n_nodes} 种分配"
        )

    try:
        result = brute_force_maxcut(edges, n_nodes)
        # 添加被切割边信息
        best_partition = result["best_partition"]
        result["cut_edges"] = get_cut_edges(best_partition, edges)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"暴力搜索失败: {str(e)}")


# ============================================================
# 静态文件挂载（前端页面）
# ============================================================

_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
_FRONTEND_STATIC = os.path.join(_FRONTEND_DIR, "static")

if os.path.isdir(_FRONTEND_STATIC):
    app.mount("/static", StaticFiles(directory=_FRONTEND_STATIC), name="static")


@app.get("/")
async def serve_frontend():
    html_path = os.path.join(_FRONTEND_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Frontend not built yet. Use /docs for API."}


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
