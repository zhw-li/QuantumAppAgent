/* ========================================
   QAOA MaxCut 量子优化求解器 - 应用逻辑
   Vue 3 CDN + Element Plus + ECharts
   ======================================== */

const { createApp, ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } = Vue;

const app = createApp({
  setup() {
    // ========== 图数据 ==========
    const graphList = ref([]);
    const selectedGraphName = ref('');
    const currentGraph = ref(null);
    const graphLoading = ref(false);

    // ========== 参数配置 ==========
    const qaoaDepth = ref(2);
    const restarts = ref(5);
    const maxIterations = ref(300);

    // ========== 求解状态 ==========
    const solving = ref(false);
    const bruteForcing = ref(false);
    const activeTab = ref('graph-cut');

    // ========== 结果数据 ==========
    const qaoaResult = ref(null);
    const bruteForceResult = ref(null);

    // ========== ECharts 实例管理 ==========
    const chartInstances = {};

    // 图名称映射
    const graphNameMap = {
      'simple_4': '简单4节点图（三角形+悬挂）',
      'medium_6': '中等6节点图（环+对角线）',
      'large_8': '复杂8节点图（稠密图）'
    };

    // ========== 计算属性：分区 ==========
    const partitionSet0 = computed(() => {
      if (!qaoaResult.value || !qaoaResult.value.best_partition) return [];
      return qaoaResult.value.best_partition
        .map((v, i) => v === 0 ? i : -1)
        .filter(i => i >= 0);
    });

    const partitionSet1 = computed(() => {
      if (!qaoaResult.value || !qaoaResult.value.best_partition) return [];
      return qaoaResult.value.best_partition
        .map((v, i) => v === 1 ? i : -1)
        .filter(i => i >= 0);
    });

    // ========== API 调用 ==========
    async function fetchGraphs() {
      try {
        const resp = await fetch('/api/graphs');
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        graphList.value = data.graphs || [];
        if (graphList.value.length > 0) {
          selectedGraphName.value = graphList.value[0].name;
          await loadGraph(selectedGraphName.value);
        }
      } catch (e) {
        ElementPlus.ElMessage.error('获取图列表失败: ' + e.message);
      }
    }

    async function loadGraph(name) {
      graphLoading.value = true;
      try {
        const resp = await fetch(`/api/graph/${name}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        currentGraph.value = data;
        await nextTick();
        renderGraphPreview();
      } catch (e) {
        ElementPlus.ElMessage.error('加载图数据失败: ' + e.message);
      } finally {
        graphLoading.value = false;
      }
    }

    async function runQAOA() {
      if (!currentGraph.value) {
        ElementPlus.ElMessage.warning('请先选择图');
        return;
      }
      solving.value = true;
      qaoaResult.value = null;
      try {
        const resp = await fetch('/api/solve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            graph_name: selectedGraphName.value,
            depth: qaoaDepth.value,
            restarts: restarts.value,
            maxiter: maxIterations.value
          })
        });
        if (!resp.ok) {
          const errData = await resp.json().catch(() => ({}));
          throw new Error(errData.detail || `HTTP ${resp.status}`);
        }
        const data = await resp.json();
        qaoaResult.value = data;
        await nextTick();
        renderResultCharts();
      } catch (e) {
        ElementPlus.ElMessage.error('QAOA 求解失败: ' + e.message);
      } finally {
        solving.value = false;
      }
    }

    async function runBruteForce() {
      if (!currentGraph.value) {
        ElementPlus.ElMessage.warning('请先选择图');
        return;
      }
      bruteForcing.value = true;
      bruteForceResult.value = null;
      try {
        const resp = await fetch('/api/brute-force', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ graph_name: selectedGraphName.value })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        bruteForceResult.value = data;
        // 如果 QAOA 结果已存在，刷新对比 Tab
        if (qaoaResult.value) {
          await nextTick();
          if (activeTab.value === 'comparison') {
            delayedRenderChart('comparison-chart');
          }
        }
      } catch (e) {
        ElementPlus.ElMessage.error('暴力搜索失败: ' + e.message);
      } finally {
        bruteForcing.value = false;
      }
    }

    // ========== 图选择变更 ==========
    watch(selectedGraphName, async (newName) => {
      if (newName) {
        await loadGraph(newName);
      }
    });

    // ========== Tab 切换 ==========
    function onTabChange(tab) {
      const tabName = typeof tab === 'string' ? tab : (tab.paneName || tab.props?.name);
      activeTab.value = tabName;
      // 延迟渲染当前 Tab 中的图表（解决 el-tabs display:none 问题）
      setTimeout(() => {
        renderActiveTabCharts(tabName);
      }, 200);
    }

    function renderActiveTabCharts(tabName) {
      switch (tabName) {
        case 'graph-cut':
          renderCutGraph();
          break;
        case 'optimization':
          renderOptimizationChart();
          break;
        case 'probability':
          renderProbabilityChart();
          break;
        case 'comparison':
          renderComparisonChart();
          break;
      }
    }

    // ========== ECharts 工具 ==========
    function getOrCreateChart(domId) {
      const dom = document.getElementById(domId);
      if (!dom || dom.offsetWidth === 0) return null;
      // 销毁旧实例
      if (chartInstances[domId]) {
        chartInstances[domId].dispose();
        delete chartInstances[domId];
      }
      const instance = echarts.init(dom);
      chartInstances[domId] = instance;
      return instance;
    }

    function delayedRenderChart(domId, renderFn) {
      setTimeout(() => {
        const instance = getOrCreateChart(domId);
        if (instance && renderFn) {
          renderFn(instance);
        }
      }, 200);
    }

    // ========== 图预览渲染 ==========
    function renderGraphPreview() {
      if (!currentGraph.value) return;
      const instance = getOrCreateChart('graph-preview-chart');
      if (!instance) return;

      const graph = currentGraph.value;
      const nodes = [];
      for (let i = 0; i < graph.n_nodes; i++) {
        nodes.push({ name: String(i), symbolSize: 36 });
      }
      const links = graph.edges.map(e => ({
        source: String(e[0]),
        target: String(e[1])
      }));

      instance.setOption({
        tooltip: {},
        animation: false,
        series: [{
          type: 'graph',
          layout: 'force',
          roam: false,
          data: nodes,
          links: links,
          label: {
            show: true,
            fontSize: 14,
            color: '#FFFFFF',
            fontWeight: 'bold'
          },
          edgeSymbol: ['none', 'none'],
          edgeSymbolSize: 8,
          itemStyle: {
            color: '#1664FF',
            borderColor: '#4F9DF7',
            borderWidth: 2
          },
          lineStyle: {
            color: '#DCE0EB',
            width: 2
          },
          force: {
            repulsion: 200,
            edgeLength: 120,
            gravity: 0.1
          }
        }]
      });
    }

    // ========== 结果图表渲染 ==========
    function renderResultCharts() {
      // 渲染当前活跃 Tab 的图表
      renderActiveTabCharts(activeTab.value);
    }

    // Tab1: 图与割集
    function renderCutGraph() {
      if (!qaoaResult.value || !currentGraph.value) return;
      const instance = getOrCreateChart('cut-graph-chart');
      if (!instance) return;

      const graph = currentGraph.value;
      const result = qaoaResult.value;
      const partition = result.best_partition;

      // 分区颜色
      const colorA = '#1664FF';
      const colorB = '#4F9DF7';
      const cutEdgeColor = '#FB4214';
      const normalEdgeColor = '#DCE0EB';

      const nodes = [];
      for (let i = 0; i < graph.n_nodes; i++) {
        nodes.push({
          name: String(i),
          symbolSize: 44,
          itemStyle: {
            color: partition[i] === 0 ? colorA : colorB,
            borderColor: partition[i] === 0 ? '#0D47D1' : '#3A8AE0',
            borderWidth: 2
          }
        });
      }

      // 判断边是否在割集中
      const cutEdgesSet = new Set(
        (result.cut_edges || []).map(e => `${Math.min(e[0], e[1])}-${Math.max(e[0], e[1])}`)
      );

      const links = graph.edges.map(e => {
        const key = `${Math.min(e[0], e[1])}-${Math.max(e[0], e[1])}`;
        const isCut = cutEdgesSet.has(key);
        return {
          source: String(e[0]),
          target: String(e[1]),
          lineStyle: {
            color: isCut ? cutEdgeColor : normalEdgeColor,
            width: isCut ? 3 : 2,
            type: isCut ? 'solid' : 'dashed'
          }
        };
      });

      instance.setOption({
        tooltip: {
          formatter: (params) => {
            if (params.dataType === 'node') {
              const idx = parseInt(params.name);
              return `节点 ${idx} - 分区 ${partition[idx] === 0 ? 'A (S\u2080)' : 'B (S\u2081)'}`;
            }
            if (params.dataType === 'edge') {
              const key = `${Math.min(+params.data.source, +params.data.target)}-${Math.max(+params.data.source, +params.data.target)}`;
              return `边 ${params.data.source}-${params.data.target} ${cutEdgesSet.has(key) ? '(割边)' : ''}`;
            }
            return '';
          }
        },
        animation: false,
        series: [{
          type: 'graph',
          layout: 'force',
          roam: false,
          data: nodes,
          links: links,
          label: {
            show: true,
            fontSize: 16,
            color: '#FFFFFF',
            fontWeight: 'bold'
          },
          edgeSymbol: ['none', 'none'],
          force: {
            repulsion: 250,
            edgeLength: 140,
            gravity: 0.1
          }
        }]
      });
    }

    // Tab2: 优化过程
    function renderOptimizationChart() {
      if (!qaoaResult.value) return;
      const instance = getOrCreateChart('optimization-chart');
      if (!instance) return;

      const history = qaoaResult.value.optimization_history || [];
      const xData = history.map((_, i) => i + 1);

      instance.setOption({
        tooltip: {
          trigger: 'axis',
          formatter: (params) => `迭代 ${params[0].axisValue}<br/>期望值: ${params[0].value.toFixed(4)}`
        },
        grid: { left: 60, right: 30, top: 30, bottom: 40 },
        xAxis: {
          type: 'category',
          data: xData,
          name: '迭代次数',
          nameTextStyle: { color: '#939AAB', fontSize: 14 },
          axisLine: { lineStyle: { color: '#DCE0EB' } },
          axisLabel: { color: '#939AAB' }
        },
        yAxis: {
          type: 'value',
          name: '期望值',
          nameTextStyle: { color: '#939AAB', fontSize: 14 },
          axisLine: { lineStyle: { color: '#DCE0EB' } },
          axisLabel: { color: '#939AAB' },
          splitLine: { lineStyle: { color: '#F4F7FC' } }
        },
        series: [{
          type: 'line',
          data: history,
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#1664FF', width: 2 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(22, 100, 255, 0.15)' },
              { offset: 1, color: 'rgba(22, 100, 255, 0.02)' }
            ])
          }
        }]
      });
    }

    // Tab3: 概率分布
    function renderProbabilityChart() {
      if (!qaoaResult.value) return;
      const instance = getOrCreateChart('probability-chart');
      if (!instance) return;

      // 后端返回 top_probabilities: [{bitstring, probability, cut_value}, ...]
      const topProbs = qaoaResult.value.top_probabilities || [];
      if (topProbs.length === 0) return;

      // 找最优分区对应的 bitstring
      const bestPartition = qaoaResult.value.best_partition || [];
      const bestBitstring = bestPartition.join('');
      const xData = topProbs.map(e => e.bitstring);
      const yData = topProbs.map(e => e.probability);
      const colors = xData.map(bitstr =>
        bitstr === bestBitstring ? '#1664FF' : '#4F9DF7'
      );

      instance.setOption({
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const d = params[0];
            const isBest = d.name === bestBitstring;
            const entry = topProbs[d.dataIndex];
            return `${d.name}${isBest ? ' (最优)' : ''}<br/>概率: ${d.value.toFixed(4)}<br/>割值: ${entry ? entry.cut_value : '-'}`;
          }
        },
        grid: { left: 60, right: 30, top: 30, bottom: 40 },
        xAxis: {
          type: 'category',
          data: xData,
          name: '比特串',
          nameTextStyle: { color: '#939AAB', fontSize: 14 },
          axisLine: { lineStyle: { color: '#DCE0EB' } },
          axisLabel: {
            color: '#41464F',
            fontSize: 12,
            rotate: (xData.length > 0 && xData[0].length > 6) ? 30 : 0
          }
        },
        yAxis: {
          type: 'value',
          name: '概率',
          nameTextStyle: { color: '#939AAB', fontSize: 14 },
          axisLine: { lineStyle: { color: '#DCE0EB' } },
          axisLabel: { color: '#939AAB' },
          splitLine: { lineStyle: { color: '#F4F7FC' } }
        },
        series: [{
          type: 'bar',
          data: yData.map((v, i) => ({
            value: v,
            itemStyle: { color: colors[i], borderRadius: [4, 4, 0, 0] }
          })),
          barMaxWidth: 40
        }]
      });
    }

    // Tab4: 结果对比
    function renderComparisonChart() {
      if (!qaoaResult.value) return;
      const instance = getOrCreateChart('comparison-chart');
      if (!instance) return;

      const qaoaCut = qaoaResult.value.qaoa_cut || 0;
      const optimalCut = qaoaResult.value.optimal_cut || (bruteForceResult.value ? bruteForceResult.value.optimal_cut : 0);

      instance.setOption({
        tooltip: {
          trigger: 'axis'
        },
        grid: { left: 60, right: 30, top: 30, bottom: 40 },
        xAxis: {
          type: 'category',
          data: ['QAOA', '暴力搜索最优'],
          axisLine: { lineStyle: { color: '#DCE0EB' } },
          axisLabel: { color: '#41464F', fontSize: 16 }
        },
        yAxis: {
          type: 'value',
          name: '割值',
          nameTextStyle: { color: '#939AAB', fontSize: 14 },
          axisLine: { lineStyle: { color: '#DCE0EB' } },
          axisLabel: { color: '#939AAB' },
          splitLine: { lineStyle: { color: '#F4F7FC' } }
        },
        series: [{
          type: 'bar',
          data: [
            {
              value: qaoaCut,
              itemStyle: { color: '#1664FF', borderRadius: [4, 4, 0, 0] }
            },
            {
              value: optimalCut,
              itemStyle: { color: '#4F9DF7', borderRadius: [4, 4, 0, 0] }
            }
          ],
          barMaxWidth: 60,
          label: {
            show: true,
            position: 'top',
            fontSize: 16,
            color: '#020814',
            fontWeight: 'bold'
          }
        }]
      });
    }

    // ========== 计算属性 ==========
    const graphDescription = computed(() => {
      if (!currentGraph.value) return '';
      return currentGraph.value.description || '';
    });

    const hasQaoaResult = computed(() => qaoaResult.value !== null);
    const hasBruteForceResult = computed(() => bruteForceResult.value !== null);

    // ========== 生命周期 ==========
    onMounted(() => {
      fetchGraphs();
      window.addEventListener('resize', handleResize);
    });

    onBeforeUnmount(() => {
      // 销毁所有 ECharts 实例
      Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
          chartInstances[key].dispose();
          delete chartInstances[key];
        }
      });
      window.removeEventListener('resize', handleResize);
    });

    function handleResize() {
      Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
          chartInstances[key].resize();
        }
      });
    }

    return {
      // 图数据
      graphList,
      selectedGraphName,
      currentGraph,
      graphLoading,
      graphNameMap,
      graphDescription,

      // 参数
      qaoaDepth,
      restarts,
      maxIterations,

      // 状态
      solving,
      bruteForcing,
      activeTab,

      // 结果
      qaoaResult,
      bruteForceResult,
      hasQaoaResult,
      hasBruteForceResult,

      // 分区
      partitionSet0,
      partitionSet1,

      // 方法
      runQAOA,
      runBruteForce,
      onTabChange
    };
  }
});

app.use(ElementPlus);
app.mount('#app');
