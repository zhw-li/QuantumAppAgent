/**
 * Quantum Reservoir Computing - API 模块
 *
 * 经 @/utils/axios.js 统一请求；并对后端裸数据做适配，返回页面 (index.vue) 期望的结构。
 *
 * 后端 (Finance_QRC FastAPI, port 8009) 端点契约:
 *   GET  /api/stocks               { stocks, default }
 *   GET  /api/params               { n_qubits, depth, window_size, n_reservoir, spectral_radius, ridge_alpha }
 *   POST /api/solve                { ticker, params..., classic:{RMSE,MAE,MAPE,n_params,predictions,actual,dates},
 *                                                  quantum:{RMSE,MAE,MAPE,n_params,predictions,actual,dates},
 *                                                  comparison:{...} }
 *   GET  /api/circuit              { n_qubits, depth, n_parameters, gate_counts, circuit_depth, qcis }
 *   GET  /api/reservoir-states     { quantum_states, classic_states, input_values }
 *   GET  /api/compare              { stocks:[{ticker, classic_rmse, quantum_rmse, ...}], summary }
 *   GET  /api/raw-data/{ticker}    { ticker, dates, close, ... }
 */
import request from '@/utils/axios.js';

const BASE = '/api';

/**
 * 适配 /api/solve 响应：后端把 classic/quantum 指标分散在两块，
 * 页面期望收敛到 metrics.{classic,quantum} 与统一 predictions/reservoir_states。
 */
function adaptSolveResult(raw) {
  const classic = raw.classic || {};
  const quantum = raw.quantum || {};

  // 指标块（字段名对齐：后端 n_params -> 页面 param_count）
  const metrics = {
    classic: {
      RMSE: classic.RMSE,
      MAE: classic.MAE,
      MAPE: classic.MAPE,
      param_count: classic.n_params
    },
    quantum: {
      RMSE: quantum.RMSE,
      MAE: quantum.MAE,
      MAPE: quantum.MAPE,
      param_count: quantum.n_params
    }
  };

  // 预测序列（取 quantum 的 actual 与 dates 作横轴，classic/quantum 各自预测线）
  const dates = quantum.dates || classic.dates || [];
  const predictions = {
    dates,
    actual: quantum.actual || classic.actual || [],
    classic: classic.predictions || [],
    quantum: quantum.predictions || []
  };

  return {
    success: !('error' in classic) && !('error' in quantum),
    stock: raw.ticker,
    params: raw.params,
    metrics,
    predictions,
    reservoir_states: null, // 由独立端点按需加载
    circuit_info: null,     // 由独立端点按需加载
    comparison: raw.comparison || null
  };
}

/** 适配 /api/reservoir-states 响应为页面期望的 {quantumPoints, classicPoints} */
function adaptReservoirStates(raw) {
  return {
    quantumPoints: raw.quantum_states || [],
    classicPoints: raw.classic_states || [],
    input_values: raw.input_values || []
  };
}

/** 适配 /api/circuit 响应为页面 CircuitInfo 期望结构 */
function adaptCircuitInfo(raw) {
  return {
    n_qubits: raw.n_qubits,
    depth: raw.depth,
    gate_count: raw.gate_counts ? Object.values(raw.gate_counts).reduce((a, b) => a + b, 0) : 0,
    gate_counts: raw.gate_counts,
    parameter_count: raw.n_parameters,
    circuit_depth: raw.circuit_depth,
    circuit_type: 'Parameterized Quantum Reservoir',
    qcis_code: raw.qcis || ''
  };
}

/** 适配 /api/compare 响应为页面 compare 表格期望的行结构 */
function adaptCompare(raw) {
  const stocks = (raw.stocks || []).map(s => ({
    ticker: s.ticker,
    classic_RMSE: s.classic_rmse,
    quantum_RMSE: s.quantum_rmse,
    classic_MAE: null,
    quantum_MAE: null,
    classic_params: 9702,
    quantum_params: 46,
    improvement: s.improvement,
    quantum_wins: s.quantum_wins
  }));
  return stocks;
}

export const api = {
  /** GET /api/stocks */
  getStocks() {
    return request({ url: `${BASE}/stocks`, method: 'get' });
  },

  /** GET /api/params */
  getParams() {
    return request({ url: `${BASE}/params`, method: 'get' });
  },

  /**
   * POST /api/solve —— 运行 QRC vs ClassicRC 对比实验
   * @param {Object} payload { ticker, n_qubits, depth, window_size, n_reservoir, spectral_radius, ridge_alpha, seed }
   * @returns 适配后的页面结构
   */
  async solve(payload) {
    const raw = await request({ url: `${BASE}/solve`, method: 'post', data: payload });
    // 后端 /api/solve 不含 {code,data} 包裹，直接返回对象；若 axios 拦截器已解包，raw 即数据
    return adaptSolveResult(raw);
  },

  /** GET /api/reservoir-states?ticker=&n_qubits=&depth=&window_size= */
  async getReservoirStates(query) {
    const raw = await request({ url: `${BASE}/reservoir-states`, method: 'get', params: query });
    return adaptReservoirStates(raw);
  },

  /** GET /api/circuit?n_qubits=&depth= */
  async getCircuitInfo(query) {
    const raw = await request({ url: `${BASE}/circuit`, method: 'get', params: query });
    return adaptCircuitInfo(raw);
  },

  /** GET /api/compare */
  async getCompare() {
    const raw = await request({ url: `${BASE}/compare`, method: 'get' });
    return adaptCompare(raw);
  },

  /** GET /api/raw-data/{ticker}?days= */
  getRawData(ticker, days = 365) {
    return request({ url: `${BASE}/raw-data/${ticker}`, method: 'get', params: { days } });
  }
};

export default api;
