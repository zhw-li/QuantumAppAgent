<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  modelInfo: { type: Object, default: null },
});
</script>

<template>
  <div class="architecture-info-panel wrapper">
    <h2 class="section-title">{{ $t('financeQlstm.architecture.title') }}</h2>
    <template v-if="modelInfo">
      <div class="arch-grid">
        <!-- QLSTM Architecture -->
        <el-card class="arch-card" shadow="never">
          <div class="card-header">
            <span class="card-badge qlstm-badge">QLSTM</span>
            <h3 class="card-title">{{ $t('financeQlstm.architecture.qlstm') }}</h3>
          </div>
          <el-descriptions :column="1" border size="default">
            <el-descriptions-item :label="$t('financeQlstm.architecture.nQubits')">
              {{ modelInfo.QLSTM.n_qubits }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('financeQlstm.architecture.layers')">
              {{ modelInfo.QLSTM.layers }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('financeQlstm.architecture.hiddenSize')">
              {{ modelInfo.QLSTM.hidden_size }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('financeQlstm.architecture.vqcStructure')">
              RY + RX encoding / RY + RZ variational / CNOT ring
            </el-descriptions-item>
            <el-descriptions-item :label="$t('financeQlstm.architecture.totalParams')">
              {{ modelInfo.QLSTM.total_params.toLocaleString() }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- LSTM Architecture -->
        <el-card class="arch-card" shadow="never">
          <div class="card-header">
            <span class="card-badge lstm-badge">LSTM</span>
            <h3 class="card-title">{{ $t('financeQlstm.architecture.lstm') }}</h3>
          </div>
          <el-descriptions :column="1" border size="default">
            <el-descriptions-item :label="$t('financeQlstm.architecture.hiddenSize')">
              {{ modelInfo.LSTM.hidden_size }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('financeQlstm.architecture.numLayers')">
              {{ modelInfo.LSTM.num_layers }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('financeQlstm.architecture.totalParams')">
              {{ modelInfo.LSTM.total_params.toLocaleString() }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>
    </template>
    <el-empty v-else :description="$t('financeQlstm.architecture.noData')" />
  </div>
</template>

<style lang="scss" scoped>
.architecture-info-panel {
  margin-top: 30px;
  padding-bottom: 80px;
}

.section-title {
  font-size: 30px;
  font-weight: regular;
  color: #020814;
  margin: 0 0 20px;
}

.arch-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.arch-card {
  border-radius: 8px;
  border: 1px solid #DCE0EB;
  background: #ffffff;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
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
</style>
