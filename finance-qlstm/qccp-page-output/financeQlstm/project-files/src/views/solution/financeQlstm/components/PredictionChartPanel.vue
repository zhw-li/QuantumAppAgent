<script setup>
import { ref, nextTick, onBeforeUnmount, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import * as echarts from 'echarts';

const { t } = useI18n();

const props = defineProps({
  predictions: { type: Object, default: null },
  rawData: { type: Object, default: null },
});

const activeTab = ref('prediction');
const predictionChartRef = ref(null);
const candleChartRef = ref(null);
let predictionChartInstance = null;
let candleChartInstance = null;

function getOrCreateChart(domRef, existingInstance) {
  if (!domRef) return null;
  if (domRef.offsetWidth === 0) return null;
  if (existingInstance && !existingInstance.isDisposed()) {
    return existingInstance;
  }
  return echarts.init(domRef);
}

function renderPredictionChart() {
  if (!props.predictions || !predictionChartRef.value) return;
  predictionChartInstance = getOrCreateChart(predictionChartRef.value, predictionChartInstance);
  if (!predictionChartInstance) return;

  const { dates, actual, QLSTM, LSTM } = props.predictions;

  predictionChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: [
        t('financeQlstm.prediction.actual'),
        t('financeQlstm.prediction.qlstm'),
        t('financeQlstm.prediction.lstm'),
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
      data: dates,
      axisLabel: {
        fontSize: 12,
        color: '#939AAB',
        rotate: 30,
      },
      name: t('financeQlstm.prediction.date'),
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 12, color: '#939AAB' },
      name: t('financeQlstm.prediction.price'),
    },
    series: [
      {
        name: t('financeQlstm.prediction.actual'),
        type: 'line',
        data: actual,
        lineStyle: { color: '#020814', width: 2 },
        itemStyle: { color: '#020814' },
        symbol: 'circle',
        symbolSize: 6,
      },
      {
        name: t('financeQlstm.prediction.qlstm'),
        type: 'line',
        data: QLSTM,
        lineStyle: { color: '#1664FF', width: 2 },
        itemStyle: { color: '#1664FF' },
        symbol: 'diamond',
        symbolSize: 6,
      },
      {
        name: t('financeQlstm.prediction.lstm'),
        type: 'line',
        data: LSTM,
        lineStyle: { color: '#4F9DF7', width: 2, type: 'dashed' },
        itemStyle: { color: '#4F9DF7' },
        symbol: 'triangle',
        symbolSize: 6,
      },
    ],
  }, true);
}

function renderCandleChart() {
  if (!props.rawData || !candleChartRef.value) return;
  candleChartInstance = getOrCreateChart(candleChartRef.value, candleChartInstance);
  if (!candleChartInstance) return;

  const { dates, OHLC, volume } = props.rawData;

  const ohlcData = OHLC.map((d) => [d.open, d.close, d.low, d.high]);
  const volumeData = volume;

  candleChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      data: [
        t('financeQlstm.prediction.close'),
        t('financeQlstm.prediction.volume'),
      ],
      top: 0,
    },
    grid: [
      { left: 60, right: 30, top: 40, height: '55%' },
      { left: 60, right: 30, top: '72%', height: '20%' },
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        axisLabel: { fontSize: 12, color: '#939AAB', rotate: 30 },
        gridIndex: 0,
      },
      {
        type: 'category',
        data: dates,
        gridIndex: 1,
        axisLabel: { show: false },
      },
    ],
    yAxis: [
      {
        type: 'value',
        axisLabel: { fontSize: 12, color: '#939AAB' },
        name: t('financeQlstm.prediction.price'),
        gridIndex: 0,
      },
      {
        type: 'value',
        axisLabel: { fontSize: 12, color: '#939AAB' },
        name: t('financeQlstm.prediction.volume'),
        gridIndex: 1,
        splitNumber: 3,
      },
    ],
    series: [
      {
        name: t('financeQlstm.prediction.close'),
        type: 'candlestick',
        data: ohlcData,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: '#FB4214',
          color0: '#27AE60',
          borderColor: '#FB4214',
          borderColor0: '#27AE60',
        },
      },
      {
        name: t('financeQlstm.prediction.volume'),
        type: 'bar',
        data: volumeData,
        xAxisIndex: 1,
        yAxisIndex: 1,
        itemStyle: { color: '#4F9DF7' },
      },
    ],
  }, true);
}

function tryRenderCurrentTab() {
  nextTick(() => {
    setTimeout(() => {
      if (activeTab.value === 'prediction') {
        renderPredictionChart();
      } else {
        renderCandleChart();
      }
    }, 200);
  });
}

function onTabChange(tab) {
  activeTab.value = tab.paneName || tab;
  tryRenderCurrentTab();
}

watch(
  () => props.predictions,
  () => {
    if (activeTab.value === 'prediction') {
      tryRenderCurrentTab();
    }
  },
);

watch(
  () => props.rawData,
  () => {
    if (activeTab.value === 'candle') {
      tryRenderCurrentTab();
    }
  },
);

function handleResize() {
  predictionChartInstance && !predictionChartInstance.isDisposed() && predictionChartInstance.resize();
  candleChartInstance && !candleChartInstance.isDisposed() && candleChartInstance.resize();
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  if (predictionChartInstance && !predictionChartInstance.isDisposed()) {
    predictionChartInstance.dispose();
    predictionChartInstance = null;
  }
  if (candleChartInstance && !candleChartInstance.isDisposed()) {
    candleChartInstance.dispose();
    candleChartInstance = null;
  }
});

// Register resize listener on mount
import { onMounted } from 'vue';
onMounted(() => {
  window.addEventListener('resize', handleResize);
  // Initial render for the visible tab
  tryRenderCurrentTab();
});
</script>

<template>
  <div class="prediction-chart-panel wrapper">
    <h2 class="section-title">{{ $t('financeQlstm.prediction.title') }}</h2>
    <template v-if="predictions || rawData">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane :label="$t('financeQlstm.prediction.tabPrediction')" name="prediction">
          <div ref="predictionChartRef" class="chart-container"></div>
        </el-tab-pane>
        <el-tab-pane :label="$t('financeQlstm.prediction.tabCandle')" name="candle">
          <div ref="candleChartRef" class="chart-container"></div>
        </el-tab-pane>
      </el-tabs>
    </template>
    <el-empty v-else :description="$t('financeQlstm.prediction.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.prediction-chart-panel {
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
  height: 420px;
  margin-top: 10px;
}
</style>
