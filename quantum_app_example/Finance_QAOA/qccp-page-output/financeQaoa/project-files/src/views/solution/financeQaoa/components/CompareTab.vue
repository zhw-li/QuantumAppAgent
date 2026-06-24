<script setup>
import { nextTick, onBeforeUnmount, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { compareOptimization } from '@/api/financeQaoa/index.js';

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

const metricsTableData = ref([]);

const runComparison = async () => {
  loading.value = true;
  result.value = null;
  try {
    const res = await compareOptimization({
      tier: props.tier,
      k: form.k,
      q: form.q,
      depth: form.depth,
      restarts: form.restarts,
    });
    if (res.code === 200 && res.data) {
      result.value = res.data;
      buildMetricsTable();
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

const buildMetricsTable = () => {
  if (!result.value) return;
  const c = result.value.classical || {};
  const q = result.value.quantum || {};
  const bf = result.value.bruteforce || {};

  metricsTableData.value = [
    {
      method: t('financeQaoa.compare.classicalMethod'),
      portfolioReturn: c.portfolio_return,
      portfolioRisk: c.portfolio_risk,
      portfolioSharpe: c.portfolio_sharpe,
      selectedStocks: (c.selected_stocks || []).join(', '),
      costGap: '-',
    },
    {
      method: t('financeQaoa.compare.quantumMethod'),
      portfolioReturn: q.portfolio_return,
      portfolioRisk: q.portfolio_risk,
      portfolioSharpe: q.portfolio_sharpe,
      selectedStocks: (q.selected_stocks || []).join(', '),
      costGap: q.cost_gap != null ? q.cost_gap.toFixed(2) + '%' : '-',
    },
    {
      method: t('financeQaoa.compare.bruteForceMethod'),
      portfolioReturn: bf.portfolio_return,
      portfolioRisk: bf.portfolio_risk,
      portfolioSharpe: bf.portfolio_sharpe,
      selectedStocks: (bf.selected_stocks || []).join(', '),
      costGap: '0.00%',
    },
  ];
};

const renderAllCharts = () => {
  nextTick(() => {
    setTimeout(() => {
      renderWeightComparison();
      renderEfficientFrontier();
      renderRiskReturnChart();
    }, 100);
  });
};

const renderWeightComparison = () => {
  const el = chartRefs.weightCompare;
  if (!el || el.offsetWidth === 0 || !result.value) return;
  const instance = initChart('weightCompare', el);
  if (!instance) return;

  const c = result.value.classical || {};
  const q = result.value.quantum || {};
  const cWeights = c.weights || {};
  const qWeights = q.weights || {};
  const symbols = result.value.symbols || [];

  const cData = symbols.map((s) => parseFloat(((cWeights[s] || 0) * 100).toFixed(2)));
  const qData = symbols.map((s) => parseFloat(((qWeights[s] || 0) * 100).toFixed(2)));

  instance.setOption({
    tooltip: { trigger: 'axis', formatter: (params) => {
      let s = params[0].name + '<br/>';
      params.forEach((p) => { s += `${p.seriesName}: ${p.value}%<br/>`; });
      return s;
    }},
    legend: { bottom: 0 },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: { type: 'category', data: symbols, axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { fontSize: 11, formatter: '{value}%' } },
    series: [
      {
        name: t('financeQaoa.compare.classicalMethod'),
        type: 'bar',
        data: cData,
        itemStyle: { color: '#4F9DF7', borderRadius: [4, 4, 0, 0] },
        barMaxWidth: 30,
      },
      {
        name: t('financeQaoa.compare.quantumMethod'),
        type: 'bar',
        data: qData,
        itemStyle: { color: '#1664FF', borderRadius: [4, 4, 0, 0] },
        barMaxWidth: 30,
      },
    ],
  });
};

const renderEfficientFrontier = () => {
  const el = chartRefs.frontier;
  if (!el || el.offsetWidth === 0 || !result.value) return;
  const instance = initChart('frontier', el);
  if (!instance) return;

  const frontier = result.value.efficient_frontier || [];
  const c = result.value.classical || {};
  const q = result.value.quantum || {};
  const bf = result.value.bruteforce || {};

  const frontierData = frontier.map((p) => [(p.risk * 100).toFixed(2), (p.return * 100).toFixed(2)]);

  const highlights = [];
  if (c.portfolio_risk != null) {
    highlights.push({
      name: t('financeQaoa.compare.classicalMethod'),
      value: [(c.portfolio_risk * 100).toFixed(2), (c.portfolio_return * 100).toFixed(2)],
      itemStyle: { color: '#4F9DF7' },
      symbolSize: 14,
    });
  }
  if (q.portfolio_risk != null) {
    highlights.push({
      name: t('financeQaoa.compare.quantumMethod'),
      value: [(q.portfolio_risk * 100).toFixed(2), (q.portfolio_return * 100).toFixed(2)],
      itemStyle: { color: '#1664FF' },
      symbolSize: 14,
    });
  }
  if (bf.portfolio_risk != null) {
    highlights.push({
      name: t('financeQaoa.compare.bruteForceMethod'),
      value: [(bf.portfolio_risk * 100).toFixed(2), (bf.portfolio_return * 100).toFixed(2)],
      itemStyle: { color: '#FB4214' },
      symbolSize: 14,
    });
  }

  instance.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: {
      type: 'value',
      name: t('financeQaoa.compare.portfolioRisk') + ' (%)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: t('financeQaoa.compare.portfolioReturn') + ' (%)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: { fontSize: 11 },
    },
    series: [
      {
        name: t('financeQaoa.compare.efficientFrontier'),
        type: 'line',
        data: frontierData,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#DCE0EB', type: 'dashed' },
      },
      {
        name: t('financeQaoa.compare.riskReturnChart'),
        type: 'scatter',
        data: highlights,
        label: { show: true, formatter: '{b}', position: 'right', fontSize: 11 },
      },
    ],
  });
};

const renderRiskReturnChart = () => {
  const el = chartRefs.riskReturn;
  if (!el || el.offsetWidth === 0 || !result.value) return;
  const instance = initChart('riskReturn', el);
  if (!instance) return;

  const c = result.value.classical || {};
  const q = result.value.quantum || {};
  const bf = result.value.bruteforce || {};

  const barData = [];
  const categories = [
    t('financeQaoa.compare.portfolioReturn'),
    t('financeQaoa.compare.portfolioRisk'),
    t('financeQaoa.compare.portfolioSharpe'),
  ];

  const classicalVals = [
    c.portfolio_return != null ? (c.portfolio_return * 100).toFixed(2) : 0,
    c.portfolio_risk != null ? (c.portfolio_risk * 100).toFixed(2) : 0,
    c.portfolio_sharpe != null ? c.portfolio_sharpe.toFixed(2) : 0,
  ];
  const quantumVals = [
    q.portfolio_return != null ? (q.portfolio_return * 100).toFixed(2) : 0,
    q.portfolio_risk != null ? (q.portfolio_risk * 100).toFixed(2) : 0,
    q.portfolio_sharpe != null ? q.portfolio_sharpe.toFixed(2) : 0,
  ];
  const bfVals = [
    bf.portfolio_return != null ? (bf.portfolio_return * 100).toFixed(2) : 0,
    bf.portfolio_risk != null ? (bf.portfolio_risk * 100).toFixed(2) : 0,
    bf.portfolio_sharpe != null ? bf.portfolio_sharpe.toFixed(2) : 0,
  ];

  instance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0 },
    grid: { left: 60, right: 30, top: 30, bottom: 50 },
    xAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
    series: [
      {
        name: t('financeQaoa.compare.classicalMethod'),
        type: 'bar',
        data: classicalVals,
        itemStyle: { color: '#4F9DF7', borderRadius: [4, 4, 0, 0] },
        barMaxWidth: 30,
      },
      {
        name: t('financeQaoa.compare.quantumMethod'),
        type: 'bar',
        data: quantumVals,
        itemStyle: { color: '#1664FF', borderRadius: [4, 4, 0, 0] },
        barMaxWidth: 30,
      },
      {
        name: t('financeQaoa.compare.bruteForceMethod'),
        type: 'bar',
        data: bfVals,
        itemStyle: { color: '#FB4214', borderRadius: [4, 4, 0, 0] },
        barMaxWidth: 30,
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
  <div class="compare-tab">
    <!-- Params -->
    <div class="section-card">
      <div class="section-header">
        <span class="section-title">{{ t('financeQaoa.compare.params') }}</span>
      </div>
      <el-form :model="form" label-width="160px" inline>
        <el-form-item :label="t('financeQaoa.compare.selectK')">
          <el-input-number v-model="form.k" :min="1" :max="10" :step="1" />
        </el-form-item>
        <el-form-item :label="t('financeQaoa.compare.riskAversion')">
          <el-input-number v-model="form.q" :min="0" :max="1" :step="0.1" :precision="1" />
        </el-form-item>
        <el-form-item :label="t('financeQaoa.compare.depth')">
          <el-input-number v-model="form.depth" :min="1" :max="5" :step="1" />
        </el-form-item>
        <el-form-item :label="t('financeQaoa.compare.restarts')">
          <el-input-number v-model="form.restarts" :min="1" :max="20" :step="1" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="runComparison">
            {{ loading ? t('financeQaoa.compare.running') : t('financeQaoa.compare.run') }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Results -->
    <template v-if="result">
      <!-- Metrics table -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.compare.metricsTable') }}</span>
        </div>
        <el-table :data="metricsTableData" stripe style="width: 100%">
          <el-table-column prop="method" :label="t('financeQaoa.compare.method')" width="180" />
          <el-table-column :label="t('financeQaoa.compare.portfolioReturn')">
            <template #default="{ row }">{{ fmtPercent(row.portfolioReturn) }}</template>
          </el-table-column>
          <el-table-column :label="t('financeQaoa.compare.portfolioRisk')">
            <template #default="{ row }">{{ fmtPercent(row.portfolioRisk) }}</template>
          </el-table-column>
          <el-table-column :label="t('financeQaoa.compare.portfolioSharpe')">
            <template #default="{ row }">{{ row.portfolioSharpe != null ? row.portfolioSharpe.toFixed(4) : '-' }}</template>
          </el-table-column>
          <el-table-column prop="costGap" :label="t('financeQaoa.compare.costGap')" width="120" />
          <el-table-column prop="selectedStocks" :label="t('financeQaoa.compare.selectedStocks')" />
        </el-table>
      </div>

      <!-- Weight comparison -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.compare.weightComparison') }}</span>
        </div>
        <div ref="chartRefs.weightCompare" class="chart-container"></div>
      </div>

      <!-- Efficient frontier -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.compare.efficientFrontier') }}</span>
        </div>
        <div ref="chartRefs.frontier" class="chart-container"></div>
      </div>

      <!-- Risk-return comparison -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.compare.riskReturnChart') }}</span>
        </div>
        <div ref="chartRefs.riskReturn" class="chart-container"></div>
      </div>
    </template>

    <el-empty v-else-if="!loading" :description="t('financeQaoa.message.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.compare-tab {
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

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
