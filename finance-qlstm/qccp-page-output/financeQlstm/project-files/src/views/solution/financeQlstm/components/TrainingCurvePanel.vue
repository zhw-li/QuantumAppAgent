<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import * as echarts from 'echarts';

const { t } = useI18n();

const props = defineProps({
  trainingCurves: { type: Object, default: null },
});

const chartRef = ref(null);
let chartInstance = null;

function getOrCreateChart() {
  if (!chartRef.value) return null;
  if (chartRef.value.offsetWidth === 0) return null;
  if (chartInstance && !chartInstance.isDisposed()) {
    return chartInstance;
  }
  return echarts.init(chartRef.value);
}

function renderChart() {
  if (!props.trainingCurves || !chartRef.value) return;
  chartInstance = getOrCreateChart();
  if (!chartInstance) return;

  const { QLSTM, LSTM } = props.trainingCurves;
  const epochs = QLSTM.map((_, i) => i + 1);

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: [
        t('financeQlstm.training.qlstm'),
        t('financeQlstm.training.lstm'),
      ],
      top: 0,
    },
    grid: {
      left: 60,
      right: 30,
      top: 40,
      bottom: 40,
    },
    xAxis: {
      type: 'category',
      data: epochs,
      axisLabel: { fontSize: 12, color: '#939AAB' },
      name: t('financeQlstm.training.epoch'),
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 12, color: '#939AAB' },
      name: t('financeQlstm.training.loss'),
    },
    series: [
      {
        name: t('financeQlstm.training.qlstm'),
        type: 'line',
        data: QLSTM,
        lineStyle: { color: '#1664FF', width: 2 },
        itemStyle: { color: '#1664FF' },
        symbol: 'none',
        smooth: true,
      },
      {
        name: t('financeQlstm.training.lstm'),
        type: 'line',
        data: LSTM,
        lineStyle: { color: '#4F9DF7', width: 2, type: 'dashed' },
        itemStyle: { color: '#4F9DF7' },
        symbol: 'none',
        smooth: true,
      },
    ],
  }, true);
}

watch(
  () => props.trainingCurves,
  () => {
    nextTick(() => {
      setTimeout(() => renderChart(), 200);
    });
  },
);

function handleResize() {
  chartInstance && !chartInstance.isDisposed() && chartInstance.resize();
}

onMounted(() => {
  window.addEventListener('resize', handleResize);
  nextTick(() => {
    setTimeout(() => renderChart(), 200);
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance && !chartInstance.isDisposed()) {
    chartInstance.dispose();
    chartInstance = null;
  }
});
</script>

<template>
  <div class="training-curve-panel wrapper">
    <h2 class="section-title">{{ $t('financeQlstm.training.title') }}</h2>
    <template v-if="trainingCurves">
      <div ref="chartRef" class="chart-container"></div>
    </template>
    <el-empty v-else :description="$t('financeQlstm.training.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.training-curve-panel {
  margin-top: 30px;
}

.section-title {
  font-size: 30px;
  font-weight: regular;
  color: #020814;
  margin: 0 0 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
