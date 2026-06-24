<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  qaoaCut: {
    type: Number,
    default: null,
  },
  optimalCut: {
    type: Number,
    default: null,
  },
  costGap: {
    type: Number,
    default: null,
  },
  nQubits: {
    type: Number,
    default: null,
  },
  circuitDepth: {
    type: Number,
    default: null,
  },
  elapsedTime: {
    type: Number,
    default: null,
  },
});

const metricCards = computed(() => [
  {
    key: 'qaoaCut',
    label: t('maxcutQaoa.qaoaCutValue'),
    value: props.qaoaCut !== null ? props.qaoaCut : '--',
  },
  {
    key: 'optimalCut',
    label: t('maxcutQaoa.optimalCutValue'),
    value: props.optimalCut !== null ? props.optimalCut : '--',
  },
  {
    key: 'costGap',
    label: t('maxcutQaoa.costGap'),
    value: props.costGap !== null ? `${props.costGap.toFixed(2)}${t('maxcutQaoa.percent')}` : '--',
  },
  {
    key: 'qubits',
    label: t('maxcutQaoa.qubitCount'),
    value: props.nQubits !== null ? props.nQubits : '--',
  },
  {
    key: 'depth',
    label: t('maxcutQaoa.circuitDepth'),
    value: props.circuitDepth !== null ? props.circuitDepth : '--',
  },
  {
    key: 'time',
    label: t('maxcutQaoa.solveTime'),
    value: props.elapsedTime !== null ? `${props.elapsedTime.toFixed(2)}${t('maxcutQaoa.seconds')}` : '--',
  },
]);

const tableData = computed(() => [
  {
    metric: t('maxcutQaoa.qaoaCutValue'),
    value: props.qaoaCut !== null ? props.qaoaCut : '--',
  },
  {
    metric: t('maxcutQaoa.optimalCutValue'),
    value: props.optimalCut !== null ? props.optimalCut : '--',
  },
  {
    metric: t('maxcutQaoa.costGap'),
    value: props.costGap !== null ? `${props.costGap.toFixed(2)}${t('maxcutQaoa.percent')}` : '--',
  },
  {
    metric: t('maxcutQaoa.qubitCount'),
    value: props.nQubits !== null ? props.nQubits : '--',
  },
  {
    metric: t('maxcutQaoa.circuitDepth'),
    value: props.circuitDepth !== null ? props.circuitDepth : '--',
  },
  {
    metric: t('maxcutQaoa.solveTime'),
    value: props.elapsedTime !== null ? `${props.elapsedTime.toFixed(2)}${t('maxcutQaoa.seconds')}` : '--',
  },
]);
</script>

<template>
  <div class="compare-panel">
    <div class="metric-cards">
      <div
        v-for="card in metricCards"
        :key="card.key"
        class="metric-card"
      >
        <span class="metric-label">{{ card.label }}</span>
        <span class="metric-value">{{ card.value }}</span>
      </div>
    </div>

    <el-table
      :data="tableData"
      stripe
      style="width: 100%"
    >
      <el-table-column
        prop="metric"
        :label="$t('maxcutQaoa.metric')"
        min-width="200"
      />
      <el-table-column
        prop="value"
        :label="$t('maxcutQaoa.value')"
        min-width="200"
      />
    </el-table>
  </div>
</template>

<style lang="scss" scoped>
.compare-panel {
  width: 100%;
}

.metric-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: #FFFFFF;
  border: 1px solid #DCE0EB;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-label {
  font-size: 14px;
  color: #939AAB;
}

.metric-value {
  font-size: 30px;
  color: #020814;
  font-weight: 400;
}

@media (max-width: 1440px) {
  .metric-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
