/* ========================================
   Finance QRC - Vue 3 CDN Application
   Quantum Reservoir Computing Finance Platform
   Backend API on port 8009
   ======================================== */

const { createApp, ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } = Vue;

// 使用相对路径，前端自动与后端同源（无论后端跑在哪个端口都匹配）
const API_BASE = '/api';

const DOW10_TICKERS = ['AAPL', 'MSFT', 'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'CVX', 'KO'];

const app = createApp({
  setup() {
    // ===== Reactive State =====
    const selectedStock = ref('AAPL');
    const nQubits = ref(4);
    const depth = ref(2);
    const windowSize = ref(5);
    const nReservoir = ref(100);
    const spectralRadius = ref(0.9);
    const ridgeAlpha = ref(1.0);
    const loading = ref(false);
    const activeTab = ref('prediction');
    const hasResult = ref(false);

    // Current experiment result (from /api/solve)
    const currentResult = reactive({
      ticker: '',
      classic: null,
      quantum: null,
      comparison: null,
      params: null,
    });

    // Reservoir states (from /api/reservoir-states)
    const reservoirData = reactive({
      quantum_states: [],
      classic_states: [],
      input_values: [],
    });

    // Circuit info (from /api/circuit)
    const circuitData = reactive({
      n_qubits: 0,
      depth: 0,
      n_parameters: 0,
      gate_counts: {},
      circuit_depth: 0,
      qcis: '',
    });

    // Multi-stock comparison (from /api/compare)
    const compareData = reactive({
      stocks: [],
      summary: null,
    });

    // Chart instances (for proper cleanup)
    const chartInstances = {};

    // ===== API Methods =====
    async function apiCall(endpoint, options = {}) {
      try {
        const resp = await fetch(`${API_BASE}${endpoint}`, {
          headers: { 'Content-Type': 'application/json' },
          ...options,
        });
        if (!resp.ok) {
          const errText = await resp.text();
          throw new Error(`API Error ${resp.status}: ${errText}`);
        }
        return await resp.json();
      } catch (e) {
        console.error(`API call failed: ${endpoint}`, e);
        throw e;
      }
    }

    async function startPrediction() {
      loading.value = true;
      hasResult.value = false;
      try {
        // 1. Run the main solve experiment
        const data = await apiCall('/solve', {
          method: 'POST',
          body: JSON.stringify({
            ticker: selectedStock.value,
            n_qubits: nQubits.value,
            depth: depth.value,
            window_size: windowSize.value,
            n_reservoir: nReservoir.value,
            spectral_radius: spectralRadius.value,
            ridge_alpha: ridgeAlpha.value,
            seed: 42,
            force: true,
          }),
        });

        // Populate result
        currentResult.ticker = data.ticker || selectedStock.value;
        currentResult.classic = data.classic || null;
        currentResult.quantum = data.quantum || null;
        currentResult.comparison = data.comparison || null;
        currentResult.params = data.params || null;

        hasResult.value = true;

        // 2. Fetch reservoir states (async, non-blocking)
        fetchReservoirStates();

        // 3. Fetch circuit info
        fetchCircuitInfo();

        // 4. Fetch multi-stock comparison
        fetchCompareData();

        // Wait for DOM update then render charts
        await nextTick();
        renderActiveTabChart();

        ElementPlus.ElMessage.success('预测完成');
      } catch (e) {
        ElementPlus.ElMessage.error(`预测失败: ${e.message}`);
      } finally {
        loading.value = false;
      }
    }

    async function fetchReservoirStates() {
      try {
        const data = await apiCall(
          `/reservoir-states?ticker=${selectedStock.value}&n_qubits=${nQubits.value}&depth=${depth.value}&window_size=${windowSize.value}&n_samples=50`
        );
        reservoirData.quantum_states = data.quantum_states || [];
        reservoirData.classic_states = data.classic_states || [];
        reservoirData.input_values = data.input_values || [];
      } catch (e) {
        console.warn('储备池状态获取失败:', e);
        reservoirData.quantum_states = [];
        reservoirData.classic_states = [];
        reservoirData.input_values = [];
      }
    }

    async function fetchCircuitInfo() {
      try {
        const data = await apiCall(
          `/circuit?n_qubits=${nQubits.value}&depth=${depth.value}`
        );
        circuitData.n_qubits = data.n_qubits || nQubits.value;
        circuitData.depth = data.depth || depth.value;
        circuitData.n_parameters = data.n_parameters || 0;
        circuitData.gate_counts = data.gate_counts || {};
        circuitData.circuit_depth = data.circuit_depth || 0;
        circuitData.qcis = data.qcis || '';
      } catch (e) {
        console.warn('电路信息获取失败:', e);
      }
    }

    async function fetchCompareData() {
      try {
        const data = await apiCall('/compare');
        compareData.stocks = data.stocks || [];
        compareData.summary = data.summary || null;
      } catch (e) {
        console.warn('多股对比获取失败:', e);
      }
    }

    // ===== Chart Rendering =====
    function disposeChart(key) {
      if (chartInstances[key]) {
        chartInstances[key].dispose();
        delete chartInstances[key];
      }
    }

    function initChart(domId, key) {
      disposeChart(key);
      const dom = document.getElementById(domId);
      if (!dom || dom.offsetWidth === 0) return null;
      const chart = echarts.init(dom);
      chartInstances[key] = chart;
      return chart;
    }

    function renderPredictionChart() {
      const chart = initChart('predictionChart', 'prediction');
      if (!chart || !currentResult.classic || !currentResult.quantum) return;

      const classic = currentResult.classic;
      const quantum = currentResult.quantum;
      const dates = classic.dates || quantum.dates || [];
      const actual = classic.actual || quantum.actual || [];
      const classicPred = classic.predictions || [];
      const quantumPred = quantum.predictions || [];

      chart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
        },
        legend: {
          data: ['Actual Price', 'Classic RC', 'QRC'],
          top: 0,
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: 40,
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: { rotate: 30, fontSize: 11 },
        },
        yAxis: {
          type: 'value',
          name: 'Price ($)',
        },
        series: [
          {
            name: 'Actual Price',
            type: 'line',
            data: actual,
            lineStyle: { width: 2, color: '#020814' },
            itemStyle: { color: '#020814' },
            symbol: 'none',
          },
          {
            name: 'Classic RC',
            type: 'line',
            data: classicPred,
            lineStyle: { width: 2, type: 'dashed', color: '#FAAD14' },
            itemStyle: { color: '#FAAD14' },
            symbol: 'none',
          },
          {
            name: 'QRC',
            type: 'line',
            data: quantumPred,
            lineStyle: { width: 2, color: '#1664FF' },
            itemStyle: { color: '#1664FF' },
            symbol: 'none',
          },
        ],
      });
    }

    function renderReservoirStatesChart() {
      // Quantum reservoir states
      const qChart = initChart('quantumReservoirChart', 'quantumReservoir');
      if (qChart && reservoirData.quantum_states.length > 0) {
        const qProjected = pcaProject(reservoirData.quantum_states, reservoirData.input_values);
        qChart.setOption({
          tooltip: { trigger: 'item' },
          title: { text: 'Quantum Reservoir States (PCA)', left: 'center', top: 0, textStyle: { fontSize: 13 } },
          grid: { left: '3%', right: '4%', bottom: '3%', top: 30, containLabel: true },
          xAxis: { type: 'value', name: 'PC1', nameTextStyle: { fontSize: 11 } },
          yAxis: { type: 'value', name: 'PC2', nameTextStyle: { fontSize: 11 } },
          series: [{
            type: 'scatter',
            data: qProjected.points,
            symbolSize: 7,
            itemStyle: {
              color: function(params) {
                return params.data[2] != null ? getHeatColor(params.data[2]) : '#1664FF';
              },
            },
          }],
          visualMap: {
            min: 0,
            max: 1,
            show: false,
            dimension: 2,
          },
        });
      }

      // Classic reservoir states
      const cChart = initChart('classicReservoirChart', 'classicReservoir');
      if (cChart && reservoirData.classic_states.length > 0) {
        const cProjected = pcaProject(reservoirData.classic_states, reservoirData.input_values);
        cChart.setOption({
          tooltip: { trigger: 'item' },
          title: { text: 'Classic Reservoir States (PCA)', left: 'center', top: 0, textStyle: { fontSize: 13 } },
          grid: { left: '3%', right: '4%', bottom: '3%', top: 30, containLabel: true },
          xAxis: { type: 'value', name: 'PC1', nameTextStyle: { fontSize: 11 } },
          yAxis: { type: 'value', name: 'PC2', nameTextStyle: { fontSize: 11 } },
          series: [{
            type: 'scatter',
            data: cProjected.points,
            symbolSize: 7,
            itemStyle: {
              color: function(params) {
                return params.data[2] != null ? getHeatColor(params.data[2]) : '#FAAD14';
              },
            },
          }],
          visualMap: {
            min: 0,
            max: 1,
            show: false,
            dimension: 2,
          },
        });
      }
    }

    function renderMultiStockChart() {
      const chart = initChart('multiStockBarChart', 'multiStock');
      if (!chart) return;

      const stocks = compareData.stocks;
      if (!stocks || stocks.length === 0) return;

      const tickers = stocks.map(s => s.ticker);
      const classicRMSE = stocks.map(s => s.classic_rmse || 0);
      const quantumRMSE = stocks.map(s => s.quantum_rmse || 0);

      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['Classic RC RMSE', 'QRC RMSE'], top: 0 },
        grid: { left: '3%', right: '4%', bottom: '3%', top: 40, containLabel: true },
        xAxis: { type: 'category', data: tickers },
        yAxis: { type: 'value', name: 'RMSE' },
        series: [
          {
            name: 'Classic RC RMSE',
            type: 'bar',
            data: classicRMSE,
            itemStyle: { color: '#FAAD14' },
            barWidth: '30%',
          },
          {
            name: 'QRC RMSE',
            type: 'bar',
            data: quantumRMSE,
            itemStyle: { color: '#1664FF' },
            barWidth: '30%',
          },
        ],
      });
    }

    function renderActiveTabChart() {
      if (!hasResult.value) return;
      setTimeout(() => {
        nextTick(() => {
          switch (activeTab.value) {
            case 'prediction':
              renderPredictionChart();
              break;
            case 'reservoir':
              renderReservoirStatesChart();
              break;
            case 'circuit':
              // No ECharts needed
              break;
            case 'multistock':
              renderMultiStockChart();
              break;
          }
        });
      }, 200);
    }

    function onTabChange(tab) {
      activeTab.value = tab;
      renderActiveTabChart();
    }

    // ===== PCA Implementation =====
    function pcaProject(data, labels) {
      if (!data || data.length === 0) return { points: [] };

      const matrix = data.map(row => Array.isArray(row) ? row : Object.values(row));
      const n = matrix.length;
      if (n === 0) return { points: [] };
      const d = matrix[0].length;

      if (d <= 2) {
        const points = matrix.map((row, i) => {
          const pt = row.slice(0, 2);
          while (pt.length < 2) pt.push(0);
          if (labels && labels[i] != null) pt.push(labels[i]);
          return pt;
        });
        return { points };
      }

      // Compute mean
      const mean = new Array(d).fill(0);
      for (let i = 0; i < n; i++) {
        for (let j = 0; j < d; j++) {
          mean[j] += matrix[i][j];
        }
      }
      for (let j = 0; j < d; j++) mean[j] /= n;

      // Center
      const centered = matrix.map(row => row.map((v, j) => v - mean[j]));

      // Covariance
      const cov = Array.from({ length: d }, () => new Array(d).fill(0));
      for (let i = 0; i < d; i++) {
        for (let j = i; j < d; j++) {
          let sum = 0;
          for (let k = 0; k < n; k++) sum += centered[k][i] * centered[k][j];
          cov[i][j] = sum / (n - 1);
          cov[j][i] = cov[i][j];
        }
      }

      function powerIteration(mat, dim, numIter = 100) {
        let vec = Array.from({ length: dim }, () => Math.random() - 0.5);
        let norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0));
        if (norm < 1e-10) return vec;
        vec = vec.map(v => v / norm);
        for (let iter = 0; iter < numIter; iter++) {
          const newVec = new Array(dim).fill(0);
          for (let i = 0; i < dim; i++) {
            for (let j = 0; j < dim; j++) {
              newVec[i] += mat[i][j] * vec[j];
            }
          }
          norm = Math.sqrt(newVec.reduce((s, v) => s + v * v, 0));
          if (norm < 1e-10) break;
          vec = newVec.map(v => v / norm);
        }
        return vec;
      }

      function eigenvalue(mat, vec) {
        const dim = vec.length;
        const mv = new Array(dim).fill(0);
        for (let i = 0; i < dim; i++) {
          for (let j = 0; j < dim; j++) mv[i] += mat[i][j] * vec[j];
        }
        let val = 0;
        for (let i = 0; i < dim; i++) val += vec[i] * mv[i];
        return val;
      }

      function deflate(mat, eigenvec, eval_) {
        return mat.map((row, i) => row.map((v, j) => v - eval_ * eigenvec[i] * eigenvec[j]));
      }

      const ev1 = powerIteration(cov, d);
      const ev1Val = eigenvalue(cov, ev1);
      const cov2 = deflate(cov, ev1, ev1Val);
      const ev2 = powerIteration(cov2, d);

      const points = centered.map((row, idx) => {
        const pc1 = row.reduce((s, v, j) => s + v * ev1[j], 0);
        const pc2 = row.reduce((s, v, j) => s + v * ev2[j], 0);
        const pt = [pc1, pc2];
        if (labels && labels[idx] != null) pt.push(labels[idx]);
        return pt;
      });

      return { points };
    }

    // ===== Color Helpers =====
    function getHeatColor(value) {
      const v = Math.max(0, Math.min(1, value));
      const r = Math.round(22 + v * 200);
      const g = Math.round(100 + (1 - v) * 155);
      const b = Math.round(255 - v * 200);
      return `rgb(${r},${g},${b})`;
    }

    // ===== Computed Properties =====
    // Backend returns UPPERCASE keys: RMSE, MAE, MAPE
    const classicRMSE = computed(() => currentResult.classic?.RMSE ?? null);
    const quantumRMSE = computed(() => currentResult.quantum?.RMSE ?? null);
    const classicMAE = computed(() => currentResult.classic?.MAE ?? null);
    const quantumMAE = computed(() => currentResult.quantum?.MAE ?? null);
    const classicMAPE = computed(() => currentResult.classic?.MAPE ?? null);
    const quantumMAPE = computed(() => currentResult.quantum?.MAPE ?? null);
    const classicParams = computed(() => currentResult.classic?.n_params ?? null);
    const quantumParams = computed(() => currentResult.quantum?.n_params ?? null);

    // Backend: comparison.rmse_improvement, .mae_improvement, .mape_improvement
    // (positive = QRC better)
    const rmseImprovement = computed(() => currentResult.comparison?.rmse_improvement ?? null);
    const maeImprovement = computed(() => currentResult.comparison?.mae_improvement ?? null);
    const mapeImprovement = computed(() => currentResult.comparison?.mape_improvement ?? null);
    const paramEfficiency = computed(() => currentResult.comparison?.param_efficiency ?? null);
    const quantumWins = computed(() => currentResult.comparison?.quantum_wins ?? false);

    // Circuit info items
    const circuitInfoItems = computed(() => {
      if (circuitData.n_qubits === 0) {
        return [
          { label: 'Quantum Bits', value: nQubits.value },
          { label: 'Depth', value: depth.value },
          { label: 'Parameters', value: '-' },
          { label: 'Circuit Depth', value: '-' },
        ];
      }
      return [
        { label: 'Quantum Bits', value: circuitData.n_qubits },
        { label: 'Depth', value: circuitData.depth },
        { label: 'Parameters', value: circuitData.n_parameters },
        { label: 'Circuit Depth', value: circuitData.circuit_depth },
      ];
    });

    // Gate counts for circuit tab
    const gateCountEntries = computed(() => {
      const gc = circuitData.gate_counts;
      if (!gc || Object.keys(gc).length === 0) return [];
      return Object.entries(gc).map(([gate, count]) => ({ gate: gate.toUpperCase(), count }));
    });

    // Multi-stock table data
    const multiStockTableData = computed(() => {
      return (compareData.stocks || []).map(s => ({
        ticker: s.ticker,
        classicRMSE: s.classic_rmse,
        quantumRMSE: s.quantum_rmse,
        improvement: s.improvement,
        quantumWins: s.quantum_wins,
      }));
    });

    // ===== Formatting =====
    function fmt(val, digits = 4) {
      if (val == null) return '-';
      return typeof val === 'number' ? val.toFixed(digits) : val;
    }

    function fmtPct(val, digits = 2) {
      if (val == null) return '-';
      const prefix = val > 0 ? '+' : '';
      return prefix + val.toFixed(digits) + '%';
    }

    function fmtArrow(val) {
      if (val == null) return '';
      return val > 0 ? '↑' : val < 0 ? '↓' : '→';
    }

    function fmtParams(val) {
      if (val == null) return '-';
      if (val >= 1000) return (val / 1000).toFixed(1) + 'k';
      return val.toString();
    }

    // ===== Lifecycle =====
    onMounted(async () => {
      await fetchCompareData();
    });

    onBeforeUnmount(() => {
      Object.keys(chartInstances).forEach(key => disposeChart(key));
    });

    // Window resize handler
    let resizeTimer;
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
          Object.values(chartInstances).forEach(chart => {
            if (chart && !chart.isDisposed()) chart.resize();
          });
        }, 300);
      });
    }

    return {
      // State
      selectedStock,
      nQubits,
      depth,
      windowSize,
      nReservoir,
      spectralRadius,
      ridgeAlpha,
      loading,
      activeTab,
      hasResult,
      currentResult,
      reservoirData,
      circuitData,
      compareData,
      DOW10_TICKERS,

      // Computed
      classicRMSE,
      quantumRMSE,
      classicMAE,
      quantumMAE,
      classicMAPE,
      quantumMAPE,
      classicParams,
      quantumParams,
      rmseImprovement,
      maeImprovement,
      mapeImprovement,
      paramEfficiency,
      quantumWins,
      circuitInfoItems,
      gateCountEntries,
      multiStockTableData,

      // Methods
      startPrediction,
      onTabChange,
      fmt,
      fmtPct,
      fmtArrow,
      fmtParams,
    };
  }
});

app.use(ElementPlus);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}
app.mount('#app');
