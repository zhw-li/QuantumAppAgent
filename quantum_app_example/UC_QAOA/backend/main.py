"""
UC-QAOA 机组组合优化平台 - 后端服务
基于QAOA量子算法求解机组组合(Unit Commitment)问题
"""
import asyncio
import time
import uuid
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from cqlib import Circuit, Parameter
from cqlib.simulator import StatevectorSimulator

# ============ 数据模型 ============

class Generator(BaseModel):
    """发电机组"""
    id: str
    name: str
    p_max: float  # 最大出力 MW
    a: float      # 常数项
    b: float      # 线性系数
    c: float      # 二次系数

    def fuel_cost(self, p: float) -> float:
        """计算燃料成本 F = a + b*P + c*P^2"""
        return self.a + self.b * p + self.c * p ** 2

class SolveRequest(BaseModel):
    """求解请求"""
    generator_ids: List[str] = Field(..., min_length=2, max_length=4, description="选择的机组ID列表(2-4个)")
    loads: List[float] = Field(..., min_length=1, max_length=6, description="各时段负载(MW)")
    qaoa_layers: int = Field(default=2, ge=1, le=5, description="QAOA层数p")
    restarts: int = Field(default=10, ge=1, le=30, description="优化重启次数")

class ScheduleEntry(BaseModel):
    """调度条目"""
    period: int
    generator_id: str
    generator_name: str
    status: int  # 1=ON, 0=OFF
    power: float  # 出力MW
    cost: float   # 燃料成本

class QAOAResult(BaseModel):
    """QAOA求解结果"""
    task_id: str
    status: str
    schedule: List[ScheduleEntry]
    total_cost: float
    qubit_count: int
    optimal_bitstring: str
    classical_optimal_cost: float
    optimality_gap: float
    probability: float
    qaoa_layers: int
    solve_time: float
    qubo_matrix_size: int
    constraint_satisfied: bool

# ============ 机组数据 ============

GENERATORS = {
    "A": Generator(id="A", name="机组A", p_max=300, a=800, b=12, c=0.014),
    "B": Generator(id="B", name="机组B", p_max=420, a=900, b=13, c=0.014),
    "C": Generator(id="C", name="机组C", p_max=550, a=1100, b=14, c=0.016),
    "D": Generator(id="D", name="机组D", p_max=700, a=1300, b=16, c=0.017),
    "E": Generator(id="E", name="机组E", p_max=850, a=1500, b=17, c=0.018),
    "F": Generator(id="F", name="机组F", p_max=1000, a=1700, b=18, c=0.019),
}

# ============ QUBO建模 ============

def build_uc_qubo(gen_ids: List[str], loads: List[float]) -> np.ndarray:
    """
    构建机组组合问题的QUBO矩阵
    
    变量: x[i,t] ∈ {0,1}, 机组i在时段t是否开机
    编码: qubit index = i * T + t (i=机组索引, t=时段索引)
    
    目标: min Σ_i,t x[i,t] * C_i  (燃料成本)
    约束: Σ_i x[i,t] * P_i >= D_t  (负载平衡, 用二次惩罚)
    
    H = Σ_i,t x[i,t]*C_i + λ * Σ_t (D_t - Σ_i x[i,t]*P_i)^2
    """
    n_gens = len(gen_ids)
    n_periods = len(loads)
    n = n_gens * n_periods
    gens = [GENERATORS[gid] for gid in gen_ids]
    
    Q = np.zeros((n, n))
    
    # 燃料成本: 当机组开机时产生成本
    # 简化: 机组开机时按最优出力运行(经济调度)
    # 对于QUBO, 假设开机时按满载运行
    for i, gen in enumerate(gens):
        C_i = gen.fuel_cost(gen.p_max)
        for t in range(n_periods):
            idx = i * n_periods + t
            Q[idx, idx] += C_i
    
    # 负载平衡惩罚: λ * (D_t - Σ_i x[i,t]*P_i)^2
    # 展开: λ * (D_t^2 - 2*D_t*Σ_i x[i,t]*P_i + (Σ_i x[i,t]*P_i)^2)
    # 计算 lambda: 自适应惩罚权重
    avg_cost = np.mean([g.fuel_cost(g.p_max) for g in gens])
    avg_capacity = np.mean([g.p_max for g in gens])
    # lambda 应足够大使约束成立
    lam = max(10 * avg_cost / (avg_capacity ** 2), 5.0)
    
    for t in range(n_periods):
        D_t = loads[t]
        # D_t^2 常数项(不影响优化方向,但影响Q的对角线)
        # -2*λ*D_t*P_i 对角项
        for i, gen in enumerate(gens):
            idx = i * n_periods + t
            Q[idx, idx] += lam * (-2 * D_t * gen.p_max)
        
        # λ * P_i * P_j 交叉项
        for i, gen_i in enumerate(gens):
            for j, gen_j in enumerate(gens):
                if i == j:
                    idx = i * n_periods + t
                    Q[idx, idx] += lam * gen_i.p_max ** 2
                elif i < j:
                    idx_i = i * n_periods + t
                    idx_j = j * n_periods + t
                    Q[idx_i, idx_j] += lam * 2 * gen_i.p_max * gen_j.p_max
    
    # QUBO归一化到[-1,1]范围(改善QAOA优化景观)
    max_abs = np.max(np.abs(Q))
    if max_abs > 0:
        Q = Q / max_abs
    
    return Q


def evaluate_schedule(bitstring: str, gen_ids: List[str], loads: List[float],
                      original_Q: np.ndarray) -> Dict:
    """
    评估一个调度方案
    
    Returns: dict with cost, feasible, schedule details
    """
    n_gens = len(gen_ids)
    n_periods = len(loads)
    gens = [GENERATORS[gid] for gid in gen_ids]
    n = n_gens * n_periods
    
    x = np.array([int(bitstring[-1 - i]) for i in range(n)])
    
    # 计算原始QUBO成本(未归一化)
    cost = float(x @ original_Q @ x)
    
    # 检查约束满足
    feasible = True
    period_details = []
    
    for t in range(n_periods):
        total_capacity = sum(gens[i].p_max * x[i * n_periods + t] for i in range(n_gens))
        if total_capacity < loads[t]:
            feasible = False
        period_details.append({
            "period": t + 1,
            "load": loads[t],
            "capacity": total_capacity,
            "satisfied": total_capacity >= loads[t]
        })
    
    # 计算实际燃料成本
    total_fuel_cost = 0.0
    schedule_entries = []
    
    for t in range(n_periods):
        on_gens = [i for i in range(n_gens) if x[i * n_periods + t] == 1]
        total_cap = sum(gens[i].p_max for i in on_gens) if on_gens else 0
        
        for i in range(n_gens):
            idx = i * n_periods + t
            status = int(x[idx])
            if status == 1 and total_cap > 0:
                # 经济调度: 按容量比例分配负载
                power = gens[i].p_max * (loads[t] / total_cap) if total_cap >= loads[t] else gens[i].p_max
                power = min(power, gens[i].p_max)
            else:
                power = 0.0
            
            fuel = gens[i].fuel_cost(power) if status == 1 else 0.0
            total_fuel_cost += fuel
            schedule_entries.append(ScheduleEntry(
                period=t + 1,
                generator_id=gen_ids[i],
                generator_name=gens[i].name,
                status=status,
                power=round(power, 2),
                cost=round(fuel, 2)
            ))
    
    return {
        "qubo_cost": cost,
        "fuel_cost": total_fuel_cost,
        "feasible": feasible,
        "period_details": period_details,
        "schedule": schedule_entries
    }


def brute_force_optimal(gen_ids: List[str], loads: List[float]) -> Dict:
    """暴力搜索最优解"""
    n_gens = len(gen_ids)
    n_periods = len(loads)
    n = n_gens * n_periods
    
    # 构建未归一化的Q用于评估
    Q_raw = build_uc_qubo_raw(gen_ids, loads)
    
    best_cost = float('inf')
    best_bitstring = None
    best_result = None
    
    for k in range(2 ** n):
        bs = format(k, f'0{n}b')
        result = evaluate_schedule(bs, gen_ids, loads, Q_raw)
        if result["feasible"] and result["fuel_cost"] < best_cost:
            best_cost = result["fuel_cost"]
            best_bitstring = bs
            best_result = result
    
    return {
        "bitstring": best_bitstring,
        "fuel_cost": best_cost,
        "result": best_result
    }


def build_uc_qubo_raw(gen_ids: List[str], loads: List[float]) -> np.ndarray:
    """构建未归一化的QUBO矩阵(用于暴力搜索评估)"""
    n_gens = len(gen_ids)
    n_periods = len(loads)
    n = n_gens * n_periods
    gens = [GENERATORS[gid] for gid in gen_ids]
    
    Q = np.zeros((n, n))
    
    for i, gen in enumerate(gens):
        C_i = gen.fuel_cost(gen.p_max)
        for t in range(n_periods):
            idx = i * n_periods + t
            Q[idx, idx] += C_i
    
    avg_cost = np.mean([g.fuel_cost(g.p_max) for g in gens])
    avg_capacity = np.mean([g.p_max for g in gens])
    lam = max(10 * avg_cost / (avg_capacity ** 2), 5.0)
    
    for t in range(n_periods):
        D_t = loads[t]
        for i, gen in enumerate(gens):
            idx = i * n_periods + t
            Q[idx, idx] += lam * (-2 * D_t * gen.p_max)
        for i, gen_i in enumerate(gens):
            for j, gen_j in enumerate(gens):
                if i == j:
                    idx = i * n_periods + t
                    Q[idx, idx] += lam * gen_i.p_max ** 2
                elif i < j:
                    idx_i = i * n_periods + t
                    idx_j = j * n_periods + t
                    Q[idx_i, idx_j] += lam * 2 * gen_i.p_max * gen_j.p_max
    
    return Q


# ============ QAOA算法 ============

def add_zz(circuit, qi, qj, coeff, gamma):
    """ZZ交互: CNOT-RZ-CNOT分解"""
    angle = 2 * coeff * gamma
    circuit.cx(qi, qj)
    circuit.rz(qj, angle)
    circuit.cx(qi, qj)


def add_z(circuit, qi, coeff, gamma):
    """Z项"""
    circuit.rz(qi, 2 * coeff * gamma)


def build_qaoa_circuit(n, Q, p=1):
    """构建QAOA ansatz"""
    pn = []
    for layer in range(p):
        pn.extend([f'g{layer}', f'b{layer}'])
    
    c = Circuit(n, parameters=pn)
    
    # 初始叠加态
    for i in range(n):
        c.h(i)
    
    # p层QAOA
    for layer in range(p):
        gamma = Parameter(f'g{layer}')
        beta = Parameter(f'b{layer}')
        
        # 代价哈密顿量 H_C
        for i in range(n):
            for j in range(i + 1, n):
                if abs(Q[i][j]) > 1e-12:
                    add_zz(c, i, j, Q[i][j], gamma)
            if abs(Q[i][i]) > 1e-12:
                add_z(c, i, Q[i][i], gamma)
        
        # 混合哈密顿量 H_M
        for i in range(n):
            c.rx(i, 2 * beta)
    
    c.measure_all()
    return c, pn


def qaoa_expectation(params, circuit, param_names, n, Q):
    """计算QAOA期望值"""
    bc = circuit.assign_parameters(dict(zip(param_names, params)))
    probs = StatevectorSimulator(circuit=bc).measure()
    
    exp_val = 0.0
    for bitstring, prob in probs.items():
        if prob < 1e-12:
            continue
        # 注意: cqlib测量结果反序
        x = np.array([(1 - int(bitstring[-1 - i])) for i in range(n)])
        cost = float(x @ Q @ x)
        exp_val += prob * cost
    
    return exp_val


def run_qaoa(n, Q, p=1, restarts=10):
    """运行QAOA优化"""
    from scipy.optimize import minimize  # lazy import
    
    circuit, param_names = build_qaoa_circuit(n, Q, p)
    
    best_result = None
    best_cost = float('inf')
    history = []
    
    for r in range(restarts):
        x0 = np.random.uniform(0, np.pi, len(param_names))
        try:
            result = minimize(
                qaoa_expectation, x0,
                args=(circuit, param_names, n, Q),
                method='COBYLA',
                options={'maxiter': 500, 'rhobeg': 0.5}
            )
            history.append({"restart": r, "cost": float(result.fun), "success": result.success})
            if result.fun < best_cost:
                best_cost = result.fun
                best_result = result
        except Exception as e:
            history.append({"restart": r, "cost": float('inf'), "success": False, "error": str(e)})
    
    return best_result, circuit, param_names, history


def find_best_feasible(circuit, param_names, params, n, Q, gen_ids, loads, top_k=50):
    """
    从QAOA采样结果中搜索最优可行解
    最高概率解 ≠ 最优可行解! 必须搜索top-k
    """
    bc = circuit.assign_parameters(dict(zip(param_names, params)))
    probs = StatevectorSimulator(circuit=bc).measure()
    
    Q_raw = build_uc_qubo_raw(gen_ids, loads)
    
    # 按概率排序,取top_k
    sorted_probs = sorted(probs.items(), key=lambda x: -x[1])
    
    best_feasible = None
    best_feasible_cost = float('inf')
    best_prob = 0.0
    
    for bitstring, prob in sorted_probs[:top_k]:
        result = evaluate_schedule(bitstring, gen_ids, loads, Q_raw)
        if result["feasible"] and result["fuel_cost"] < best_feasible_cost:
            best_feasible_cost = result["fuel_cost"]
            best_feasible = result
            best_prob = prob
    
    # 如果top_k中没有可行解,扩大搜索
    if best_feasible is None:
        for bitstring, prob in sorted_probs:
            result = evaluate_schedule(bitstring, gen_ids, loads, Q_raw)
            if result["feasible"]:
                best_feasible_cost = result["fuel_cost"]
                best_feasible = result
                best_prob = prob
                break
    
    return best_feasible, best_feasible_cost, best_prob


# ============ 任务管理 ============

tasks_store: Dict[str, Dict] = {}

# ============ FastAPI应用 ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="UC-QAOA 机组组合优化平台",
    description="基于QAOA量子近似优化算法的机组组合(Unit Commitment)求解器",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/generators")
async def get_generators():
    """获取所有发电机组信息"""
    return {
        "generators": [g.model_dump() for g in GENERATORS.values()],
        "load_options": [400, 600, 700]
    }


@app.post("/api/solve", response_model=QAOAResult)
async def solve_uc(req: SolveRequest):
    """
    求解机组组合问题
    
    1. 构建QUBO矩阵
    2. 运行QAOA优化
    3. 搜索最优可行解
    4. 暴力搜索经典最优
    5. 计算最优性差距
    """
    # 验证机组ID
    for gid in req.generator_ids:
        if gid not in GENERATORS:
            raise HTTPException(400, f"未知机组ID: {gid}")
    
    # 验证负载值
    for load in req.loads:
        if load not in [400, 600, 700]:
            raise HTTPException(400, f"负载值必须为400/600/700 MW, 当前: {load}")
    
    n_gens = len(req.generator_ids)
    n_periods = len(req.loads)
    n = n_gens * n_periods
    
    
    
    task_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        # 1. 构建QUBO
        Q = build_uc_qubo(req.generator_ids, req.loads)
        
        # 2. 运行QAOA (在异步中运行CPU密集任务)
        loop = asyncio.get_event_loop()
        best_result, circuit, param_names, history = await loop.run_in_executor(
            None, run_qaoa, n, Q, req.qaoa_layers, req.restarts
        )
        
        if best_result is None:
            raise HTTPException(500, "QAOA优化失败: 所有重启均未收敛")
        
        # 3. 搜索最优可行解
        feasible_result, feasible_cost, probability = await loop.run_in_executor(
            None, find_best_feasible,
            circuit, param_names, best_result.x,
            n, Q, req.generator_ids, req.loads, 100
        )
        
        # 4. 暴力搜索经典最优(仅小规模)
        classical_result = None
        classical_cost = float('inf')
        if n <= 20:
            classical_result = await loop.run_in_executor(
                None, brute_force_optimal, req.generator_ids, req.loads
            )
            classical_cost = classical_result["fuel_cost"] if classical_result else float('inf')
        
        # 5. 计算最优性差距
        if feasible_result and classical_cost < float('inf'):
            gap = abs(feasible_cost - classical_cost) / max(classical_cost, 1e-10) * 100
        else:
            gap = -1.0
        
        solve_time = time.time() - start_time
        
        if feasible_result is None:
            # 没有找到可行解,返回QAOA最高概率解
            bc = circuit.assign_parameters(dict(zip(param_names, best_result.x)))
            probs = StatevectorSimulator(circuit=bc).measure()
            best_bs = max(probs.items(), key=lambda x: x[1])[0]
            Q_raw = build_uc_qubo_raw(req.generator_ids, req.loads)
            eval_result = evaluate_schedule(best_bs, req.generator_ids, req.loads, Q_raw)
            
            return QAOAResult(
                task_id=task_id,
                status="infeasible",
                schedule=eval_result["schedule"],
                total_cost=round(eval_result["fuel_cost"], 2),
                qubit_count=n,
                optimal_bitstring=best_bs,
                classical_optimal_cost=round(classical_cost, 2) if classical_result else -1,
                optimality_gap=-1.0,
                probability=round(probs[best_bs], 6),
                qaoa_layers=req.qaoa_layers,
                solve_time=round(solve_time, 2),
                qubo_matrix_size=n,
                constraint_satisfied=False
            )
        
        # 构建最优比特串
        opt_bs_parts = []
        for t in range(n_periods):
            for i in range(n_gens):
                idx = i * n_periods + t
                # 找到对应的schedule entry
                for entry in feasible_result["schedule"]:
                    if entry.period == t + 1 and entry.generator_id == req.generator_ids[i]:
                        opt_bs_parts.append(str(entry.status))
                        break
        
        opt_bitstring = ''.join(reversed(opt_bs_parts))  # cqlib反序
        
        return QAOAResult(
            task_id=task_id,
            status="success",
            schedule=feasible_result["schedule"],
            total_cost=round(feasible_cost, 2),
            qubit_count=n,
            optimal_bitstring=opt_bitstring,
            classical_optimal_cost=round(classical_cost, 2) if classical_result else -1,
            optimality_gap=round(gap, 2),
            probability=round(probability, 6),
            qaoa_layers=req.qaoa_layers,
            solve_time=round(solve_time, 2),
            qubo_matrix_size=n,
            constraint_satisfied=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"求解失败: {str(e)}")


@app.post("/api/solve-classical")
async def solve_classical(req: SolveRequest):
    """经典暴力搜索求解(用于对比)"""
    for gid in req.generator_ids:
        if gid not in GENERATORS:
            raise HTTPException(400, f"未知机组ID: {gid}")
    
    n_gens = len(req.generator_ids)
    n_periods = len(req.loads)
    n = n_gens * n_periods
    
    if n > 20:
        raise HTTPException(400, f"暴力搜索仅支持≤20个变量, 当前: {n}")
    
    start_time = time.time()
    result = brute_force_optimal(req.generator_ids, req.loads)
    solve_time = time.time() - start_time
    
    if result["result"] is None:
        return {
            "status": "infeasible",
            "message": "无可行解",
            "solve_time": round(solve_time, 2)
        }
    
    return {
        "status": "success",
        "schedule": [e.model_dump() for e in result["result"]["schedule"]],
        "total_cost": round(result["fuel_cost"], 2),
        "bitstring": result["bitstring"],
        "solve_time": round(solve_time, 2),
        "qubit_count": n
    }


@app.get("/api/validate")
async def validate_config(generator_ids: str, loads: str):
    """验证配置是否满足量子比特数要求"""
    gen_list = generator_ids.split(",")
    load_list = [float(x) for x in loads.split(",")]
    n = len(gen_list) * len(load_list)
    
    return {
        "generator_count": len(gen_list),
        "period_count": len(load_list),
        "qubit_count": n,
        "valid": n >= 2,
        "message": f"{len(gen_list)}机组×{len(load_list)}时段={n}量子比特"
    }


# ============ 静态文件挂载 ============
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
_FRONTEND_STATIC = os.path.join(_FRONTEND_DIR, "static") if os.path.isdir(os.path.join(_FRONTEND_DIR, "static")) else _FRONTEND_DIR

if os.path.isdir(_FRONTEND_DIR):
    if os.path.isdir(os.path.join(_FRONTEND_DIR, "static")):
        app.mount("/static", StaticFiles(directory=os.path.join(_FRONTEND_DIR, "static")), name="static")
    else:
        # frontend has css/ and js/ subdirs, mount as /static/
        app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")


@app.get("/")
async def serve_frontend():
    html_path = os.path.join(_FRONTEND_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Frontend not found. Use /docs for API."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
