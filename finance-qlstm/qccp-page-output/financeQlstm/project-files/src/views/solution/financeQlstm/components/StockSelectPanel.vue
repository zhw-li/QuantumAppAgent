<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';

const { t } = useI18n();

const props = defineProps({
  stocks: { type: Array, default: () => [] },
  selectedStock: { type: String, default: '' },
  hiddenSize: { type: Number, default: 8 },
  nQubits: { type: Number, default: 4 },
  epochs: { type: Number, default: 30 },
  training: { type: Boolean, default: false },
});

const emit = defineEmits([
  'update:selectedStock',
  'update:hiddenSize',
  'update:nQubits',
  'update:epochs',
  'train',
]);

const stockOptions = computed(() =>
  props.stocks.map((s) => ({ label: s, value: s }))
);

function handleTrain() {
  if (!props.selectedStock) {
    ElMessage.warning(t('financeQlstm.message.noStock'));
    return;
  }
  emit('train');
}
</script>

<template>
  <div class="stock-select-panel wrapper">
    <el-card class="panel-card" shadow="never">
      <template #header>
        <h3 class="panel-title">{{ $t('financeQlstm.stock.title') }}</h3>
      </template>
      <div class="param-row">
        <div class="param-item">
          <span class="param-label">{{ $t('financeQlstm.stock.selectLabel') }}</span>
          <el-select
            :model-value="selectedStock"
            :placeholder="$t('financeQlstm.stock.selectPlaceholder')"
            @update:model-value="$emit('update:selectedStock', $event)"
            style="width: 180px"
          >
            <el-option
              v-for="opt in stockOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </div>
        <div class="param-item">
          <span class="param-label">{{ $t('financeQlstm.stock.hiddenSize') }}</span>
          <el-input-number
            :model-value="hiddenSize"
            :min="4"
            :max="128"
            :step="4"
            @update:model-value="$emit('update:hiddenSize', $event)"
          />
        </div>
        <div class="param-item">
          <span class="param-label">{{ $t('financeQlstm.stock.nQubits') }}</span>
          <el-input-number
            :model-value="nQubits"
            :min="2"
            :max="8"
            :step="1"
            @update:model-value="$emit('update:nQubits', $event)"
          />
        </div>
        <div class="param-item">
          <span class="param-label">{{ $t('financeQlstm.stock.epochs') }}</span>
          <el-input-number
            :model-value="epochs"
            :min="10"
            :max="200"
            :step="10"
            @update:model-value="$emit('update:epochs', $event)"
          />
        </div>
        <div class="param-item param-action">
          <el-button
            type="primary"
            :loading="training"
            @click="handleTrain"
          >
            {{ training ? $t('financeQlstm.stock.training') : $t('financeQlstm.stock.startTrain') }}
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.stock-select-panel {
  margin-top: 30px;
}

.panel-card {
  border-radius: 8px;
  border: 1px solid #DCE0EB;
}

.panel-title {
  font-size: 24px;
  font-weight: regular;
  color: #020814;
  margin: 0;
}

.param-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 30px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.param-label {
  font-size: 16px;
  color: #41464F;
  white-space: nowrap;
}

.param-action {
  margin-left: auto;
}
</style>
