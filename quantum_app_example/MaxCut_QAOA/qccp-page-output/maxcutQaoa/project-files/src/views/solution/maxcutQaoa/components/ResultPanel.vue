<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import * as echarts from 'echarts';

const { t } = useI18n();

const props = defineProps({
  optimizationHistory: {
    type: Array,
    default: () => [],
  },
  probabilities: {
    type: Array,
    default: () => [],
  },
  bestPartition: {
    type: Array,
    default: () => [],
  },
});

const convergenceRef = ref(null);
const probabilityRef = ref(null);
let convergenceChart = null;
let probabilityChart = null;

function buildConvergenceOption() {
  const data = props.optimizationHistory || [];
  return {
    tooltip: {
      trigger: 'axis',
    },
    grid: {
      left: 60,
      right: 30,
      top: 30,
      bottom: 40,
    },
    xAxis: {
      type: 'category',
      name: t('maxcutQaoa.iteration'),
      data: data.map((_, i) => i + 1),
      axisLine: { lineStyle: { color: '#DCE0EB' } },
      axisLabel: { color: '#939AAB' },
      nameTextStyle: { color: '#41464F' },
    },
    yAxis: {
      type: 'value',
      name: t('maxcutQaoa.expectation'),
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#DCE0EB' } },
      axisLabel: { color: '#939AAB' },
      nameTextStyle: { color: '#41464F' },
    },
    series: [
      {
        type: 'line',
        data: data,
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        lineStyle: { color: '#1664FF', width: 2 },
        itemStyle: { color: '#1664FF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22,100,255,0.15)' },
            { offset: 1, color: 'rgba(22,100,255,0.02)' },
          ]),
        },
      },
    ],
  };
}

function buildProbabilityOption() {
  const probs = props.probabilities || [];
  const top10 = probs.slice(0, 10);
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    grid: {
      left: 80,
      right: 30,
      top: 30,
      bottom: 40,
    },
    xAxis: {
      type: 'category',
      name: t('maxcutQaoa.bitstring'),
      data: top10.map((p) => p.bitstring),
      axisLine: { lineStyle: { color: '#DCE0EB' } },
      axisLabel: { color: '#939AAB', rotate: 30 },
      nameTextStyle: { color: '#41464F' },
    },
    yAxis: {
      type: 'value',
      name: t('maxcutQaoa.probability'),
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#DCE0EB' } },
      axisLabel: { color: '#939AAB' },
      nameTextStyle: { color: '#41464F' },
    },
    series: [
      {
        type: 'bar',
        data: top10.map((p) => p.probability),
        barWidth: 24,
        itemStyle: {
          color: '#1664FF',
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
  };
}

function renderConvergence() {
  if (!convergenceRef.value || convergenceRef.value.offsetWidth === 0) return;
  if (!convergenceChart) {
    convergenceChart = echarts.init(convergenceRef.value);
  }
  convergenceChart.setOption(buildConvergenceOption(), true);
}

function renderProbability() {
  if (!probabilityRef.value || probabilityRef.value.offsetWidth === 0) return;
  if (!probabilityChart) {
    probabilityChart = echarts.init(probabilityRef.value);
  }
  probabilityChart.setOption(buildProbabilityOption(), true);
}

function renderAll() {
  nextTick(() => {
    setTimeout(() => {
      renderConvergence();
      renderProbability();
    }, 200);
  });
}

watch(
  () => [props.optimizationHistory, props.probabilities],
  () => renderAll(),
  { deep: true },
);

onBeforeUnmount(() => {
  if (convergenceChart) {
    convergenceChart.dispose();
    convergenceChart = null;
  }
  if (probabilityChart) {
    probabilityChart.dispose();
    probabilityChart = null;
  }
});

defineExpose({ renderAll });
</script>

<template>
  <div class="result-panel">
    <div v-if="optimizationHistory.length > 0" class="result-section">
      <h3 class="section-title">{{ $t('maxcutQaoa.tabOptimization') }}</h3>
      <div ref="convergenceRef" class="chart-container" />
    </div>
    <div v-if="probabilities.length > 0" class="result-section">
      <h3 class="section-title">{{ $t('maxcutQaoa.tabProbability') }}</h3>
      <div ref="probabilityRef" class="chart-container" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.result-panel {
  width: 100%;
}

.result-section {
  margin-bottom: 30px;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 20px;
  font-weight: 400;
  color: #020814;
  margin: 0 0 16px 0;
}

.chart-container {
  width: 100%;
  height: 350px;
  min-height: 250px;
}
</style>
