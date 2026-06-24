/**
 * Quantum Reservoir Computing - Mock data and API configuration
 * For standalone preview. Replace with real API calls via axios.js in production.
 */

export const API_BASE = '/api';

export const DEFAULT_STOCKS = ['AAPL', 'MSFT', 'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'CVX', 'KO'];

export const DEFAULT_PARAMS = {
  n_qubits: 4,
  depth: 2,
  window_size: 5,
  n_reservoir: 100,
  spectral_radius: 0.9,
  ridge_alpha: 1.0,
  seed: 42
};

/** Generate mock prediction data */
function generateMockPredictions(length = 60) {
  const actual = [];
  const classic = [];
  const quantum = [];
  const dates = [];
  const baseDate = new Date('2024-01-02');

  let aPrice = 150;
  let cPrice = 150;
  let qPrice = 150;

  for (let i = 0; i < length; i++) {
    const d = new Date(baseDate);
    d.setDate(d.getDate() + i);
    // Skip weekends
    if (d.getDay() === 0 || d.getDay() === 6) continue;
    dates.push(d.toISOString().slice(0, 10));

    const drift = (Math.sin(i / 10) * 2 + (Math.random() - 0.5) * 3);
    aPrice = aPrice + drift;
    cPrice = cPrice + drift + (Math.random() - 0.5) * 1.5;
    qPrice = qPrice + drift + (Math.random() - 0.5) * 0.8;

    actual.push(parseFloat(aPrice.toFixed(2)));
    classic.push(parseFloat(cPrice.toFixed(2)));
    quantum.push(parseFloat(qPrice.toFixed(2)));
  }

  return { dates, actual, classic, quantum };
}

/** Generate mock reservoir state data for PCA scatter */
function generateMockReservoirStates(nPoints = 120, nDims = 4) {
  const quantumPoints = [];
  const classicPoints = [];

  for (let i = 0; i < nPoints; i++) {
    const qPoint = [];
    const cPoint = [];
    for (let d = 0; d < 2; d++) { // PCA reduces to 2D
      qPoint.push(parseFloat(((Math.sin(i / 20 + d) * 3 + Math.random() * 1.5) + d * 2).toFixed(2)));
      cPoint.push(parseFloat(((Math.cos(i / 20 + d) * 2 + Math.random() * 2) - d * 1.5).toFixed(2)));
    }
    quantumPoints.push(qPoint);
    classicPoints.push(cPoint);
  }

  return { quantumPoints, classicPoints };
}

/** Generate mock circuit info */
function generateMockCircuitInfo() {
  return {
    n_qubits: 4,
    depth: 2,
    gate_count: 28,
    parameter_count: 12,
    circuit_type: 'Parameterized Quantum Reservoir',
    qcis_code: `# QCIS Circuit - Quantum Reservoir (4 qubits, depth 2)
Q0 RY 0.3124
Q1 RY -0.5678
Q2 RY 0.8912
Q3 RY -0.2345
Q0 Q1 CNOT
Q1 Q2 CNOT
Q2 Q3 CNOT
Q3 Q0 CNOT
Q0 RZ 1.2345
Q1 RZ -0.7890
Q2 RZ 0.4567
Q3 RZ -1.0123
Q0 RY -0.4321
Q1 RY 0.8765
Q2 RY -0.1098
Q3 RY 0.5432
Q0 Q2 CNOT
Q1 Q3 CNOT
Q0 RZ 0.6543
Q1 RZ -0.3210
Q2 RZ 0.9876
Q3 RZ -0.1357`
  };
}

/** Generate mock comparison data across multiple stocks */
function generateMockComparison() {
  const stocks = DEFAULT_STOCKS.slice(0, 5);
  return stocks.map(ticker => ({
    ticker,
    classic_RMSE: parseFloat((4 + Math.random() * 3).toFixed(2)),
    quantum_RMSE: parseFloat((3 + Math.random() * 2).toFixed(2)),
    classic_MAE: parseFloat((3 + Math.random() * 2).toFixed(2)),
    quantum_MAE: parseFloat((2 + Math.random() * 1.5).toFixed(2)),
    classic_MAPE: parseFloat((5 + Math.random() * 10).toFixed(2)),
    quantum_MAPE: parseFloat((4 + Math.random() * 8).toFixed(2)),
    classic_params: 2560,
    quantum_params: 48
  }));
}

/** Mock solve result */
export function getMockSolveResult() {
  const predictions = generateMockPredictions();
  return {
    success: true,
    stock: 'AAPL',
    params: { ...DEFAULT_PARAMS },
    metrics: {
      classic: {
        RMSE: parseFloat((4.52 + Math.random()).toFixed(2)),
        MAE: parseFloat((3.28 + Math.random() * 0.5).toFixed(2)),
        MAPE: parseFloat((8.45 + Math.random() * 3).toFixed(2)),
        param_count: 2560
      },
      quantum: {
        RMSE: parseFloat((3.21 + Math.random() * 0.8).toFixed(2)),
        MAE: parseFloat((2.35 + Math.random() * 0.3).toFixed(2)),
        MAPE: parseFloat((6.12 + Math.random() * 2).toFixed(2)),
        param_count: 48
      }
    },
    predictions,
    reservoir_states: generateMockReservoirStates(),
    circuit_info: generateMockCircuitInfo()
  };
}

/** Mock comparison result */
export function getMockCompareResult() {
  return {
    success: true,
    comparison: generateMockComparison()
  };
}

/** Mock API fetch wrapper for standalone preview */
export async function mockFetch(endpoint, body) {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 600));

  switch (endpoint) {
    case '/api/solve':
      return getMockSolveResult();
    case '/api/stocks':
      return { stocks: DEFAULT_STOCKS };
    case '/api/params':
      return {
        n_qubits: [4, 6, 8],
        depth: [2, 3],
        window_size: [5, 10, 20],
        n_reservoir: { min: 50, max: 500 },
        spectral_radius: { min: 0.1, max: 0.99, step: 0.01 },
        ridge_alpha: { min: 0.01, max: 100, step: 0.01 }
      };
    case '/api/circuit':
      return generateMockCircuitInfo();
    case '/api/reservoir-states':
      return generateMockReservoirStates();
    case '/api/compare':
      return getMockCompareResult();
    default:
      throw new Error(`Unknown endpoint: ${endpoint}`);
  }
}
