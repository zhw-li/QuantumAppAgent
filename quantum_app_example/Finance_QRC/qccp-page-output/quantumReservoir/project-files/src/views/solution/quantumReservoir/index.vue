<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';

import Footer from '@/components/Footer.vue';

import MetricsCard from './components/MetricsCard.vue';
import PredictionChart from './components/PredictionChart.vue';
import ReservoirScatter from './components/ReservoirScatter.vue';
import CircuitInfo from './components/CircuitInfo.vue';

import api from '@/api/quantumReservoir/index.js';
import { DEFAULT_STOCKS, DEFAULT_PARAMS } from './data.js';

const { locale, t } = useI18n();

// --- State ---
const selectedStock = ref('AAPL');
const stocks = ref([...DEFAULT_STOCKS]);
const params = reactive({ ...DEFAULT_PARAMS });
const loading = ref(false);
const loadError = ref(false);
const hasResult = ref(false);

const solveResult = ref(null);
const comparisonData = ref(null);
const comparisonLoading = ref(false);
const activeTab = ref('prediction');

// Chart refs
const predictionChartRef = ref(null);
const reservoirScatterRef = ref(null);
const compareChartRef = ref(null);
let compareChartInstance = null;

// --- Computed ---
const classicMetrics = computed(() => solveResult.value?.metrics?.classic || {});
const quantumMetrics = computed(() => solveResult.value?.metrics?.quantum || {});
const predictions = computed(() => solveResult.value?.predictions || null);
const reservoirStates = computed(() => solveResult.value?.reservoir_states || null);
const circuitInfo = computed(() => solveResult.value?.circuit_info || null);

const paramEfficiency = computed(() => {
  const cParams = classicMetrics.value?.param_count;
  const qParams = quantumMetrics.value?.param_count;
  if (!cParams || !qParams) return { classic: '-', quantum: '-' };
  return { classic: cParams, quantum: qParams };
});

// --- API Layer ---
// 直接调用真实后端（Finance_QRC FastAPI, port 8009），经 api 模块适配响应结构。
// 集成进 qccp-web 后由网关/代理把 /api 转发到后端服务。

// --- Actions ---
async function handleSolve() {
  loading.value = true;
  loadError.value = false;
  hasResult.value = false;

  try {
    const payload = {
      ticker: selectedStock.value,
      ...params
    };

    // 1. 主实验：/api/solve（含 classic + quantum 指标与预测）
    const result = await api.solve(payload);

    // 2. 并行加载储备池状态散点与电路信息（这两个是独立端点）
    const query = {
      ticker: selectedStock.value,
      n_qubits: params.n_qubits,
      depth: params.depth,
      window_size: params.window_size
    };
    const [reservoirStates, circuitInfo] = await Promise.all([
      api.getReservoirStates(query).catch(() => null),
      api.getCircuitInfo({ n_qubits: params.n_qubits, depth: params.depth }).catch(() => null)
    ]);

    if (result && result.success !== false) {
      solveResult.value = {
        ...result,
        reservoir_states: reservoirStates,
        circuit_info: circuitInfo
      };
      hasResult.value = true;
      ElMessage.success(t('quantumReservoir.message.solveSuccess'));
    } else {
      loadError.value = true;
      ElMessage.error(t('quantumReservoir.message.solveFailed'));
    }
  } catch (error) {
    loadError.value = true;
    ElMessage.error(t('quantumReservoir.message.networkError'));
  } finally {
    loading.value = false;
  }
}

async function loadComparison() {
  if (comparisonData.value) return;
  comparisonLoading.value = true;
  try {
    const result = await api.getCompare();
    if (result) {
      comparisonData.value = result;
    }
  } catch (error) {
    ElMessage.error(t('quantumReservoir.message.networkError'));
  } finally {
    comparisonLoading.value = false;
  }
}

function handleRetry() {
  if (hasResult.value || !loadError.value) return;
  handleSolve();
}

// --- Tab switch with ECharts fix ---
function onTabChange(tab) {
  activeTab.value = tab;

  nextTick(() => {
    setTimeout(() => {
      if (tab === 'prediction' && predictionChartRef.value) {
        predictionChartRef.value.deferredRender();
      } else if (tab === 'scatter' && reservoirScatterRef.value) {
        reservoirScatterRef.value.deferredRender();
      } else if (tab === 'compare') {
        initCompareChart();
      }
    }, 200);
  });
}

// --- Compare chart ---
function initCompareChart() {
  if (!compareChartRef.value || compareChartRef.value.offsetWidth <= 0) return;
  if (!comparisonData.value) return;

  if (compareChartInstance) {
    compareChartInstance.dispose();
    compareChartInstance = null;
  }

  compareChartInstance = echarts.init(compareChartRef.value);

  const data = comparisonData.value;
  const tickers = data.map(d => d.ticker);
  const classicRMSE = data.map(d => d.classic_RMSE);
  const quantumRMSE = data.map(d => d.quantum_RMSE);

  compareChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: {
      data: [
        t('quantumReservoir.compare.classicRMSE'),
        t('quantumReservoir.compare.quantumRMSE')
      ],
      top: 0
    },
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category',
      data: tickers,
      axisLabel: { color: '#939aab' },
      axisLine: { lineStyle: { color: '#dce0eb' } }
    },
    yAxis: {
      type: 'value',
      name: 'RMSE',
      axisLabel: { color: '#939aab' },
      splitLine: { lineStyle: { color: '#dce0eb', type: 'dashed' } }
    },
    series: [
      {
        name: t('quantumReservoir.compare.classicRMSE'),
        type: 'bar',
        data: classicRMSE,
        itemStyle: { color: '#41464f', borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      },
      {
        name: t('quantumReservoir.compare.quantumRMSE'),
        type: 'bar',
        data: quantumRMSE,
        itemStyle: { color: '#1664ff', borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      }
    ]
  }, true);
}

// --- Compare table columns ---
const compareTableColumns = computed(() => [
  { prop: 'ticker', label: t('quantumReservoir.compare.ticker'), width: 100 },
  { prop: 'classic_RMSE', label: t('quantumReservoir.compare.classicRMSE'), width: 140 },
  { prop: 'quantum_RMSE', label: t('quantumReservoir.compare.quantumRMSE'), width: 140 },
  { prop: 'classic_MAE', label: t('quantumReservoir.compare.classicMAE'), width: 140 },
  { prop: 'quantum_MAE', label: t('quantumReservoir.compare.quantumMAE'), width: 140 },
  { prop: 'classic_params', label: t('quantumReservoir.compare.classicParams'), width: 130 },
  { prop: 'quantum_params', label: t('quantumReservoir.compare.quantumParams'), width: 130 }
]);

// --- Lifecycle ---
onMounted(async () => {
  // Pre-load comparison data
  await loadComparison();
});

onBeforeUnmount(() => {
  if (compareChartInstance) {
    compareChartInstance.dispose();
    compareChartInstance = null;
  }
});
</script>

<template>
  <main class="quantum-reservoir-page">
    <!-- Section 1: Banner -->
    <section class="quantum-reservoir-page__banner">
      <div class="wrapper">
        <h1 class="quantum-reservoir-page__banner-title">
          {{ $t('quantumReservoir.banner.title') }}
        </h1>
        <p class="quantum-reservoir-page__banner-subtitle">
          {{ $t('quantumReservoir.banner.subtitle') }}
        </p>
      </div>
    </section>

    <!-- Section 2: Stock & Parameters Panel -->
    <section class="quantum-reservoir-page__controls wrapper">
      <el-card class="quantum-reservoir-page__controls-card">
        <div class="quantum-reservoir-page__controls-header">
          <div class="quantum-reservoir-page__stock-select">
            <span class="quantum-reservoir-page__label">
              {{ $t('quantumReservoir.controls.stock') }}
            </span>
            <el-select
              v-model="selectedStock"
              :placeholder="$t('quantumReservoir.controls.stockPlaceholder')"
              style="width: 160px"
            >
              <el-option
                v-for="s in stocks"
                :key="s"
                :label="s"
                :value="s"
              />
            </el-select>
          </div>
          <el-button
            type="primary"
            :loading="loading"
            :disabled="loading"
            @click="handleSolve"
          >
            {{ loading ? $t('quantumReservoir.controls.solving') : $t('quantumReservoir.controls.solve') }}
          </el-button>
        </div>

        <div class="quantum-reservoir-page__params-grid">
          <div class="quantum-reservoir-page__param-item">
            <span class="quantum-reservoir-page__label">
              {{ $t('quantumReservoir.controls.nQubits') }}
            </span>
            <el-radio-group v-model="params.n_qubits" size="small">
              <el-radio-button :value="4">4</el-radio-button>
              <el-radio-button :value="6">6</el-radio-button>
              <el-radio-button :value="8">8</el-radio-button>
            </el-radio-group>
          </div>

          <div class="quantum-reservoir-page__param-item">
            <span class="quantum-reservoir-page__label">
              {{ $t('quantumReservoir.controls.depth') }}
            </span>
            <el-radio-group v-model="params.depth" size="small">
              <el-radio-button :value="2">2</el-radio-button>
              <el-radio-button :value="3">3</el-radio-button>
            </el-radio-group>
          </div>

          <div class="quantum-reservoir-page__param-item">
            <span class="quantum-reservoir-page__label">
              {{ $t('quantumReservoir.controls.windowSize') }}
            </span>
            <el-radio-group v-model="params.window_size" size="small">
              <el-radio-button :value="5">5</el-radio-button>
              <el-radio-button :value="10">10</el-radio-button>
              <el-radio-button :value="20">20</el-radio-button>
            </el-radio-group>
          </div>

          <div class="quantum-reservoir-page__param-item quantum-reservoir-page__param-item--slider">
            <span class="quantum-reservoir-page__label">
              {{ $t('quantumReservoir.controls.nReservoir') }}: {{ params.n_reservoir }}
            </span>
            <el-slider
              v-model="params.n_reservoir"
              :min="50"
              :max="500"
              :step="10"
            />
          </div>

          <div class="quantum-reservoir-page__param-item quantum-reservoir-page__param-item--slider">
            <span class="quantum-reservoir-page__label">
              {{ $t('quantumReservoir.controls.spectralRadius') }}: {{ params.spectral_radius }}
            </span>
            <el-slider
              v-model="params.spectral_radius"
              :min="0.1"
              :max="0.99"
              :step="0.01"
            />
          </div>

          <div class="quantum-reservoir-page__param-item quantum-reservoir-page__param-item--slider">
            <span class="quantum-reservoir-page__label">
              {{ $t('quantumReservoir.controls.ridgeAlpha') }}: {{ params.ridge_alpha }}
            </span>
            <el-slider
              v-model="params.ridge_alpha"
              :min="0.01"
              :max="100"
              :step="0.01"
            />
          </div>
        </div>
      </el-card>
    </section>

    <!-- Error state -->
    <section v-if="loadError && !hasResult" class="quantum-reservoir-page__error wrapper">
      <el-empty :description="$t('quantumReservoir.message.loadFailed')">
        <el-button type="primary" @click="handleRetry">
          {{ $t('quantumReservoir.controls.retry') }}
        </el-button>
      </el-empty>
    </section>

    <!-- Section 3: Metrics Comparison Row -->
    <section v-if="hasResult" class="quantum-reservoir-page__metrics wrapper">
      <div class="quantum-reservoir-page__metrics-grid">
        <MetricsCard
          :title="$t('quantumReservoir.metrics.rmse')"
          :classic-value="classicMetrics.RMSE"
          :quantum-value="quantumMetrics.RMSE"
          unit=""
          :lower-is-better="true"
        />
        <MetricsCard
          :title="$t('quantumReservoir.metrics.mae')"
          :classic-value="classicMetrics.MAE"
          :quantum-value="quantumMetrics.MAE"
          unit=""
          :lower-is-better="true"
        />
        <MetricsCard
          :title="$t('quantumReservoir.metrics.mape')"
          :classic-value="classicMetrics.MAPE"
          :quantum-value="quantumMetrics.MAPE"
          unit="%"
          :lower-is-better="true"
        />
        <MetricsCard
          :title="$t('quantumReservoir.metrics.paramEfficiency')"
          :classic-value="paramEfficiency.classic"
          :quantum-value="paramEfficiency.quantum"
          unit=""
          :lower-is-better="false"
        />
      </div>
    </section>

    <!-- Section 4: el-tabs -->
    <section v-if="hasResult" class="quantum-reservoir-page__tabs wrapper">
      <el-card>
        <el-tabs v-model="activeTab" @tab-change="onTabChange">
          <el-tab-pane
            :label="$t('quantumReservoir.tabs.prediction')"
            name="prediction"
          >
            <PredictionChart
              ref="predictionChartRef"
              :predictions="predictions"
            />
          </el-tab-pane>

          <el-tab-pane
            :label="$t('quantumReservoir.tabs.scatter')"
            name="scatter"
          >
            <ReservoirScatter
              ref="reservoirScatterRef"
              :reservoir-states="reservoirStates"
            />
          </el-tab-pane>

          <el-tab-pane
            :label="$t('quantumReservoir.tabs.circuit')"
            name="circuit"
          >
            <CircuitInfo :circuit-info="circuitInfo" />
          </el-tab-pane>

          <el-tab-pane
            :label="$t('quantumReservoir.tabs.compare')"
            name="compare"
          >
            <div v-loading="comparisonLoading">
              <div
                v-if="comparisonData"
                ref="compareChartRef"
                class="quantum-reservoir-page__compare-chart"
              />
              <el-table
                v-if="comparisonData"
                :data="comparisonData"
                stripe
                style="width: 100%; margin-top: 20px"
              >
                <el-table-column
                  v-for="col in compareTableColumns"
                  :key="col.prop"
                  :prop="col.prop"
                  :label="col.label"
                  :width="col.width"
                />
              </el-table>
              <el-empty
                v-if="!comparisonData && !comparisonLoading"
                :description="$t('quantumReservoir.compare.noData')"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </section>

    <!-- Empty state before first solve -->
    <section v-if="!hasResult && !loading && !loadError" class="quantum-reservoir-page__empty wrapper">
      <el-empty :description="$t('quantumReservoir.message.noResult')" />
    </section>

    <!-- Section 5: Algorithm Description -->
    <section class="quantum-reservoir-page__algorithm wrapper">
      <el-card>
        <h3 class="quantum-reservoir-page__algorithm-title">
          {{ $t('quantumReservoir.algorithm.title') }}
        </h3>
        <div class="quantum-reservoir-page__algorithm-content">
          <p>{{ $t('quantumReservoir.algorithm.desc1') }}</p>
          <p>{{ $t('quantumReservoir.algorithm.desc2') }}</p>
          <p>{{ $t('quantumReservoir.algorithm.desc3') }}</p>
        </div>
      </el-card>
    </section>

    <!-- Footer -->
    <Footer />
  </main>
</template>

<style lang="scss" scoped>
.quantum-reservoir-page {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #f4f7fc;

  .wrapper {
    max-width: 1440px;
    margin: 0 auto;
    padding: 0 20px;
  }

  // --- Banner ---
  &__banner {
    background: linear-gradient(135deg, #1664ff 0%, #4f9df7 100%);
    padding: 60px 0;
  }

  &__banner-title {
    font-size: 40px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 12px 0;
  }

  &__banner-subtitle {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.85);
    margin: 0;
  }

  // --- Controls ---
  &__controls {
    margin-top: 24px;
  }

  &__controls-card {
    border-radius: 8px;
    border-color: #dce0eb;
  }

  &__controls-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  &__stock-select {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  &__label {
    font-size: 14px;
    color: #41464f;
    white-space: nowrap;
  }

  &__params-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  &__param-item {
    display: flex;
    flex-direction: column;
    gap: 8px;

    &--slider {
      grid-column: span 1;
    }
  }

  // --- Error ---
  &__error {
    margin-top: 40px;
    display: flex;
    justify-content: center;
  }

  // --- Metrics ---
  &__metrics {
    margin-top: 24px;
  }

  &__metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
  }

  // --- Tabs ---
  &__tabs {
    margin-top: 24px;

    :deep(.el-card__body) {
      padding: 20px;
    }

    :deep(.el-tabs__item) {
      font-size: 14px;
    }

    :deep(.el-tabs__item.is-active) {
      color: #1664ff;
    }
  }

  // --- Compare chart ---
  &__compare-chart {
    width: 100%;
    height: 350px;
  }

  // --- Empty ---
  &__empty {
    margin-top: 40px;
    display: flex;
    justify-content: center;
  }

  // --- Algorithm ---
  &__algorithm {
    margin-top: 24px;
    margin-bottom: 40px;
  }

  &__algorithm-title {
    font-size: 20px;
    font-weight: 600;
    color: #020814;
    margin: 0 0 16px 0;
  }

  &__algorithm-content {
    p {
      font-size: 14px;
      color: #41464f;
      line-height: 1.8;
      margin: 0 0 8px 0;
    }
  }
}

// Responsive adjustments
@media (max-width: 1440px) {
  .quantum-reservoir-page {
    &__params-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    &__metrics-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

@media (max-width: 1366px) {
  .quantum-reservoir-page {
    &__params-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    &__metrics-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    &__banner-title {
      font-size: 32px;
    }
  }
}
</style>
