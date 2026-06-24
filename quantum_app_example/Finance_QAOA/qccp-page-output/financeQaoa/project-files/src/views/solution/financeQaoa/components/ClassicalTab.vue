<script setup>
import { nextTick, onBeforeUnmount, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { optimizeClassical } from '@/api/financeQaoa/index.js';

const props = defineProps({
  tier: { type: String, default: 'demo' },
});

const { t } = useI18n();

const loading = ref(false);
const result = ref(null);

const form = reactive({
  k: 3,
  q: 0.5,
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
    const res = await optimizeClassical({
      tier: props.tier,
      k: form.k,
      q: form.q,
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
      renderEfficientFrontier();
      renderPieChart();
      renderRiskReturnScatter();
    }, 100);
  });
};

const renderEfficientFrontier = () => {
  const el = chartRefs.frontier;
  if (!el || el.offsetWidth === 0 || !result.value) return;
  const instance = initChart('frontier', el);
  if (!instance) return;

  const frontier = result.value.efficient_frontier || [];
  const risks = frontier.map((p) => (p.risk * 100).toFixed(2));
  const returns = frontier.map((p) => (p.return * 100).toFixed(2));
  const stockPoints = result.value.stock_points || [];

  const stockScatter = stockPoints.map((sp) => ({
    name: sp.name,
    value: [(sp.risk * 100).toFixed(2), (sp.return * 100).toFixed(2)],
  }));

  const optRisk = result.value.portfolio_risk != null ? (result.value.portfolio_risk * 100).toFixed(2) : null;
  const optReturn = result.value.portfolio_return != null ? (result.value.portfolio_return * 100).toFixed(2) : null;

  const series = [
    {
      name: t('financeQaoa.classical.efficientFrontier'),
      type: 'line',
      data: risks.map((r, i) => [r, returns[i]]),
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: '#1664FF' },
    },
    {
      name: t('financeQaoa.statistics.stock'),
      type: 'scatter',
      data: stockScatter,
      symbolSize: 14,
      itemStyle: { color: '#4F9DF7' },
      label: { show: true, formatter: '{b}', position: 'right', fontSize: 11 },
    },
  ];

  if (optRisk != null && optReturn != null) {
    series.push({
      name: t('financeQaoa.classical.title'),
      type: 'scatter',
      data: [{ name: 'Optimal', value: [optRisk, optReturn] }],
      symbolSize: 20,
      itemStyle: { color: '#FB4214' },
      label: { show: true, formatter: 'Optimal', position: 'top', fontSize: 12, fontWeight: 'bold' },
    });
  }

  instance.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: {
      type: 'value',
      name: t('financeQaoa.classical.portfolioRisk') + ' (%)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: t('financeQaoa.classical.portfolioReturn') + ' (%)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 },
    },
    series,
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

const renderRiskReturnScatter = () => {
  const el = chartRefs.riskScatter;
  if (!el || el.offsetWidth === 0 || !result.value) return;
  const instance = initChart('riskScatter', el);
  if (!instance) return;

  const stockPoints = result.value.stock_points || [];
  const scatterData = stockPoints.map((sp) => ({
    name: sp.name,
    value: [(sp.risk * 100).toFixed(2), (sp.return * 100).toFixed(2)],
  }));

  instance.setOption({
    tooltip: {
      formatter: (p) => `${p.name}<br/>Risk: ${p.value[0]}%<br/>Return: ${p.value[1]}%`,
    },
    grid: { left: 60, right: 30, top: 30, bottom: 40 },
    xAxis: {
      type: 'value',
      name: t('financeQaoa.classical.portfolioRisk') + ' (%)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: t('financeQaoa.classical.portfolioReturn') + ' (%)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 },
    },
    series: [
      {
        type: 'scatter',
        data: scatterData,
        symbolSize: 16,
        itemStyle: { color: '#1664FF' },
        label: { show: true, formatter: '{b}', position: 'right', fontSize: 11 },
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
  <div class="classical-tab">
    <!-- Params -->
    <div class="section-card">
      <div class="section-header">
        <span class="section-title">{{ t('financeQaoa.classical.params') }}</span>
      </div>
      <el-form :model="form" label-width="160px" inline>
        <el-form-item :label="t('financeQaoa.classical.selectK')">
          <el-input-number v-model="form.k" :min="1" :max="10" :step="1" />
        </el-form-item>
        <el-form-item :label="t('financeQaoa.classical.riskAversion')">
          <el-input-number v-model="form.q" :min="0" :max="1" :step="0.1" :precision="1" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="runOptimization">
            {{ loading ? t('financeQaoa.classical.running') : t('financeQaoa.classical.run') }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- Metrics -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.classical.portfolioReturn') }}</div>
          <div class="metric-value text-up">{{ fmtPercent(result.portfolio_return) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.classical.portfolioRisk') }}</div>
          <div class="metric-value text-down">{{ fmtPercent(result.portfolio_risk) }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.classical.portfolioSharpe') }}</div>
          <div class="metric-value">{{ result.portfolio_sharpe?.toFixed(4) ?? '-' }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">{{ t('financeQaoa.classical.selectedStocks') }}</div>
          <div class="metric-value">{{ (result.selected_stocks || []).join(', ') }}</div>
        </div>
      </div>

      <!-- Charts row -->
      <div class="charts-row">
        <div class="section-card chart-main">
          <div class="section-header">
            <span class="section-title">{{ t('financeQaoa.classical.efficientFrontier') }}</span>
          </div>
          <div ref="chartRefs.frontier" class="chart-container"></div>
        </div>
        <div class="section-card chart-side">
          <div class="section-header">
            <span class="section-title">{{ t('financeQaoa.classical.weightDistribution') }}</span>
          </div>
          <div ref="chartRefs.pie" class="chart-container"></div>
        </div>
      </div>

      <!-- Risk-return scatter -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.classical.riskReturnScatter') }}</span>
        </div>
        <div ref="chartRefs.riskScatter" class="chart-container"></div>
      </div>
    </template>

    <el-empty v-else-if="!loading" :description="t('financeQaoa.message.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.classical-tab {
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
  min-width: 180px;
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
  font-size: 22px;
  font-weight: 700;
  color: #020814;
}

.text-up {
  color: #1664ff;
}

.text-down {
  color: #fb4214;
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
