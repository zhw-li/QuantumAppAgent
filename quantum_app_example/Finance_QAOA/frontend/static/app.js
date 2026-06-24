/* ============================================
   量子组合投资优化云平台 - Vue App Logic
   API contract (port 8006):
     GET  /api/stocks                        → { stocks, tiers }
     GET  /api/stock/{symbol}/history        → { symbol, history: [{date, close}] }
     GET  /api/statistics?tier=demo          → { symbols, annual_returns, annual_volatilities,
                                                 sharpe_ratios, max_drawdowns, total_returns,
                                                 correlation, correlation_matrix, annual_covariance,
                                                 price_history }
     POST /api/optimize/classical            → { weights:{sym:w}, portfolio_return, portfolio_risk,
                                                 portfolio_sharpe, sharpe_ratio, efficient_frontier,
                                                 selected_stocks, top_k_selection, stock_points,
                                                 symbols, tier }
     POST /api/optimize/quantum              → { symbols, tier, k, q, solution, selected_indices,
                                                 selected_stocks, weights:{sym:w}, portfolio_return,
                                                 portfolio_risk, portfolio_sharpe, sharpe_ratio,
                                                 cost_gap, optimal_energy, penalty_weight,
                                                 norm_factor, n_qubits, depth,
                                                 top_bitstrings:[{bitstring,probability,is_selected}],
                                                 brute_force:{selected_stocks,portfolio_return,
                                                              portfolio_risk,portfolio_sharpe} }
     POST /api/compare                       → { symbols, tier, k, q,
                                                 classical:{weights,portfolio_return,portfolio_risk,
                                                            portfolio_sharpe,sharpe_ratio,
                                                            efficient_frontier,selected_stocks},
                                                 quantum:{weights,selected_indices,selected_stocks,
                                                          portfolio_return,portfolio_risk,
                                                          portfolio_sharpe,sharpe_ratio,
                                                          qubo_energy,optimal_energy,cost_gap,
                                                          n_qubits},
                                                 bruteforce:{selected_indices,selected_stocks,
                                                             portfolio_return,portfolio_risk,
                                                             portfolio_sharpe,sharpe_ratio,
                                                             qubo_energy,optimal_energy},
                                                 efficient_frontier }
   ============================================ */

const { createApp, ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } = Vue;

// 使用相对路径，前端自动与后端同源（无论后端跑在哪个端口都匹配）
const API_BASE = '';

/* Color palette for charts */
const COLORS = [
  '#1664FF', '#4F9DF7', '#00C7E7', '#FB4214', '#E6A23C',
  '#67C23A', '#909399', '#F56C6C', '#409EFF', '#6F7AD3',
  '#D14A61', '#2DB7B5'
];

const PIE_COLORS = [
  '#1664FF', '#4F9DF7', '#00C7E7', '#FB4214', '#E6A23C',
  '#67C23A', '#9B59B6', '#1ABC9C', '#E74C3C', '#3498DB',
  '#D14A61', '#2DB7B5'
];

const app = createApp({
  setup() {
    /* ===================== STATE ===================== */
    const activeTab = ref('dashboard');
    const dashboardTier = ref('demo');
    const statsTier = ref('demo');

    const stocks = ref([]);
    const tiers = ref({});
    const stockHistories = ref({});
    const statsData = ref(null);
    const statsTableData = ref([]);

    const classicalParams = reactive({ tier: 'demo', k: 3, q: 1.0 });
    const classicalResult = ref(null);
    const classicalLoading = ref(false);

    const quantumParams = reactive({ tier: 'demo', k: 3, q: 1.0, depth: 2, restarts: 5 });
    const quantumResult = ref(null);
    const quantumLoading = ref(false);

    const compareParams = reactive({ tier: 'demo', k: 3, q: 1.0, depth: 2, restarts: 5 });
    const compareResult = ref(null);
    const compareLoading = ref(false);

    /* Chart instances registry */
    const chartInstances = {};

    /* ===================== UTILITIES ===================== */
    function formatNum(val, digits = 2) {
      if (val === null || val === undefined || isNaN(val)) return '--';
      return Number(val).toFixed(digits);
    }

    /**
     * Get or create an ECharts instance.
     * CRITICAL RULES:
     *   1. Check offsetWidth > 0 before init (element must be visible)
     *   2. Dispose existing instance before re-creating
     */
    function getOrCreateChart(domId) {
      const dom = document.getElementById(domId);
      if (!dom) return null;
      if (dom.offsetWidth <= 0) return null;
      if (chartInstances[domId]) {
        chartInstances[domId].dispose();
        delete chartInstances[domId];
      }
      const chart = echarts.init(dom);
      chartInstances[domId] = chart;
      return chart;
    }

    function disposeChart(domId) {
      if (chartInstances[domId]) {
        chartInstances[domId].dispose();
        delete chartInstances[domId];
      }
    }

    function disposeAllCharts() {
      Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key] && !chartInstances[key].isDisposed()) {
          chartInstances[key].dispose();
        }
        delete chartInstances[key];
      });
    }

    /* ===================== API CALLS ===================== */
    async function apiGet(url) {
      const resp = await fetch(`${API_BASE}${url}`);
      if (!resp.ok) throw new Error(`API Error: ${resp.status}`);
      return resp.json();
    }

    async function apiPost(url, body) {
      const resp = await fetch(`${API_BASE}${url}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!resp.ok) throw new Error(`API Error: ${resp.status}`);
      return resp.json();
    }

    /* ===================== DATA LOADING ===================== */
    async function fetchStocks() {
      try {
        const data = await apiGet('/api/stocks');
        stocks.value = data.stocks || [];
        tiers.value = data.tiers || {};
      } catch (e) {
        console.error('fetchStocks error:', e);
        stocks.value = [];
        tiers.value = {};
      }
    }

    async function fetchHistory(symbol) {
      try {
        const data = await apiGet(`/api/stock/${symbol}/history`);
        // API returns { symbol, history: [{date, close}] }
        stockHistories.value[symbol] = data.history || [];
      } catch (e) {
        console.error(`fetchHistory(${symbol}) error:`, e);
        stockHistories.value[symbol] = [];
      }
    }

    async function fetchStatistics(tier) {
      try {
        const data = await apiGet(`/api/statistics?tier=${tier}`);
        statsData.value = data;
        // Build table data from flat arrays: { symbols, annual_returns, ... }
        if (data.symbols && data.annual_returns) {
          statsTableData.value = data.symbols.map((s, i) => ({
            symbol: s,
            annual_return: data.annual_returns[i],
            annual_volatility: data.annual_volatilities[i],
            sharpe_ratio: data.sharpe_ratios ? data.sharpe_ratios[i] : null,
            max_drawdown: data.max_drawdowns ? data.max_drawdowns[i] : null,
            total_return: data.total_returns ? data.total_returns[i] : null
          }));
        } else {
          statsTableData.value = [];
        }
      } catch (e) {
        console.error('fetchStatistics error:', e);
        statsData.value = null;
        statsTableData.value = [];
      }
    }

    /* ===================== TAB 1: DASHBOARD ===================== */
    async function loadDashboard() {
      await fetchStocks();
      // Fetch price history for each stock
      const historyPromises = stocks.value.map(s => fetchHistory(s.symbol));
      await Promise.all(historyPromises);
      await nextTick();
      // CRITICAL: deferred render with 200ms delay for el-tabs visibility
      setTimeout(() => {
        renderPriceChart();
        renderSparklines();
      }, 200);
    }

    function renderPriceChart() {
      const chart = getOrCreateChart('priceChart');
      if (!chart) return;

      const series = stocks.value.map((stock, idx) => {
        const history = stockHistories.value[stock.symbol] || [];
        return {
          name: stock.symbol,
          type: 'line',
          data: history.map(h => [h.date, h.close]),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5 },
          itemStyle: { color: COLORS[idx % COLORS.length] }
        };
      });

      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { top: 0, type: 'scroll', textStyle: { fontSize: 12 } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'time', boundaryGap: false },
        yAxis: { type: 'value', scale: true, name: 'Price ($)' },
        series
      });
    }

    function renderSparklines() {
      stocks.value.forEach((stock) => {
        const domId = `spark-${stock.symbol}`;
        const dom = document.getElementById(domId);
        if (!dom || dom.offsetWidth <= 0) return;

        if (chartInstances[domId]) {
          chartInstances[domId].dispose();
        }

        const chart = echarts.init(dom);
        chartInstances[domId] = chart;

        const history = stockHistories.value[stock.symbol] || [];
        const totalReturn = stock.total_return || 0;
        const color = totalReturn >= 0 ? '#FB4214' : '#67C23A';

        chart.setOption({
          grid: { left: 0, right: 0, top: 2, bottom: 2 },
          xAxis: { type: 'category', show: false, data: history.map(h => h.date) },
          yAxis: { type: 'value', show: false },
          series: [{
            type: 'line',
            data: history.map(h => h.close),
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 1.5, color },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: color + '40' },
                { offset: 1, color: color + '05' }
              ])
            }
          }]
        });
      });
    }

    /* ===================== TAB 2: STATISTICS ===================== */
    async function loadStatistics() {
      await fetchStatistics(statsTier.value);
      await nextTick();
      setTimeout(() => {
        renderReturnsChart();
        renderCorrelationHeatmap();
        renderRiskReturnChart();
      }, 200);
    }

    function renderReturnsChart() {
      const chart = getOrCreateChart('returnsChart');
      if (!chart) return;

      const tableData = statsTableData.value;
      if (!tableData.length) return;

      const symbols = tableData.map(d => d.symbol);
      const returns = tableData.map(d => (d.annual_return || 0) * 100);

      chart.setOption({
        tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: symbols, axisLabel: { rotate: 30, fontSize: 11 } },
        yAxis: { type: 'value', name: 'Annual Return (%)' },
        series: [{
          type: 'bar',
          data: returns.map((v, i) => ({
            value: v,
            itemStyle: { color: v >= 0 ? COLORS[i % COLORS.length] : '#F56C6C' }
          })),
          barMaxWidth: 40
        }]
      });
    }

    function renderCorrelationHeatmap() {
      const chart = getOrCreateChart('correlationChart');
      if (!chart) return;

      const data = statsData.value;
      if (!data) return;

      // API returns correlation_matrix as 2D array
      const symbols = data.symbols || [];
      const corrMatrix = data.correlation_matrix || data.correlation || [];

      if (!symbols.length || !corrMatrix.length) return;

      const heatData = [];
      for (let i = 0; i < symbols.length; i++) {
        for (let j = 0; j < symbols.length; j++) {
          heatData.push([i, j, corrMatrix[i][j]]);
        }
      }

      chart.setOption({
        tooltip: {
          formatter: function(p) {
            return `${symbols[p.data[0]]} vs ${symbols[p.data[1]]}: ${p.data[2].toFixed(3)}`;
          }
        },
        grid: { left: '15%', right: '10%', bottom: '15%', containLabel: false },
        xAxis: { type: 'category', data: symbols, axisLabel: { rotate: 30, fontSize: 10 }, splitArea: { show: true } },
        yAxis: { type: 'category', data: symbols, axisLabel: { fontSize: 10 }, splitArea: { show: true } },
        visualMap: {
          min: -1, max: 1, calculable: true,
          orient: 'horizontal', left: 'center', bottom: 0,
          inRange: { color: ['#1664FF', '#F3F7FF', '#FB4214'] }
        },
        series: [{
          type: 'heatmap',
          data: heatData,
          label: { show: symbols.length <= 8, fontSize: 9, formatter: p => p.data[2].toFixed(2) },
          emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } }
        }]
      });
    }

    function renderRiskReturnChart() {
      const chart = getOrCreateChart('riskReturnChart');
      if (!chart) return;

      const tableData = statsTableData.value;
      if (!tableData.length) return;

      const scatterData = tableData.map((d, i) => ({
        name: d.symbol,
        value: [(d.annual_volatility || 0) * 100, (d.annual_return || 0) * 100],
        itemStyle: { color: COLORS[i % COLORS.length] }
      }));

      chart.setOption({
        tooltip: {
          formatter: function(p) {
            return `${p.name}<br/>Risk: ${p.value[0].toFixed(2)}%<br/>Return: ${p.value[1].toFixed(2)}%`;
          }
        },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', name: 'Annual Volatility (%)', nameLocation: 'middle', nameGap: 25 },
        yAxis: { type: 'value', name: 'Annual Return (%)', nameLocation: 'middle', nameGap: 40 },
        series: [{
          type: 'scatter',
          data: scatterData,
          symbolSize: 16,
          label: { show: true, formatter: '{b}', position: 'top', fontSize: 11 }
        }]
      });
    }

    /* ===================== TAB 3: CLASSICAL OPTIMIZATION ===================== */
    async function runClassical() {
      classicalLoading.value = true;
      classicalResult.value = null;
      try {
        const result = await apiPost('/api/optimize/classical', {
          tier: classicalParams.tier,
          k: classicalParams.k,
          q: classicalParams.q
        });
        classicalResult.value = result;
        await nextTick();
        setTimeout(() => {
          renderEfficientFrontier();
          renderClassicalWeightsPie();
        }, 200);
      } catch (e) {
        console.error('runClassical error:', e);
        ElementPlus.ElMessage.error('经典优化运行失败: ' + e.message);
      } finally {
        classicalLoading.value = false;
      }
    }

    function renderEfficientFrontier() {
      const chart = getOrCreateChart('frontierChart');
      if (!chart || !classicalResult.value) return;

      const result = classicalResult.value;
      const frontier = result.efficient_frontier || [];

      // Frontier curve
      const frontierData = frontier.map(p => [p.risk * 100, p.return * 100]);

      const series = [
        {
          name: 'Effective Frontier',
          type: 'line',
          data: frontierData,
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#00C7E7', width: 2 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0,199,231,0.15)' },
              { offset: 1, color: 'rgba(0,199,231,0.02)' }
            ])
          }
        },
        {
          name: 'Optimal Portfolio',
          type: 'scatter',
          data: [[result.portfolio_risk * 100, result.portfolio_return * 100]],
          symbolSize: 14,
          itemStyle: { color: '#1664FF' },
          label: { show: true, formatter: 'Optimal', position: 'top', fontWeight: 'bold' }
        }
      ];

      // Individual stock risk-return points
      if (result.stock_points) {
        series.push({
          name: 'Individual Stocks',
          type: 'scatter',
          data: result.stock_points.map(p => [p.risk * 100, p.return * 100]),
          symbolSize: 10,
          itemStyle: { color: '#939AAB' },
          label: { show: true, formatter: p => p.name || '', fontSize: 10, position: 'right' }
        });
      }

      chart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: function(p) {
            if (p.seriesName === 'Effective Frontier') {
              return `Risk: ${p.value[0].toFixed(2)}%<br/>Return: ${p.value[1].toFixed(2)}%`;
            }
            return `${p.seriesName}<br/>Risk: ${p.value[0].toFixed(2)}%<br/>Return: ${p.value[1].toFixed(2)}%`;
          }
        },
        legend: { top: 0 },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', name: 'Risk (%)', nameLocation: 'middle', nameGap: 25 },
        yAxis: { type: 'value', name: 'Return (%)', nameLocation: 'middle', nameGap: 40 },
        series
      });
    }

    function renderClassicalWeightsPie() {
      const chart = getOrCreateChart('classicalWeightsPie');
      if (!chart || !classicalResult.value) return;

      // API returns weights as {symbol: weight} object
      const weights = classicalResult.value.weights || {};
      const data = Object.entries(weights).map(([k, v]) => ({
        name: k,
        value: Number((v * 100).toFixed(2))
      }));

      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
        legend: { orient: 'vertical', left: 'left', top: 'middle', textStyle: { fontSize: 12 } },
        series: [{
          type: 'pie',
          radius: ['35%', '65%'],
          center: ['60%', '50%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, formatter: '{b}\n{c}%', fontSize: 12 },
          data,
          color: PIE_COLORS
        }]
      });
    }

    /* ===================== TAB 4: QUANTUM OPTIMIZATION ===================== */
    async function runQuantum() {
      quantumLoading.value = true;
      quantumResult.value = null;
      try {
        const result = await apiPost('/api/optimize/quantum', {
          tier: quantumParams.tier,
          k: quantumParams.k,
          q: quantumParams.q,
          depth: quantumParams.depth,
          restarts: quantumParams.restarts
        });
        quantumResult.value = result;
        await nextTick();
        setTimeout(() => {
          renderProbabilityDist();
          renderQuantumWeightsPie();
        }, 200);
      } catch (e) {
        console.error('runQuantum error:', e);
        ElementPlus.ElMessage.error('量子优化运行失败: ' + e.message);
      } finally {
        quantumLoading.value = false;
      }
    }

    function renderProbabilityDist() {
      const chart = getOrCreateChart('probDistChart');
      if (!chart || !quantumResult.value) return;

      // API returns top_bitstrings: [{bitstring, probability, is_selected}]
      const topBitstrings = quantumResult.value.top_bitstrings || [];
      if (!topBitstrings.length) return;

      const labels = topBitstrings.map(b => b.bitstring || '');
      const probs = topBitstrings.map(b => b.probability || 0);

      // Highlight the selected solution
      const colors = topBitstrings.map(b => {
        if (b.is_selected) return '#1664FF';
        return '#4F9DF7';
      });

      chart.setOption({
        tooltip: { trigger: 'axis', formatter: '{b}<br/>Probability: {c}' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: labels,
          axisLabel: { rotate: 45, fontSize: 10, fontFamily: 'monospace' }
        },
        yAxis: { type: 'value', name: 'Probability' },
        series: [{
          type: 'bar',
          data: probs.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
          barMaxWidth: 30
        }]
      });
    }

    function renderQuantumWeightsPie() {
      const chart = getOrCreateChart('quantumWeightsPie');
      if (!chart || !quantumResult.value) return;

      // API returns weights as {symbol: weight} object
      const weights = quantumResult.value.weights || {};
      const data = Object.entries(weights).map(([k, v]) => ({
        name: k,
        value: Number((v * 100).toFixed(2))
      }));

      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
        legend: { orient: 'vertical', left: 'left', top: 'middle', textStyle: { fontSize: 12 } },
        series: [{
          type: 'pie',
          radius: ['35%', '65%'],
          center: ['60%', '50%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, formatter: '{b}\n{c}%', fontSize: 12 },
          data,
          color: PIE_COLORS
        }]
      });
    }

    /* ===================== TAB 5: COMPARE ===================== */
    const compareTableData = computed(() => {
      if (!compareResult.value) return [];
      // API returns: classical, quantum, bruteforce (not brute_force)
      const c = compareResult.value.classical || {};
      const q = compareResult.value.quantum || {};
      const b = compareResult.value.bruteforce || {};

      return [
        {
          metric: '组合收益率',
          classical: formatNum((c.portfolio_return || 0) * 100, 2) + '%',
          quantum: formatNum((q.portfolio_return || 0) * 100, 2) + '%',
          bruteforce: formatNum((b.portfolio_return || 0) * 100, 2) + '%'
        },
        {
          metric: '组合风险',
          classical: formatNum((c.portfolio_risk || 0) * 100, 2) + '%',
          quantum: formatNum((q.portfolio_risk || 0) * 100, 2) + '%',
          bruteforce: formatNum((b.portfolio_risk || 0) * 100, 2) + '%'
        },
        {
          metric: '夏普比率',
          classical: formatNum(c.sharpe_ratio || c.portfolio_sharpe || 0, 3),
          quantum: formatNum(q.sharpe_ratio || q.portfolio_sharpe || 0, 3),
          bruteforce: formatNum(b.sharpe_ratio || b.portfolio_sharpe || 0, 3)
        },
        {
          metric: 'QUBO 能量',
          classical: formatNum(c.qubo_energy || 0, 4),
          quantum: formatNum(q.qubo_energy || q.optimal_energy || 0, 4),
          bruteforce: formatNum(b.qubo_energy || b.optimal_energy || 0, 4)
        },
        {
          metric: 'Cost Gap',
          classical: '--',
          quantum: formatNum(q.cost_gap || 0, 2) + '%',
          bruteforce: '0.00%'
        },
        {
          metric: '量子比特数',
          classical: '--',
          quantum: String(q.n_qubits || '--'),
          bruteforce: '--'
        },
        {
          metric: '选中股票',
          classical: (c.selected_stocks || []).join(', '),
          quantum: (q.selected_stocks || []).join(', '),
          bruteforce: (b.selected_stocks || []).join(', ')
        }
      ];
    });

    async function runCompare() {
      compareLoading.value = true;
      compareResult.value = null;
      try {
        const result = await apiPost('/api/compare', {
          tier: compareParams.tier,
          k: compareParams.k,
          q: compareParams.q,
          depth: compareParams.depth,
          restarts: compareParams.restarts
        });
        compareResult.value = result;
        await nextTick();
        setTimeout(() => {
          renderComparisonScatter();
          renderCompareClassicalPie();
          renderCompareQuantumPie();
        }, 200);
      } catch (e) {
        console.error('runCompare error:', e);
        ElementPlus.ElMessage.error('对比分析运行失败: ' + e.message);
      } finally {
        compareLoading.value = false;
      }
    }

    function renderComparisonScatter() {
      const chart = getOrCreateChart('comparisonScatterChart');
      if (!chart || !compareResult.value) return;

      const c = compareResult.value.classical || {};
      const q = compareResult.value.quantum || {};
      const b = compareResult.value.bruteforce || {};

      const series = [];

      // Efficient frontier (top-level field in compare response)
      const frontier = compareResult.value.efficient_frontier || [];
      if (frontier.length) {
        series.push({
          name: '有效前沿',
          type: 'line',
          data: frontier.map(p => [p.risk * 100, p.return * 100]),
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#DCE0EB', width: 2, type: 'dashed' }
        });
      }

      // Classical point
      series.push({
        name: '经典优化',
        type: 'scatter',
        data: [[(c.portfolio_risk || 0) * 100, (c.portfolio_return || 0) * 100]],
        symbolSize: 16,
        itemStyle: { color: '#00C7E7' },
        label: { show: true, formatter: 'Classical', position: 'top', color: '#00C7E7', fontWeight: 'bold' }
      });

      // Quantum point
      series.push({
        name: '量子优化 (QAOA)',
        type: 'scatter',
        data: [[(q.portfolio_risk || 0) * 100, (q.portfolio_return || 0) * 100]],
        symbolSize: 16,
        itemStyle: { color: '#1664FF' },
        label: { show: true, formatter: 'QAOA', position: 'top', color: '#1664FF', fontWeight: 'bold' }
      });

      // Brute-force point
      series.push({
        name: '暴力搜索',
        type: 'scatter',
        data: [[(b.portfolio_risk || 0) * 100, (b.portfolio_return || 0) * 100]],
        symbolSize: 16,
        itemStyle: { color: '#FB4214' },
        label: { show: true, formatter: 'Brute-Force', position: 'right', color: '#FB4214', fontWeight: 'bold' }
      });

      chart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: function(p) {
            return `${p.seriesName}<br/>Risk: ${p.value[0].toFixed(2)}%<br/>Return: ${p.value[1].toFixed(2)}%`;
          }
        },
        legend: { top: 0, textStyle: { fontSize: 12 } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', name: 'Risk (%)', nameLocation: 'middle', nameGap: 25 },
        yAxis: { type: 'value', name: 'Return (%)', nameLocation: 'middle', nameGap: 40 },
        series
      });
    }

    function renderCompareClassicalPie() {
      const chart = getOrCreateChart('compareClassicalPie');
      if (!chart || !compareResult.value) return;

      const weights = compareResult.value.classical?.weights || {};
      const data = Object.entries(weights).map(([k, v]) => ({
        name: k,
        value: Number((v * 100).toFixed(2))
      }));

      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
        series: [{
          type: 'pie',
          radius: ['30%', '60%'],
          center: ['50%', '50%'],
          itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, formatter: '{b}\n{c}%', fontSize: 11 },
          data,
          color: PIE_COLORS
        }]
      });
    }

    function renderCompareQuantumPie() {
      const chart = getOrCreateChart('compareQuantumPie');
      if (!chart || !compareResult.value) return;

      const weights = compareResult.value.quantum?.weights || {};
      const data = Object.entries(weights).map(([k, v]) => ({
        name: k,
        value: Number((v * 100).toFixed(2))
      }));

      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
        series: [{
          type: 'pie',
          radius: ['30%', '60%'],
          center: ['50%', '50%'],
          itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, formatter: '{b}\n{c}%', fontSize: 11 },
          data,
          color: PIE_COLORS
        }]
      });
    }

    /* ===================== TAB CHANGE (CRITICAL for ECharts) ===================== */
    function onTabChange(tab) {
      // Deferred render: 200ms + nextTick ensures tab DOM is visible
      setTimeout(async () => {
        await nextTick();
        switch (tab) {
          case 'dashboard':
            renderPriceChart();
            renderSparklines();
            break;
          case 'statistics':
            if (statsData.value) {
              renderReturnsChart();
              renderCorrelationHeatmap();
              renderRiskReturnChart();
            } else {
              loadStatistics();
            }
            break;
          case 'classical':
            if (classicalResult.value) {
              renderEfficientFrontier();
              renderClassicalWeightsPie();
            }
            break;
          case 'quantum':
            if (quantumResult.value) {
              renderProbabilityDist();
              renderQuantumWeightsPie();
            }
            break;
          case 'compare':
            if (compareResult.value) {
              renderComparisonScatter();
              renderCompareClassicalPie();
              renderCompareQuantumPie();
            }
            break;
        }
      }, 200);
    }

    /* ===================== RESIZE ===================== */
    function handleResize() {
      Object.values(chartInstances).forEach(chart => {
        if (chart && !chart.isDisposed()) {
          chart.resize();
        }
      });
    }

    /* ===================== LIFECYCLE ===================== */
    onMounted(async () => {
      window.addEventListener('resize', handleResize);
      await loadDashboard();
    });

    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      disposeAllCharts();
    });

    /* ===================== EXPOSE TO TEMPLATE ===================== */
    return {
      activeTab,
      dashboardTier,
      statsTier,
      stocks,
      tiers,
      stockHistories,
      statsData,
      statsTableData,
      classicalParams,
      classicalResult,
      classicalLoading,
      quantumParams,
      quantumResult,
      quantumLoading,
      compareParams,
      compareResult,
      compareLoading,
      compareTableData,
      formatNum,
      loadDashboard,
      loadStatistics,
      runClassical,
      runQuantum,
      runCompare,
      onTabChange
    };
  }
});

app.use(ElementPlus);
app.mount('#app');
