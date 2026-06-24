<script setup>
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import GraphPanel from './components/GraphPanel.vue';
import ResultPanel from './components/ResultPanel.vue';
import ComparePanel from './components/ComparePanel.vue';
import { getGraphs, getGraph, solveQaoa, bruteForce } from '@/api/maxcutQaoa/index.js';

const { t } = useI18n();

const loading = ref(false);
const loadError = ref(false);
const solving = ref(false);
const bruteForcing = ref(false);
const graphList = ref([]);
const selectedGraph = ref('');
const currentGraph = reactive({ nodes: [], edges: [] });
const activeTab = ref('graphCut');

const qaoaParams = reactive({
  depth: 2,
  restarts: 5,
  maxiter: 200,
});

const qaoaResult = reactive({
  partition: [],
  cutEdges: [],
  cutValue: null,
  optimizationHistory: [],
  probabilities: [],
});

const bruteForceResult = reactive({
  optimalCut: null,
  optimalPartition: [],
  cutEdges: [],
});

const solveMeta = reactive({
  nQubits: null,
  circuitDepth: null,
  elapsedTime: null,
  costGap: null,
});

const hasResult = ref(false);
const hasBruteForce = ref(false);

const previewChartRef = ref(null);
let previewChart = null;
const graphPanelRef = ref(null);
const optimizationPanelRef = ref(null);
const probabilityPanelRef = ref(null);

async function loadGraphList() {
  loading.value = true;
  loadError.value = false;
  try {
    const res = await getGraphs();
    if (res.code === 200 && res.data) {
      graphList.value = res.data || [];
      if (graphList.value.length > 0) {
        selectedGraph.value = graphList.value[0].name;
        await loadGraphData(selectedGraph.value);
      }
    } else {
      loadError.value = true;
    }
  } catch {
    loadError.value = true;
    ElMessage.error(t('maxcutQaoa.noResult'));
  } finally {
    loading.value = false;
  }
}

async function loadGraphData(name) {
  if (!name) return;
  try {
    const res = await getGraph(name);
    if (res.code === 200 && res.data) {
      const data = res.data;
      currentGraph.nodes = data.nodes || [];
      currentGraph.edges = data.edges || [];
      renderPreviewChart();
    }
  } catch {
    ElMessage.error(t('maxcutQaoa.noResult'));
  }
}

function handleGraphChange(val) {
  loadGraphData(val);
}

function buildPreviewOption() {
  const nodes = currentGraph.nodes;
  const edges = currentGraph.edges;
  const seriesData = nodes.map((_, idx) => ({
    name: `V${idx}`,
    value: idx,
    symbolSize: 32,
    itemStyle: { color: '#1664FF', borderColor: '#FFFFFF', borderWidth: 2 },
    label: { show: true, color: '#FFFFFF', fontSize: 12, fontWeight: 'bold' },
  }));
  const seriesLinks = edges.map((edge) => ({
    source: `V${edge[0]}`,
    target: `V${edge[1]}`,
    lineStyle: { color: '#DCE0EB', width: 1.5 },
  }));
  return {
    tooltip: {},
    animation: false,
    series: [{
      type: 'graph',
      layout: 'force',
      data: seriesData,
      links: seriesLinks,
      roam: false,
      force: { repulsion: 150, edgeLength: [60, 120], gravity: 0.1 },
      label: { show: true, position: 'inside' },
    }],
  };
}

function renderPreviewChart() {
  nextTick(() => {
    setTimeout(() => {
      if (!previewChartRef.value || previewChartRef.value.offsetWidth === 0) return;
      if (!previewChart) {
        previewChart = echarts.init(previewChartRef.value);
      }
      previewChart.setOption(buildPreviewOption(), true);
    }, 200);
  });
}

function handleTabChange(tab) {
  nextTick(() => {
    setTimeout(() => {
      if (tab === 'graphCut' && graphPanelRef.value) {
        graphPanelRef.value.renderChart();
      }
      if (tab === 'optimization' && optimizationPanelRef.value) {
        optimizationPanelRef.value.renderAll();
      }
      if (tab === 'probability' && probabilityPanelRef.value) {
        probabilityPanelRef.value.renderAll();
      }
    }, 200);
  });
}

async function handleSolve() {
  if (solving.value) return;
  solving.value = true;
  try {
    const res = await solveQaoa({
      graphName: selectedGraph.value,
      depth: qaoaParams.depth,
      restarts: qaoaParams.restarts,
      maxiter: qaoaParams.maxiter,
    });
    if (res.code === 200 && res.data) {
      const data = res.data;
      qaoaResult.partition = data.partition || [];
      qaoaResult.cutEdges = data.cut_edges || data.cutEdges || [];
      qaoaResult.cutValue = data.cut_value ?? data.cutValue ?? null;
      qaoaResult.optimizationHistory = data.optimization_history || data.optimizationHistory || [];
      qaoaResult.probabilities = data.probabilities || [];
      solveMeta.nQubits = data.n_qubits ?? data.nQubits ?? currentGraph.nodes.length;
      solveMeta.circuitDepth = data.circuit_depth ?? data.circuitDepth ?? null;
      solveMeta.elapsedTime = data.elapsed_time ?? data.elapsedTime ?? null;
      hasResult.value = true;
      ElMessage.success(t('maxcutQaoa.startSolve'));
      nextTick(() => {
        setTimeout(() => {
          if (graphPanelRef.value) {
            graphPanelRef.value.renderChart();
          }
        }, 200);
      });
    } else {
      ElMessage.error(t('maxcutQaoa.noResult'));
    }
  } catch {
    ElMessage.error(t('maxcutQaoa.noResult'));
  } finally {
    solving.value = false;
  }
}

async function handleBruteForce() {
  if (bruteForcing.value) return;
  bruteForcing.value = true;
  try {
    const res = await bruteForce({ graphName: selectedGraph.value });
    if (res.code === 200 && res.data) {
      const data = res.data;
      bruteForceResult.optimalCut = data.optimal_cut ?? data.optimalCut ?? null;
      bruteForceResult.optimalPartition = data.optimal_partition ?? data.optimalPartition ?? [];
      bruteForceResult.cutEdges = data.cut_edges ?? data.cutEdges ?? [];
      hasBruteForce.value = true;
      if (qaoaResult.cutValue !== null && bruteForceResult.optimalCut !== null) {
        solveMeta.costGap = bruteForceResult.optimalCut > 0
          ? ((bruteForceResult.optimalCut - qaoaResult.cutValue) / bruteForceResult.optimalCut) * 100
          : 0;
      }
    } else {
      ElMessage.error(t('maxcutQaoa.noResult'));
    }
  } catch {
    ElMessage.error(t('maxcutQaoa.noResult'));
  } finally {
    bruteForcing.value = false;
  }
}

onMounted(() => {
  loadGraphList();
});

onBeforeUnmount(() => {
  if (previewChart) {
    previewChart.dispose();
    previewChart = null;
  }
});
</script>

<template>
  <main class="maxcut-qaoa-page">
    <section class="banner-section">
      <div class="banner-content">
        <h1 class="banner-title">{{ $t('maxcutQaoa.title') }}</h1>
        <p class="banner-subtitle">{{ $t('maxcutQaoa.subtitle') }}</p>
      </div>
    </section>

    <section class="content-section" v-loading="loading">
      <div class="section-card">
        <div class="card-header">
          <h2 class="card-title">{{ $t('maxcutQaoa.selectGraph') }}</h2>
        </div>
        <div class="graph-select-row">
          <div class="select-area">
            <el-select
              v-model="selectedGraph"
              :placeholder="$t('maxcutQaoa.selectGraph')"
              @change="handleGraphChange"
              style="width: 280px"
            >
              <el-option
                v-for="g in graphList"
                :key="g.name"
                :label="g.label || g.name"
                :value="g.name"
              />
            </el-select>
            <div class="graph-info" v-if="currentGraph.nodes.length > 0">
              <div class="info-item">
                <span class="info-label">{{ $t('maxcutQaoa.nodeCount') }}:</span>
                <span class="info-value">{{ currentGraph.nodes.length }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">{{ $t('maxcutQaoa.edgeCount') }}:</span>
                <span class="info-value">{{ currentGraph.edges.length }}</span>
              </div>
            </div>
          </div>
          <div class="preview-area">
            <div ref="previewChartRef" class="preview-chart" />
          </div>
        </div>
      </div>
    </section>

    <section class="content-section">
      <div class="section-card">
        <div class="card-header">
          <h2 class="card-title">{{ $t('maxcutQaoa.qaoaDepth') }}</h2>
        </div>
        <div class="params-row">
          <el-form :model="qaoaParams" label-width="120px" inline>
            <el-form-item :label="$t('maxcutQaoa.qaoaDepth')">
              <el-input-number
                v-model="qaoaParams.depth"
                :min="1"
                :max="10"
                :step="1"
              />
            </el-form-item>
            <el-form-item :label="$t('maxcutQaoa.restarts')">
              <el-input-number
                v-model="qaoaParams.restarts"
                :min="1"
                :max="20"
                :step="1"
              />
            </el-form-item>
            <el-form-item :label="$t('maxcutQaoa.maxIterations')">
              <el-input-number
                v-model="qaoaParams.maxiter"
                :min="50"
                :max="2000"
                :step="50"
              />
            </el-form-item>
          </el-form>
          <div class="action-buttons">
            <el-button
              type="primary"
              :loading="solving"
              @click="handleSolve"
            >
              {{ solving ? $t('maxcutQaoa.solving') : $t('maxcutQaoa.startSolve') }}
            </el-button>
            <el-button
              :loading="bruteForcing"
              @click="handleBruteForce"
            >
              {{ $t('maxcutQaoa.bruteForce') }}
            </el-button>
          </div>
        </div>
      </div>
    </section>

    <section class="content-section" v-if="hasResult">
      <div class="section-card">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane :label="$t('maxcutQaoa.tabGraphCut')" name="graphCut">
            <div class="tab-content">
              <GraphPanel
                ref="graphPanelRef"
                :graph-data="currentGraph"
                :partition="qaoaResult.partition"
                :cut-edges="qaoaResult.cutEdges"
              />
              <div class="cut-info" v-if="qaoaResult.cutValue !== null">
                <span class="cut-label">{{ $t('maxcutQaoa.qaoaCutValue') }}:</span>
                <span class="cut-value">{{ qaoaResult.cutValue }}</span>
                <span class="cut-label" style="margin-left: 20px">{{ $t('maxcutQaoa.cutEdges') }}:</span>
                <span class="cut-value">{{ qaoaResult.cutEdges.length }}</span>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('maxcutQaoa.tabOptimization')" name="optimization">
            <div class="tab-content">
              <ResultPanel
                ref="optimizationPanelRef"
                :optimization-history="qaoaResult.optimizationHistory"
                :probabilities="[]"
                :best-partition="qaoaResult.partition"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('maxcutQaoa.tabProbability')" name="probability">
            <div class="tab-content">
              <ResultPanel
                ref="probabilityPanelRef"
                :optimization-history="[]"
                :probabilities="qaoaResult.probabilities"
                :best-partition="qaoaResult.partition"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('maxcutQaoa.tabCompare')" name="compare">
            <div class="tab-content">
              <ComparePanel
                :qaoa-cut="qaoaResult.cutValue"
                :optimal-cut="bruteForceResult.optimalCut"
                :cost-gap="solveMeta.costGap"
                :n-qubits="solveMeta.nQubits"
                :circuit-depth="solveMeta.circuitDepth"
                :elapsed-time="solveMeta.elapsedTime"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </section>

    <section class="content-section" v-if="!hasResult && !loading">
      <div class="section-card empty-card">
        <el-empty v-if="!loadError" :description="$t('maxcutQaoa.noResult')" />
        <div v-else class="error-retry">
          <el-button type="primary" @click="loadGraphList">{{ $t('maxcutQaoa.startSolve') }}</el-button>
        </div>
      </div>
    </section>
  </main>
</template>

<style lang="scss" scoped>
.maxcut-qaoa-page {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #F4F7FC;
}

.banner-section {
  background: #1664FF;
  padding: 60px 0;
}

.banner-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 140px;
}

.banner-title {
  font-size: 40px;
  font-weight: bold;
  color: #FFFFFF;
  margin: 0 0 16px 0;
}

.banner-subtitle {
  font-size: 20px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
}

.content-section {
  max-width: 1440px;
  margin: 0 auto;
  padding: 20px 140px;
}

.section-card {
  background: #FFFFFF;
  border: 1px solid #DCE0EB;
  border-radius: 8px;
  padding: 30px;
}

.card-header {
  margin-bottom: 20px;
}

.card-title {
  font-size: 24px;
  font-weight: 400;
  color: #020814;
  margin: 0;
}

.graph-select-row {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.select-area {
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.graph-info {
  display: flex;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-label {
  font-size: 14px;
  color: #939AAB;
}

.info-value {
  font-size: 18px;
  color: #020814;
}

.preview-area {
  flex: 1;
  min-width: 0;
}

.preview-chart {
  width: 100%;
  height: 300px;
  min-height: 200px;
}

.params-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 20px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
  padding-top: 4px;
}

.tab-content {
  padding: 20px 0;
}

.cut-info {
  margin-top: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.cut-label {
  font-size: 14px;
  color: #939AAB;
}

.cut-value {
  font-size: 18px;
  color: #020814;
}

.empty-card {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.error-retry {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

@media (max-width: 1440px) {
  .banner-content,
  .content-section {
    padding-left: 60px;
    padding-right: 60px;
  }

  .graph-select-row {
    flex-direction: column;
  }

  .select-area {
    flex: none;
    width: 100%;
  }
}
</style>
