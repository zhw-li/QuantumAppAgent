<script setup>
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { getStatistics } from '@/api/financeQaoa/index.js';

const props = defineProps({
  tier: { type: String, default: 'demo' },
});

const { t } = useI18n();

const loading = ref(false);
const loadError = ref(false);
const stats = ref(null);

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

const fmtNum = (v, digits = 4) => {
  if (v == null) return '-';
  return Number(v).toFixed(digits);
};

const tableData = computed(() => {
  if (!stats.value) return [];
  const syms = stats.value.symbols || [];
  return syms.map((sym, i) => ({
    symbol: sym,
    annualReturnRaw: stats.value.annual_returns?.[i],
    annualVolatilityRaw: stats.value.annual_volatilities?.[i],
    sharpeRatioRaw: stats.value.sharpe_ratios?.[i],
    maxDrawdownRaw: stats.value.max_drawdowns?.[i],
    totalReturnRaw: stats.value.total_returns?.[i],
  }));
});

const loadData = async () => {
  loading.value = true;
  loadError.value = false;
  try {
    const res = await getStatistics(props.tier);
    if (res.code === 200 && res.data) {
      stats.value = res.data;
      renderAllCharts();
    } else {
      loadError.value = true;
    }
  } catch {
    loadError.value = true;
    ElMessage.error(t('financeQaoa.message.networkError'));
  } finally {
    loading.value = false;
  }
};

const renderAllCharts = () => {
  nextTick(() => {
    setTimeout(() => {
      renderBarChart();
      renderHeatmap();
      renderScatter();
    }, 100);
  });
};

const renderBarChart = () => {
  const el = chartRefs.barChart;
  if (!el || el.offsetWidth === 0 || !stats.value) return;
  const instance = initChart('barChart', el);
  if (!instance) return;

  const symbols = stats.value.symbols || [];
  const returns = (stats.value.annual_returns || []).map((v) => (v * 100).toFixed(2));

  instance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0];
        return `${p.name}: ${p.value}%`;
      },
    },
    grid: { left: 60, right: 30, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: symbols, axisLabel: { fontSize: 11 } },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 11, formatter: '{value}%' },
    },
    series: [
      {
        type: 'bar',
        data: returns,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#1664FF' },
            { offset: 1, color: '#4F9DF7' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
        barMaxWidth: 40,
      },
    ],
  });
};

const renderHeatmap = () => {
  const el = chartRefs.heatmap;
  if (!el || el.offsetWidth === 0 || !stats.value) return;
  const instance = initChart('heatmap', el);
  if (!instance) return;

  const symbols = stats.value.symbols || [];
  const corr = stats.value.correlation || stats.value.correlation_matrix || [];
  const data = [];
  for (let i = 0; i < symbols.length; i++) {
    for (let j = 0; j < symbols.length; j++) {
      data.push([i, j, corr[i] ? corr[i][j] : 0]);
    }
  }

  instance.setOption({
    tooltip: {
      formatter: (p) => `${symbols[p.data[0]]} - ${symbols[p.data[1]]}: ${p.data[2].toFixed(3)}`,
    },
    grid: { left: 80, right: 60, top: 10, bottom: 60 },
    xAxis: {
      type: 'category',
      data: symbols,
      axisLabel: { fontSize: 11 },
      splitArea: { show: true },
    },
    yAxis: {
      type: 'category',
      data: symbols,
      axisLabel: { fontSize: 11 },
      splitArea: { show: true },
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'vertical',
      right: 0,
      top: 'center',
      inRange: { color: ['#4F9DF7', '#ffffff', '#FB4214'] },
    },
    series: [
      {
        type: 'heatmap',
        data: data,
        label: { show: symbols.length <= 8, fontSize: 10, formatter: (p) => p.data[2].toFixed(2) },
        emphasis: { itemStyle: { shadowBlur: 6, shadowColor: 'rgba(0,0,0,0.3)' } },
      },
    ],
  });
};

const renderScatter = () => {
  const el = chartRefs.scatter;
  if (!el || el.offsetWidth === 0 || !stats.value) return;
  const instance = initChart('scatter', el);
  if (!instance) return;

  const symbols = stats.value.symbols || [];
  const vols = (stats.value.annual_volatilities || []).map((v) => (v * 100).toFixed(2));
  const rets = (stats.value.annual_returns || []).map((v) => (v * 100).toFixed(2));

  const scatterData = symbols.map((sym, i) => ({
    name: sym,
    value: [parseFloat(vols[i]), parseFloat(rets[i])],
  }));

  instance.setOption({
    tooltip: {
      formatter: (p) => `${p.name}<br/>${t('financeQaoa.statistics.annualVolatility')}: ${p.value[0]}%<br/>${t('financeQaoa.statistics.annualReturn')}: ${p.value[1]}%`,
    },
    grid: { left: 60, right: 30, top: 30, bottom: 40 },
    xAxis: {
      type: 'value',
      name: t('financeQaoa.statistics.annualVolatility') + ' (%)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: t('financeQaoa.statistics.annualReturn') + ' (%)',
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

watch(() => props.tier, () => {
  loadData();
});

const handleResize = () => {
  Object.values(chartInstances).forEach((inst) => {
    if (inst && !inst.isDisposed()) {
      inst.resize();
    }
  });
};

const onVisible = () => {
  setTimeout(() => {
    renderAllCharts();
  }, 250);
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
loadData();

defineExpose({ onVisible });
</script>

<template>
  <div class="statistics-tab">
    <div v-if="loading" class="tab-loading">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>{{ t('financeQaoa.common.loading') }}</span>
    </div>

    <div v-else-if="loadError" class="tab-error">
      <el-empty :description="t('financeQaoa.message.loadFailed')">
        <el-button type="primary" @click="loadData">{{ t('financeQaoa.common.retry') }}</el-button>
      </el-empty>
    </div>

    <template v-else-if="stats">
      <!-- Annual returns bar chart -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.statistics.annualReturn') }}</span>
        </div>
        <div ref="chartRefs.barChart" class="chart-container"></div>
      </div>

      <!-- Correlation heatmap + Risk-return scatter side by side -->
      <div class="charts-row">
        <div class="section-card chart-half">
          <div class="section-header">
            <span class="section-title">{{ t('financeQaoa.statistics.correlationHeatmap') }}</span>
          </div>
          <div ref="chartRefs.heatmap" class="chart-container"></div>
        </div>
        <div class="section-card chart-half">
          <div class="section-header">
            <span class="section-title">{{ t('financeQaoa.statistics.riskReturnScatter') }}</span>
          </div>
          <div ref="chartRefs.scatter" class="chart-container"></div>
        </div>
      </div>

      <!-- Stats table -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.statistics.statsTable') }}</span>
        </div>
        <el-table :data="tableData" stripe style="width: 100%">
          <el-table-column prop="symbol" :label="t('financeQaoa.statistics.stock')" width="100" />
          <el-table-column :label="t('financeQaoa.statistics.annualReturn')">
            <template #default="{ row }">{{ fmtPercent(row.annualReturnRaw) }}</template>
          </el-table-column>
          <el-table-column :label="t('financeQaoa.statistics.annualVolatility')">
            <template #default="{ row }">{{ fmtPercent(row.annualVolatilityRaw) }}</template>
          </el-table-column>
          <el-table-column :label="t('financeQaoa.statistics.sharpeRatio')">
            <template #default="{ row }">{{ fmtNum(row.sharpeRatioRaw) }}</template>
          </el-table-column>
          <el-table-column :label="t('financeQaoa.statistics.maxDrawdown')">
            <template #default="{ row }">{{ fmtPercent(row.maxDrawdownRaw) }}</template>
          </el-table-column>
          <el-table-column :label="t('financeQaoa.statistics.totalReturn')">
            <template #default="{ row }">{{ fmtPercent(row.totalReturnRaw) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <el-empty v-else :description="t('financeQaoa.message.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.statistics-tab {
  width: 100%;
}

.tab-loading,
.tab-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 12px;
  color: #939aab;
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

.charts-row {
  display: flex;
  gap: 20px;
}

.chart-half {
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
