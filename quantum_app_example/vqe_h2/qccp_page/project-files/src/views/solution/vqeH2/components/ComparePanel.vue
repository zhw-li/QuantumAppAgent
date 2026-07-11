<template>
  <div class="compare-panel">
    <div class="panel-container">
      <div class="panel-card">
        <h2 class="section-title">{{ t('vqeH2.compare.title') }}</h2>

        <!-- Loading -->
        <div v-if="loading" class="loading-wrapper">
          <el-skeleton :rows="3" animated />
          <p class="loading-text">{{ t('vqeH2.compare.loading') }}</p>
        </div>

        <!-- Error with retry -->
        <div v-else-if="error" class="error-wrapper">
          <el-empty :description="t('vqeH2.compare.loadFailed')" :image-size="80" />
          <el-button type="primary" @click="fetchComparison">
            {{ t('vqeH2.compare.retry') }}
          </el-button>
        </div>

        <!-- Empty -->
        <div v-else-if="!data" class="empty-wrapper">
          <el-empty :description="t('vqeH2.compare.noData')" :image-size="80" />
        </div>

        <!-- Comparison table -->
        <div v-else class="compare-content">
          <el-table
            :data="tableData"
            border
            style="width: 100%"
            :header-cell-style="headerStyle"
            :cell-style="cellStyle"
          >
            <el-table-column
              prop="metric"
              :label="t('vqeH2.compare.metric')"
              min-width="200"
            />
            <el-table-column
              prop="classical"
              :label="t('vqeH2.compare.classical')"
              min-width="220"
            />
            <el-table-column
              prop="quantum"
              :label="t('vqeH2.compare.quantum')"
              min-width="220"
            />
          </el-table>

          <!-- Verdict -->
          <div v-if="vqeWins" class="verdict-banner">
            <span class="verdict-text">{{ t('vqeH2.compare.vqeWins') }}</span>
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
import { getComparison } from '@/api/vqeH2/index';

const { t } = useI18n();

const loading = ref(false);
const error = ref(false);
const data = ref(null);

const vqeWins = computed(() => {
  if (!data.value) return false;
  const vqeError = Math.abs(data.value.vqe?.energy_error_mhartree ?? Infinity);
  const hfError = Math.abs(data.value.baseline?.hf_error_mhartree ?? 0);
  return vqeError <= 1.6 && vqeError < hfError;
});

const tableData = computed(() => {
  if (!data.value) return [];
  const d = data.value;
  return [
    {
      metric: t('vqeH2.compare.energy'),
      classical: formatEnergy(d.baseline.hf_total_energy_hartree),
      quantum: formatEnergy(d.vqe.total_energy_hartree)
    },
    {
      metric: t('vqeH2.compare.exactEnergy'),
      classical: formatEnergy(d.baseline.exact_total_energy_hartree),
      quantum: formatEnergy(d.baseline.exact_total_energy_hartree)
    },
    {
      metric: t('vqeH2.compare.error'),
      classical: formatError(d.baseline.hf_error_mhartree),
      quantum: formatError(d.vqe.energy_error_mhartree)
    },
    {
      metric: t('vqeH2.compare.chemicalAccuracy'),
      classical: t('vqeH2.compare.notAchieved'),
      quantum: Math.abs(d.vqe.energy_error_mhartree) <= 1.6
        ? t('vqeH2.compare.achieved')
        : t('vqeH2.compare.notAchieved')
    },
    {
      metric: t('vqeH2.compare.circuitDepth'),
      classical: t('vqeH2.compare.notApplicable'),
      quantum: String(d.vqe.circuit_depth ?? '--')
    }
  ];
});

function formatEnergy(val) {
  if (val == null) return '--';
  return Number(val).toFixed(8);
}

function formatError(val) {
  if (val == null) return '--';
  return Number(val).toFixed(4);
}

function headerStyle() {
  return {
    backgroundColor: '#f3f7ff',
    color: '#020814',
    fontWeight: 600,
    fontSize: '14px'
  };
}

function cellStyle({ columnIndex }) {
  if (columnIndex === 2 && vqeWins.value) {
    return { backgroundColor: '#f3f7ff', fontWeight: 600 };
  }
  return {};
}

async function fetchComparison() {
  loading.value = true;
  error.value = false;
  try {
    const res = await getComparison();
    data.value = res.data || res;
  } catch (e) {
    error.value = true;
    ElMessage.error(t('vqeH2.compare.loadFailed'));
  } finally {
    loading.value = false;
  }
}

defineExpose({ data, fetchComparison });
</script>

<style lang="scss" scoped>
.compare-panel {
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

.compare-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.verdict-banner {
  background: #f3f7ff;
  border: 1px solid #dce0eb;
  border-radius: 8px;
  padding: 20px 28px;
  text-align: center;
}

.verdict-text {
  font-size: 18px;
  font-weight: 600;
  color: #1664ff;
}
</style>
