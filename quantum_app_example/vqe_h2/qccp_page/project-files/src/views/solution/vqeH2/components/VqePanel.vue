<template>
  <div class="vqe-panel">
    <div class="panel-container">
      <div class="panel-card">
        <h2 class="section-title">{{ t('vqeH2.vqe.title') }}</h2>

        <!-- Input controls -->
        <div class="controls-row">
          <div class="control-item">
            <label class="control-label">{{ t('vqeH2.vqe.seed') }}</label>
            <el-input-number
              v-model="seed"
              :min="0"
              :max="9999"
              :step="1"
              controls-position="right"
              size="large"
            />
          </div>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="runVqe"
          >
            {{ t('vqeH2.vqe.runVqe') }}
          </el-button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="loading-wrapper">
          <el-skeleton :rows="4" animated />
          <p class="loading-text">{{ t('vqeH2.vqe.loading') }}</p>
        </div>

        <!-- Error with retry -->
        <div v-else-if="error" class="error-wrapper">
          <el-empty :description="t('vqeH2.vqe.loadFailed')" :image-size="80" />
          <el-button type="primary" @click="runVqe">
            {{ t('vqeH2.vqe.retry') }}
          </el-button>
        </div>

        <!-- Empty (no data yet) -->
        <div v-else-if="!data" class="empty-wrapper">
          <el-empty :description="t('vqeH2.vqe.runFirst')" :image-size="80" />
        </div>

        <!-- Results display -->
        <div v-else class="results-content">
          <div class="metrics-grid">
            <div class="metric-item">
              <span class="metric-label">{{ t('vqeH2.vqe.vqeEnergy') }}</span>
              <span class="metric-value">{{ formatEnergy(data.total_energy_hartree) }}</span>
              <span class="metric-unit">{{ t('vqeH2.vqe.unitHartree') }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">{{ t('vqeH2.vqe.exactEnergy') }}</span>
              <span class="metric-value">{{ formatEnergy(data.electronic_energy_hartree) }}</span>
              <span class="metric-unit">{{ t('vqeH2.vqe.unitHartree') }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">{{ t('vqeH2.vqe.energyError') }}</span>
              <span
                class="metric-value"
                :class="{ 'success-value': isChemicalAccuracy, 'error-value': !isChemicalAccuracy }"
              >
                {{ formatError(data.energy_error_mhartree) }}
              </span>
              <span class="metric-unit">{{ t('vqeH2.vqe.unitMHartree') }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">{{ t('vqeH2.vqe.circuitDepth') }}</span>
              <span class="metric-value">{{ data.circuit_depth ?? '--' }}</span>
            </div>
            <div class="metric-item accuracy-item">
              <span class="metric-label">{{ t('vqeH2.vqe.chemicalAccuracy') }}</span>
              <el-tag
                :type="isChemicalAccuracy ? 'success' : 'danger'"
                size="large"
              >
                {{ isChemicalAccuracy ? t('vqeH2.vqe.chemicalAccuracyTag') : t('vqeH2.vqe.chemicalAccuracyNotTag') }}
              </el-tag>
              <span class="threshold-hint">{{ t('vqeH2.vqe.threshold') }}</span>
            </div>
          </div>

          <!-- QCIS circuit section -->
          <div v-if="qcisData" class="qcis-section">
            <h3 class="subsection-title">{{ t('vqeH2.vqe.qcisTitle') }}</h3>
            <div class="qcis-graph-wrapper">
              <QcisGraph :qcis="qcisData" />
            </div>
          </div>

          <!-- Convergence chart -->
          <div v-if="convergenceData.length > 0" class="convergence-section">
            <h3 class="subsection-title">{{ t('vqeH2.vqe.convergenceTitle') }}</h3>
            <div class="chart-wrapper">
              <div class="convergence-chart">
                <div
                  v-for="(point, idx) in chartPoints"
                  :key="idx"
                  class="chart-bar-wrapper"
                >
                  <div
                    class="chart-bar"
                    :style="{ height: point.height + '%' }"
                    :title="'Iter ' + point.iter + ': ' + point.energy.toFixed(6)"
                  />
                </div>
              </div>
              <div class="chart-axis-labels">
                <span>{{ t('vqeH2.vqe.convergenceIteration') }}</span>
                <span>{{ t('vqeH2.vqe.convergenceEnergy') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { runVqe as runVqeApi } from '@/api/vqeH2/index';
import QcisGraph from '@/views/solution/components/graph.vue';

const { t } = useI18n();

const seed = ref(42);
const loading = ref(false);
const error = ref(false);
const data = ref(null);
const qcisData = ref(null);
const convergenceData = ref([]);

const isChemicalAccuracy = computed(() => {
  if (!data.value) return false;
  return Math.abs(data.value.energy_error_mhartree) <= 1.6;
});

const chartPoints = computed(() => {
  if (convergenceData.value.length === 0) return [];
  const energies = convergenceData.value.map((p) => p.total_energy_hartree);
  const minE = Math.min(...energies);
  const maxE = Math.max(...energies);
  const range = maxE - minE || 1;
  return convergenceData.value.map((p) => ({
    iter: p.evaluation,
    energy: p.total_energy_hartree,
    height: ((p.total_energy_hartree - minE) / range) * 80 + 10
  }));
});

function formatEnergy(val) {
  if (val == null) return '--';
  return Number(val).toFixed(8);
}

function formatError(val) {
  if (val == null) return '--';
  return Number(val).toFixed(4);
}

async function runVqe() {
  loading.value = true;
  error.value = false;
  try {
    const res = await runVqeApi({ seed: seed.value });
    const result = res.data || res;
    data.value = result;
    if (result.convergence) {
      convergenceData.value = result.convergence;
    } else {
      convergenceData.value = [];
    }
    if (result.qcis) {
      qcisData.value = result.qcis;
    } else {
      qcisData.value = null;
    }
  } catch (e) {
    error.value = true;
    ElMessage.error(t('vqeH2.vqe.loadFailed'));
  } finally {
    loading.value = false;
  }
}

defineExpose({ data, runVqe });
</script>

<style lang="scss" scoped>
.vqe-panel {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0 0 24px;
}

.panel-container {
  width: 100%;
  max-width: 1440px;
  padding: 0 24px;
}

.panel-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 40px 56px;
  border: 1px solid #dce0eb;
}

.section-title {
  font-size: 30px;
  font-weight: 400;
  color: #020814;
  margin: 0 0 28px;
}

.controls-row {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-label {
  font-size: 14px;
  color: #41464f;
}

.loading-wrapper {
  padding: 20px 0;
}

.loading-text {
  font-size: 14px;
  color: #939aab;
  text-align: center;
  margin-top: 12px;
}

.error-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  gap: 16px;
}

.empty-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.results-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 28px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-label {
  font-size: 14px;
  color: #939aab;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #020814;
  font-variant-numeric: tabular-nums;
}

.metric-value.success-value {
  color: #1664ff;
}

.metric-value.error-value {
  color: #fb4214;
}

.metric-unit {
  font-size: 14px;
  color: #939aab;
}

.accuracy-item {
  justify-content: center;
}

.threshold-hint {
  font-size: 12px;
  color: #939aab;
  margin-top: 4px;
}

.subsection-title {
  font-size: 24px;
  font-weight: 400;
  color: #020814;
  margin: 0 0 16px;
}

.qcis-section {
  padding-top: 8px;
}

.qcis-graph-wrapper {
  background: #f4f7fc;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #dce0eb;
}

.qcis-code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  color: #41464f;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.convergence-section {
  padding-top: 8px;
}

.chart-wrapper {
  background: #f4f7fc;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid #dce0eb;
}

.convergence-chart {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 200px;
  padding-bottom: 8px;
}

.chart-bar-wrapper {
  flex: 1;
  min-width: 4px;
  display: flex;
  align-items: flex-end;
  height: 100%;
}

.chart-bar {
  width: 100%;
  background: #1664ff;
  border-radius: 4px 4px 0 0;
  min-height: 2px;
  cursor: pointer;
  transition: background 0.2s;
}

.chart-bar:hover {
  background: #4f9df7;
}

.chart-axis-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #939aab;
  padding-top: 8px;
  border-top: 1px solid #dce0eb;
}
</style>
