<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps({
  circuitInfo: { type: Object, default: null }
});

const { t } = useI18n();

const infoItems = computed(() => {
  if (!props.circuitInfo) return [];
  return [
    { label: t('quantumReservoir.circuit.nQubits'), value: props.circuitInfo.n_qubits },
    { label: t('quantumReservoir.circuit.depth'), value: props.circuitInfo.depth },
    { label: t('quantumReservoir.circuit.gateCount'), value: props.circuitInfo.gate_count },
    { label: t('quantumReservoir.circuit.paramCount'), value: props.circuitInfo.parameter_count },
    { label: t('quantumReservoir.circuit.circuitType'), value: props.circuitInfo.circuit_type }
  ];
});
</script>

<template>
  <div class="circuit-info">
    <div v-if="!circuitInfo" class="circuit-info__empty">
      <el-empty :description="t('quantumReservoir.circuit.noData')" />
    </div>
    <template v-else>
      <div class="circuit-info__meta">
        <div
          v-for="item in infoItems"
          :key="item.label"
          class="circuit-info__item"
        >
          <span class="circuit-info__label">{{ item.label }}</span>
          <span class="circuit-info__value">{{ item.value }}</span>
        </div>
      </div>
      <div class="circuit-info__code-section">
        <div class="circuit-info__code-header">
          <span class="circuit-info__code-title">{{ t('quantumReservoir.circuit.qcisCode') }}</span>
        </div>
        <pre class="circuit-info__code-block">{{ circuitInfo.qcis_code }}</pre>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.circuit-info {
  width: 100%;

  &__empty {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 300px;
  }

  &__meta {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-bottom: 20px;
  }

  &__item {
    background: #f3f7ff;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
  }

  &__label {
    display: block;
    font-size: 13px;
    color: #939aab;
    margin-bottom: 8px;
  }

  &__value {
    display: block;
    font-size: 22px;
    font-weight: 700;
    color: #1664ff;
  }

  &__code-section {
    border: 1px solid #dce0eb;
    border-radius: 8px;
    overflow: hidden;
  }

  &__code-header {
    background: #f3f7ff;
    padding: 10px 16px;
    border-bottom: 1px solid #dce0eb;
  }

  &__code-title {
    font-size: 14px;
    font-weight: 600;
    color: #020814;
  }

  &__code-block {
    padding: 16px;
    margin: 0;
    font-family: 'Menlo', 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #41464f;
    background: #ffffff;
    overflow-x: auto;
    white-space: pre;
  }
}
</style>
