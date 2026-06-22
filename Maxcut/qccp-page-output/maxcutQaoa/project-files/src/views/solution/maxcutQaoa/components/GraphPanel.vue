<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  graphData: {
    type: Object,
    default: () => ({ nodes: [], edges: [] }),
  },
  partition: {
    type: Array,
    default: () => [],
  },
  cutEdges: {
    type: Array,
    default: () => [],
  },
});

const chartRef = ref(null);
let chartInstance = null;

const cutEdgeSet = computed(() => {
  return new Set(props.cutEdges.map((e) => `${e[0]}-${e[1]}`));
});

function buildOption() {
  const nodes = props.graphData.nodes || [];
  const edges = props.graphData.edges || [];

  const seriesData = nodes.map((node, idx) => {
    const group = props.partition[idx] ?? 0;
    return {
      name: `V${idx}`,
      value: idx,
      symbolSize: 40,
      itemStyle: {
        color: group === 0 ? '#1664FF' : '#4F9DF7',
        borderColor: '#FFFFFF',
        borderWidth: 2,
      },
      label: {
        show: true,
        color: '#FFFFFF',
        fontSize: 14,
        fontWeight: 'bold',
      },
    };
  });

  const seriesLinks = edges.map((edge) => {
    const key = `${edge[0]}-${edge[1]}`;
    const isCut = cutEdgeSet.value.has(key);
    return {
      source: `V${edge[0]}`,
      target: `V${edge[1]}`,
      lineStyle: {
        color: isCut ? '#FB4214' : '#DCE0EB',
        width: isCut ? 3 : 1.5,
      },
    };
  });

  return {
    tooltip: {},
    animation: false,
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: seriesData,
        links: seriesLinks,
        roam: true,
        force: {
          repulsion: 200,
          edgeLength: [80, 150],
          gravity: 0.1,
        },
        label: {
          show: true,
          position: 'inside',
        },
      },
    ],
  };
}

function renderChart() {
  if (!chartRef.value || chartRef.value.offsetWidth === 0) return;
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  chartInstance.setOption(buildOption(), true);
}

watch(
  () => [props.graphData, props.partition, props.cutEdges],
  () => {
    nextTick(() => {
      setTimeout(() => renderChart(), 200);
    });
  },
  { deep: true },
);

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});

defineExpose({ renderChart });
</script>

<template>
  <div class="graph-panel">
    <div ref="chartRef" class="graph-chart" />
  </div>
</template>

<style lang="scss" scoped>
.graph-panel {
  width: 100%;
}

.graph-chart {
  width: 100%;
  height: 400px;
  min-height: 300px;
}
</style>
