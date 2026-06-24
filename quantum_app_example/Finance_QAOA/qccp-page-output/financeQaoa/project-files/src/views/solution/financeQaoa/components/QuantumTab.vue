<script setup>
import { nextTick, onBeforeUnmount, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { optimizeQuantum } from '@/api/financeQaoa/index.js';

const props = defineProps({
  tier: { type: String, default: 'demo' },
});

const { t } = useI18n();

const loading = ref(false);
const result = ref(null);

const form = reactive({
  k: 3,
  q: 0.5,
  depth: 2,
  restarts: 5,
  force: false,
});

const chartRefs = reactive({});
const chartInstances = reactive({});

const initChart = (key, el) => {
  if (!el || el.offsetWidth === 0) return null;
  if (chartInstances[key]) {
    chartInstances[key].dispose();
  }
  const instance = echarts.init(el);
  chartInstances[key] = instance;
  return instance;
};

const fmtPercent = (v) => {
  if (v == null) return '-';
  return (v * 100).toFixed(2) + '%';
};

const runOptimization = async () => {
  loading.value = true;
  result.value = null;
  try {
    const res = await optimizeQuantum({
      tier: props.tier,
      k: form.k,
      q: form.q,
      depth: form.depth,
      restarts: form.restarts,
      force: form.force,
    });
    if (res.code === 200 && res.data) {
      result.value = res.data;
      ElMessage.success(t('financeQaoa.message.optimizeSuccess'));
      renderAllCharts();
    } else {
      ElMessage.error(t('financeQaoa.message.optimizeFailed'));
    }
  } catch {
    ElMessage.error(t('financeQaoa.message.networkError'));
  } finally {
    loading.value = false;
  }
};

const renderAllCharts = () => {
  nextTick(() => {
    setTimeout(() => {
      renderBitstringChart();
      renderPieChart();
    }, 100);
  });
};

const renderBitstringChart = () => {
  const el = chartRefs.bitstring;
  if (!el || el.offsetWidth === 0 || !result.value) return;
  const instance = initChart('bitstring', el);
  if (!instance) return;

  const bitstrings = result.value.top_bitstrings || [];
  const categories = bitstrings.map((b) => b.bitstring);
  const probs = bitstrings.map((b) => (b.probability * 100).toFixed(2));
  const colors = bitstrings.map((b) => (b.is_selected ? '#FB4214' : '#1664FF'));

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0];
        const bs = bitstrings[p.dataIndex];
        const selected = bs?.is_selected ? ' (Selected)' : '';
        return `${p.name}${selected}<br/>${t('financeQaoa.quantum.bitstringDistribution')}: ${p.value}%`;
      },
    },
    grid: { left: 60, right: 30, top: 30, bottom: 60 },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { fontSize: 10, rotate: 45 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 11, formatter: '{value}%' },
    },
    series: [
      {
        type: 'bar',
        data: probs.map((v, i) => ({
          value: v,
          itemStyle: { color: colors[i], borderRadius: [4, 4, 0, 0] },
        })),
        barMaxWidth: 30,
      },
    ],
  });
};

const renderPieChart = () => {
  const el = chartRefs.pie;
  if (!el || el.offsetWidth === 0 || !result.value) return;
  const instance = initChart('pie', el);
  if (!instance) return;

  const weights = result.value.weights || {};
  const data = Object.entries(weights)
    .filter(([, w]) => w > 0)
    .map(([sym, w]) => ({ name: sym, value: parseFloat((w * 100).toFixed(2)) }));

  instance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
    legend: { bottom: 0, type: 'scroll' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        data,
        label: { formatter: '{b}\n{c}%', fontSize: 12 },
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      },
    ],
  });
};

const handleResize = () => {
  Object.values(chartInstances).forEach((inst) => {
    if (inst && !inst.isDisposed()) {
      inst.resize();
    }
  });
};

const onVisible = () => {
  if (result.value) {
    setTimeout(() => {
      renderAllCharts();
    }, 250);
  }
};

onBeforeUnmount(() => {
  Object.values(chartInstances).forEach((inst) => {
    if (inst && !inst.isDisposed()) {
      inst.dispose();
    }
  });
  window.removeEventListener('resize', handleResize);
});

window.addEventListener('resize', handleResize);

defineExpose({ onVisible });
</script>

<template>
  <div class="quantum-tab">
    <!-- Params -->
    <div class="section-card">
      <div class="section-header">
        <span class="section-title">{{ t('financeQaoa.quantum.params') }}</span>
      </div>
      <el-form :model="form" label-width="160px" inline>
        <el-form-item :label="t('financeQaoa.quantum.selectK')">
          <el-input-number v-model="form.k" :min="1" :max="10" :step="1" />
        </el-form-item>
        <el-form-item :label="t('financeQaoa.quantum.riskAversion')">
          <el-input-number v-model="form.q" :min="0" :max="1" :step="0.1" :precision="1" />
        </el-form-item>
        <el-form-item :label="t('financeQaoa.quantum.depth')">
          <el-input-number v-model="form.depth" :min="1" :max="5" :step="1" />
        </el-form-item>
        <el-form-item :label="t('financeQaoa.quantum.restarts')">
          <el-input-number v-model="form.restarts" :min="1" :max="20" :step="1" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.force">{{ t('financeQaoa.quantum.forceRerun') }}</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="runOptimization">
            {{ loading ? t('financeQaoa.quantum.running') : t('financeQaoa.quantum.run') }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- Metrics row 1: QAOA results -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.selectedStocks') }}</div>
          <div class="metric-value">{{ (result.selected_stocks || []).join(', ') }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.portfolioReturn') }}</div>
          <div class="metric-value text-up">{{ fmtPercent(result.portfolio_return) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.portfolioRisk') }}</div>
          <div class="metric-value text-down">{{ fmtPercent(result.portfolio_risk) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.portfolioSharpe') }}</div>
          <div class="metric-value">{{ result.portfolio_sharpe?.toFixed(4) ?? '-' }}</div>
        </div>
      </div>

      <!-- Metrics row 2: QAOA details -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.costGap') }}</div>
          <div class="metric-value" :class="result.cost_gap === 0 ? 'text-up' : 'text-down'">
            {{ result.cost_gap != null ? result.cost_gap.toFixed(2) + '%' : '-' }}
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.nQubits') }}</div>
          <div class="metric-value">{{ result.n_qubits ?? '-' }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.penaltyWeight') }}</div>
          <div class="metric-value">{{ result.penalty_weight != null ? result.penalty_weight.toFixed(4) : '-' }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.quantum.normFactor') }}</div>
          <div class="metric-value">{{ result.norm_factor != null ? result.norm_factor.toFixed(4) : '-' }}</div>
        </div>
      </div>

      <!-- Brute force comparison -->
      <div v-if="result.brute_force" class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.quantum.bruteForceComparison') }}</span>
        </div>
        <div class="compare-grid">
          <div class="compare-item">
            <span class="compare-label">{{ t('financeQaoa.quantum.bruteForceReturn') }}</span>
            <span class="compare-value">{{ fmtPercent(result.brute_force.portfolio_return) }}</span>
          </div>
          <div class="compare-item">
            <span class="compare-label">{{ t('financeQaoa.quantum.bruteForceRisk') }}</span>
            <span class="compare-value">{{ fmtPercent(result.brute_force.portfolio_risk) }}</span>
          </div>
          <div class="compare-item">
            <span class="compare-label">{{ t('financeQaoa.quantum.bruteForceSharpe') }}</span>
            <span class="compare-value">{{ result.brute_force.portfolio_sharpe?.toFixed(4) ?? '-' }}</span>
          </div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <div class="section-card chart-main">
          <div class="section-header">
            <span class="section-title">{{ t('financeQaoa.quantum.bitstringDistribution') }}</span>
          </div>
          <div ref="chartRefs.bitstring" class="chart-container"></div>
        </div>
        <div class="section-card chart-side">
          <div class="section-header">
            <span class="section-title">{{ t('financeQaoa.quantum.weightDistribution') }}</span>
          </div>
          <div ref="chartRefs.pie" class="chart-container"></div>
        </div>
      </div>
    </template>

    <el-empty v-else-if="!loading" :description="t('financeQaoa.message.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.quantum-tab {
  width: 100%;
}

.section-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #020814;
}

.metrics-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.metric-card {
  flex: 1;
  min-width: 160px;
  background: #f3f7ff;
  border-radius: 8px;
  padding: 16px;
}

.metric-label {
  font-size: 13px;
  color: #939aab;
  margin-bottom: 6px;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: #020814;
  word-break: break-all;
}

.text-up {
  color: #1664ff;
}

.text-down {
  color: #fb4214;
}

.compare-grid {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.compare-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.compare-label {
  font-size: 13px;
  color: #939aab;
}

.compare-value {
  font-size: 18px;
  font-weight: 600;
  color: #020814;
}

.charts-row {
  display: flex;
  gap: 20px;
}

.chart-main {
  flex: 2;
  min-width: 0;
}

.chart-side {
  flex: 1;
  min-width: 0;
}

.chart-container {
  width: 100%;
  height: 400px;
}

@media (max-width: 1200px) {
  .charts-row {
    flex-direction: column;
  }
}
</style>
