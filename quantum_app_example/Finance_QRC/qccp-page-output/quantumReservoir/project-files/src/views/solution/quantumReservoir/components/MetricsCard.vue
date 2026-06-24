<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps({
  title: { type: String, required: true },
  classicValue: { type: [Number, String], default: '-' },
  quantumValue: { type: [Number, String], default: '-' },
  unit: { type: String, default: '' },
  lowerIsBetter: { type: Boolean, default: true }
});

const { t } = useI18n();

const improvement = computed(() => {
  const c = parseFloat(props.classicValue);
  const q = parseFloat(props.quantumValue);
  if (isNaN(c) || isNaN(q) || c === 0) return null;
  const diff = props.lowerIsBetter
    ? ((c - q) / c * 100)
    : ((q - c) / c * 100);
  return diff;
});

const improvementText = computed(() => {
  if (improvement.value === null) return '-';
  const val = improvement.value.toFixed(2);
  return improvement.value > 0 ? `+${val}%` : `${val}%`;
});

const improvementClass = computed(() => {
  if (improvement.value === null) return '';
  return improvement.value > 0 ? 'improvement-positive' : 'improvement-negative';
});
</script>

<template>
  <div class="metrics-card">
    <div class="metrics-card__title">{{ title }}</div>
    <div class="metrics-card__body">
      <div class="metrics-card__row">
        <span class="metrics-card__label">{{ t('quantumReservoir.metrics.classic') }}</span>
        <span class="metrics-card__value metrics-card__value--classic">{{ classicValue }}{{ unit }}</span>
      </div>
      <div class="metrics-card__row">
        <span class="metrics-card__label">{{ t('quantumReservoir.metrics.quantum') }}</span>
        <span class="metrics-card__value metrics-card__value--quantum">{{ quantumValue }}{{ unit }}</span>
      </div>
    </div>
    <div class="metrics-card__footer">
      <span class="metrics-card__improvement" :class="improvementClass">
        {{ improvementText }}
      </span>
      <span class="metrics-card__improvement-label">{{ t('quantumReservoir.metrics.improvement') }}</span>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.metrics-card {
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #dce0eb;
  padding: 20px;
  min-height: 140px;
  display: flex;
  flex-direction: column;

  &__title {
    font-size: 16px;
    font-weight: 600;
    color: #020814;
    margin-bottom: 16px;
  }

  &__body {
    flex: 1;
  }

  &__row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  &__label {
    font-size: 14px;
    color: #939aab;
  }

  &__value {
    font-size: 20px;
    font-weight: 600;

    &--classic {
      color: #41464f;
    }

    &--quantum {
      color: #1664ff;
    }
  }

  &__footer {
    display: flex;
    align-items: center;
    gap: 6px;
    padding-top: 12px;
    border-top: 1px solid #dce0eb;
  }

  &__improvement {
    font-size: 18px;
    font-weight: 700;

    &.improvement-positive {
      color: #1664ff;
    }

    &.improvement-negative {
      color: #fb4214;
    }
  }

  &__improvement-label {
    font-size: 12px;
    color: #939aab;
  }
}
</style>
