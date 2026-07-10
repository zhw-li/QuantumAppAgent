<template>
  <div class="baseline-panel">
    <div class="panel-container">
      <div class="panel-card">
        <h2 class="section-title">{{ t('vqeH2.baseline.title') }}</h2>

        <!-- Loading -->
        <div v-if="loading" class="loading-wrapper">
          <el-skeleton :rows="3" animated />
          <p class="loading-text">{{ t('vqeH2.baseline.loading') }}</p>
        </div>

        <!-- Error with retry -->
        <div v-else-if="error" class="error-wrapper">
          <el-empty :description="t('vqeH2.baseline.loadFailed')" :image-size="80" />
          <el-button type="primary" @click="fetchBaseline">
            {{ t('vqeH2.baseline.retry') }}
          </el-button>
        </div>

        <!-- Empty -->
        <div v-else-if="!data" class="empty-wrapper">
          <el-empty :description="t('vqeH2.baseline.noData')" :image-size="80" />
          <el-button type="primary" @click="fetchBaseline">
            {{ t('vqeH2.baseline.runBaseline') }}
          </el-button>
        </div>

        <!-- Data display -->
        <div v-else class="data-content">
          <div class="metrics-grid">
            <div class="metric-item">
              <span class="metric-label">{{ t('vqeH2.baseline.hfEnergy') }}</span>
              <span class="metric-value">{{ formatEnergy(data.hf_energy_hartree) }}</span>
              <span class="metric-unit">{{ t('vqeH2.baseline.unitHartree') }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">{{ t('vqeH2.baseline.exactEnergy') }}</span>
              <span class="metric-value">{{ formatEnergy(data.exact_energy_hartree) }}</span>
              <span class="metric-unit">{{ t('vqeH2.baseline.unitHartree') }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">{{ t('vqeH2.baseline.hfError') }}</span>
              <span class="metric-value error-value">{{ formatError(data.hf_error_mhartree) }}</span>
              <span class="metric-unit">{{ t('vqeH2.baseline.unitMHartree') }}</span>
            </div>
            <div class="metric-item status-item">
              <span class="metric-label">{{ t('vqeH2.baseline.statusLabel') }}</span>
              <el-tag type="info" size="large">{{ t('vqeH2.baseline.statusReference') }}</el-tag>
            </div>
          </div>

          <div class="fetch-actions">
            <el-button @click="fetchBaseline" :loading="loading">
              {{ t('vqeH2.baseline.runBaseline') }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { getBaseline } from '@/api/vqeH2/index';

const { t } = useI18n();

const loading = ref(false);
const error = ref(false);
const data = ref(null);

function formatEnergy(val) {
  if (val == null) return '--';
  return Number(val).toFixed(8);
}

function formatError(val) {
  if (val == null) return '--';
  return Number(val).toFixed(4);
}

async function fetchBaseline() {
  loading.value = true;
  error.value = false;
  try {
    const res = await getBaseline();
    data.value = res.data || res;
  } catch (e) {
    error.value = true;
    ElMessage.error(t('vqeH2.baseline.loadFailed'));
  } finally {
    loading.value = false;
  }
}

defineExpose({ data, fetchBaseline });
</script>

<style lang="scss" scoped>
.baseline-panel {
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
  margin: 0 0 32px;
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
  gap: 16px;
}

.data-content {
  display: flex;
  flex-direction: column;
  gap: 28px;
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

.metric-value.error-value {
  color: #fb4214;
}

.metric-unit {
  font-size: 14px;
  color: #939aab;
}

.status-item {
  justify-content: center;
}

.fetch-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}
</style>
