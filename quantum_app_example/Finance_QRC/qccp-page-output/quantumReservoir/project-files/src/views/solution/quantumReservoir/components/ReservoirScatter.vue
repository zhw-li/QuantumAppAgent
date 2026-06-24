<script setup>
import { ref, watch, onBeforeUnmount, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import * as echarts from 'echarts';

const props = defineProps({
  reservoirStates: { type: Object, default: null }
});

const { t } = useI18n();
const quantumChartRef = ref(null);
const classicChartRef = ref(null);
let quantumChartInstance = null;
let classicChartInstance = null;

function buildScatterOption(data, title, color) {
  const scatterData = (data || []).map(p => [p[0], p[1]]);
  return {
    title: {
      text: title,
      left: 'center',
      textStyle: { fontSize: 14, color: '#020814', fontWeight: 600 }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => `PC1: ${params.value[0]}<br/>PC2: ${params.value[1]}`
    },
    grid: {
      left: 50,
      right: 20,
      top: 40,
      bottom: 30
    },
    xAxis: {
      name: 'PC1',
      nameTextStyle: { color: '#939aab', fontSize: 12 },
      axisLabel: { color: '#939aab', fontSize: 11 },
      axisLine: { lineStyle: { color: '#dce0eb' } },
      splitLine: { lineStyle: { color: '#dce0eb', type: 'dashed' } }
    },
    yAxis: {
      name: 'PC2',
      nameTextStyle: { color: '#939aab', fontSize: 12 },
      axisLabel: { color: '#939aab', fontSize: 11 },
      axisLine: { lineStyle: { color: '#dce0eb' } },
      splitLine: { lineStyle: { color: '#dce0eb', type: 'dashed' } }
    },
    series: [{
      type: 'scatter',
      data: scatterData,
      symbolSize: 6,
      itemStyle: { color, opacity: 0.7 }
    }]
  };
}

function initCharts() {
  if (!props.reservoirStates) return;

  if (quantumChartRef.value && quantumChartRef.value.offsetWidth > 0) {
    if (quantumChartInstance) quantumChartInstance.dispose();
    quantumChartInstance = echarts.init(quantumChartRef.value);
    quantumChartInstance.setOption(
      buildScatterOption(
        props.reservoirStates.quantumPoints,
        t('quantumReservoir.scatter.quantumTitle'),
        '#1664ff'
      ),
      true
    );
  }

  if (classicChartRef.value && classicChartRef.value.offsetWidth > 0) {
    if (classicChartInstance) classicChartInstance.dispose();
    classicChartInstance = echarts.init(classicChartRef.value);
    classicChartInstance.setOption(
      buildScatterOption(
        props.reservoirStates.classicPoints,
        t('quantumReservoir.scatter.classicTitle'),
        '#41464f'
      ),
      true
    );
  }
}

function updateCharts() {
  if (!props.reservoirStates) return;

  if (quantumChartInstance) {
    quantumChartInstance.setOption(
      buildScatterOption(
        props.reservoirStates.quantumPoints,
        t('quantumReservoir.scatter.quantumTitle'),
        '#1664ff'
      ),
      true
    );
  }

  if (classicChartInstance) {
    classicChartInstance.setOption(
      buildScatterOption(
        props.reservoirStates.classicPoints,
        t('quantumReservoir.scatter.classicTitle'),
        '#41464f'
      ),
      true
    );
  }
}

function handleResize() {
  if (quantumChartInstance) quantumChartInstance.resize();
  if (classicChartInstance) classicChartInstance.resize();
}

watch(() => props.reservoirStates, () => {
  nextTick(() => updateCharts());
}, { deep: true });

function deferredRender() {
  nextTick(() => {
    setTimeout(() => {
      initCharts();
    }, 50);
  });
}

defineExpose({ deferredRender, handleResize });

onBeforeUnmount(() => {
  if (quantumChartInstance) {
    quantumChartInstance.dispose();
    quantumChartInstance = null;
  }
  if (classicChartInstance) {
    classicChartInstance.dispose();
    classicChartInstance = null;
  }
});
</script>

<template>
  <div class="reservoir-scatter">
    <div v-if="!reservoirStates" class="reservoir-scatter__empty">
      <el-empty :description="t('quantumReservoir.scatter.noData')" />
    </div>
    <div v-else class="reservoir-scatter__grid">
      <div
        ref="quantumChartRef"
        class="reservoir-scatter__chart"
      />
      <div
        ref="classicChartRef"
        class="reservoir-scatter__chart"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.reservoir-scatter {
  width: 100%;
  min-height: 400px;

  &__empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 400px;
  }

  &__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    width: 100%;
  }

  &__chart {
    width: 100%;
    height: 350px;
  }
}
</style>
