<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  comparison: { type: Object, default: null },
});

const metricKeys = computed(() => ['RMSE', 'MAE', 'MAPE']);

function improvementColor(val) {
  if (val > 0) return '#27AE60';
  if (val < 0) return '#FB4214';
  return '#939AAB';
}

function improvementSign(val) {
  if (val > 0) return '+';
  if (val < 0) return '';
  return '';
}
</script>

<template>
  <div class="model-compare-panel wrapper">
    <h2 class="section-title">{{ $t('financeQlstm.compare.title') }}</h2>
    <template v-if="comparison">
      <div class="compare-grid">
        <!-- QLSTM Card -->
        <el-card class="compare-card" shadow="never">
          <div class="card-header">
            <span class="card-badge qlstm-badge">QLSTM</span>
            <h3 class="card-title">{{ $t('financeQlstm.compare.qlstm') }}</h3>
          </div>
          <div class="metrics-list">
            <div v-for="key in metricKeys" :key="key" class="metric-row">
              <span class="metric-label">{{ key }}</span>
              <span class="metric-value">{{ comparison.QLSTM[key].toFixed(4) }}</span>
              <span
                v-if="comparison.improvement"
                class="metric-improve"
                :style="{ color: improvementColor(comparison.improvement[key]) }"
              >
                {{ improvementSign(comparison.improvement[key]) }}{{ comparison.improvement[key].toFixed(2) }}%
              </span>
            </div>
            <div class="metric-row">
              <span class="metric-label">{{ $t('financeQlstm.compare.params') }}</span>
              <span class="metric-value metric-params">{{ comparison.QLSTM.params.toLocaleString() }}</span>
            </div>
          </div>
        </el-card>

        <!-- LSTM Card -->
        <el-card class="compare-card" shadow="never">
          <div class="card-header">
            <span class="card-badge lstm-badge">LSTM</span>
            <h3 class="card-title">{{ $t('financeQlstm.compare.lstm') }}</h3>
          </div>
          <div class="metrics-list">
            <div v-for="key in metricKeys" :key="key" class="metric-row">
              <span class="metric-label">{{ key }}</span>
              <span class="metric-value">{{ comparison.LSTM[key].toFixed(4) }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">{{ $t('financeQlstm.compare.params') }}</span>
              <span class="metric-value metric-params">{{ comparison.LSTM.params.toLocaleString() }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </template>
    <el-empty v-else :description="$t('financeQlstm.compare.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.model-compare-panel {
  margin-top: 30px;
}

.section-title {
  font-size: 30px;
  font-weight: regular;
  color: #020814;
  margin: 0 0 20px;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.compare-card {
  border-radius: 8px;
  border: 1px solid #DCE0EB;
  background: #ffffff;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.card-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  color: #ffffff;
}

.qlstm-badge {
  background: #1664FF;
}

.lstm-badge {
  background: #41464F;
}

.card-title {
  font-size: 20px;
  font-weight: regular;
  color: #020814;
  margin: 0;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 12px;
  background: #F3F7FF;
  border-radius: 6px;
}

.metric-label {
  font-size: 16px;
  color: #41464F;
  min-width: 60px;
}

.metric-value {
  font-size: 18px;
  color: #020814;
  font-weight: 500;
}

.metric-params {
  font-size: 16px;
  color: #939AAB;
}

.metric-improve {
  margin-left: auto;
  font-size: 14px;
  font-weight: 500;
}
</style>
