<script setup>
import { ref, watch, onBeforeUnmount, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import * as echarts from 'echarts';

const props = defineProps({
  predictions: { type: Object, default: null }
});

const { t } = useI18n();
const chartRef = ref(null);
let chartInstance = null;

function initChart() {
  if (!chartRef.value || chartRef.value.offsetWidth <= 0) return;
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  chartInstance = echarts.init(chartRef.value);
  updateChart();
}

function updateChart() {
  if (!chartInstance || !props.predictions) return;

  const { dates, actual, classic, quantum } = props.predictions;

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: [
        t('quantumReservoir.chart.actual'),
        t('quantumReservoir.chart.classic'),
        t('quantumReservoir.chart.quantum')
      ],
      top: 0
    },
    grid: {
      left: 60,
      right: 30,
      top: 40,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: dates || [],
      axisLabel: {
        rotate: 45,
        fontSize: 11,
        color: '#939aab'
      },
      axisLine: { lineStyle: { color: '#dce0eb' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#939aab' },
      splitLine: { lineStyle: { color: '#dce0eb', type: 'dashed' } }
    },
    series: [
      {
        name: t('quantumReservoir.chart.actual'),
        type: 'line',
        data: actual || [],
        lineStyle: { color: '#020814', width: 2 },
        itemStyle: { color: '#020814' },
        symbol: 'none',
        z: 3
      },
      {
        name: t('quantumReservoir.chart.classic'),
        type: 'line',
        data: classic || [],
        lineStyle: { color: '#41464f', width: 1.5, type: 'dashed' },
        itemStyle: { color: '#41464f' },
        symbol: 'none',
        z: 2
      },
      {
        name: t('quantumReservoir.chart.quantum'),
        type: 'line',
        data: quantum || [],
        lineStyle: { color: '#1664ff', width: 2 },
        itemStyle: { color: '#1664ff' },
        symbol: 'none',
        z: 1
      }
    ]
  };

  chartInstance.setOption(option, true);
}

function handleResize() {
  if (chartInstance) chartInstance.resize();
}

watch(() => props.predictions, () => {
  nextTick(() => updateChart());
}, { deep: true });

/**
 * Public method: deferred render for tab switch.
 * Call from parent on tab change with setTimeout(200ms) + nextTick.
 */
function deferredRender() {
  nextTick(() => {
    setTimeout(() => {
      initChart();
    }, 50);
  });
}

defineExpose({ deferredRender, handleResize });

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});
</script>

<template>
  <div class="prediction-chart">
    <div v-if="!predictions" class="prediction-chart__empty">
      <el-empty :description="t('quantumReservoir.chart.noData')" />
    </div>
    <div
      v-else
      ref="chartRef"
      class="prediction-chart__container"
    />
  </div>
</template>

<style lang="scss" scoped>
.prediction-chart {
  width: 100%;
  min-height: 400px;

  &__container {
    width: 100%;
    height: 400px;
  }

  &__empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 400px;
  }
}
</style>
