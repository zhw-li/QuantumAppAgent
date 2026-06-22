<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import BannerSection from './components/BannerSection.vue';
import StockSelectPanel from './components/StockSelectPanel.vue';
import ModelComparePanel from './components/ModelComparePanel.vue';
import PredictionChartPanel from './components/PredictionChartPanel.vue';
import TrainingCurvePanel from './components/TrainingCurvePanel.vue';
import ArchitectureInfoPanel from './components/ArchitectureInfoPanel.vue';
import {
  fetchStocks,
  fetchComparison,
  fetchPredictions,
  fetchTrainingCurves,
  fetchRawData,
  trainModels,
  fetchModelInfo,
} from '@/api/financeQlstm/index.js';
import {
  demoStocks,
  demoComparison,
  demoPredictions,
  demoTrainingCurves,
  demoModelInfo,
  demoRawData,
} from './data.js';

const { t } = useI18n();

// Reactive state
const stocks = ref([]);
const selectedStock = ref('');
const hiddenSize = ref(8);
const nQubits = ref(4);
const epochs = ref(30);
const training = ref(false);

const comparison = ref(null);
const predictions = ref(null);
const trainingCurves = ref(null);
const rawData = ref(null);
const modelInfo = ref(null);

const useDemoData = ref(false);

// Load stocks on mount
async function loadStocks() {
  try {
    const res = await fetchStocks();
    stocks.value = res.stocks || res.data?.stocks || [];
    if (stocks.value.length > 0) {
      selectedStock.value = stocks.value[0];
    }
  } catch {
    // Fallback to demo data
    stocks.value = demoStocks;
    selectedStock.value = demoStocks[0];
    useDemoData.value = true;
  }
}

async function loadExistingResults() {
  try {
    const [compRes, predRes, curveRes, infoRes] = await Promise.allSettled([
      fetchComparison(),
      fetchPredictions(),
      fetchTrainingCurves(),
      fetchModelInfo(),
    ]);
    if (compRes.status === 'fulfilled') {
      comparison.value = compRes.value || compRes.value?.data || null;
    }
    if (predRes.status === 'fulfilled') {
      predictions.value = predRes.value || predRes.value?.data || null;
    }
    if (curveRes.status === 'fulfilled') {
      trainingCurves.value = curveRes.value || curveRes.value?.data || null;
    }
    if (infoRes.status === 'fulfilled') {
      modelInfo.value = infoRes.value || infoRes.value?.data || null;
    }
  } catch {
    // No existing results, that's fine
  }
}

async function loadRawData() {
  if (!selectedStock.value) return;
  try {
    const res = await fetchRawData(selectedStock.value, 365);
    rawData.value = res || res?.data || null;
  } catch {
    rawData.value = demoRawData;
  }
}

async function handleTrain() {
  training.value = true;
  try {
    const res = await trainModels({
      stock: selectedStock.value,
      seq_len: 20,
      hidden_size: hiddenSize.value,
      n_qubits: nQubits.value,
      qlstm_epochs: epochs.value,
      lstm_epochs: Math.round(epochs.value * 1.5),
    });

    ElMessage.success(t('financeQlstm.message.trainSuccess'));

    // Reload all results after training
    await loadAllResults();
  } catch {
    ElMessage.error(t('financeQlstm.message.trainFailed'));
    // Load demo data as fallback so the page is not empty
    comparison.value = demoComparison;
    predictions.value = demoPredictions;
    trainingCurves.value = demoTrainingCurves;
    modelInfo.value = demoModelInfo;
    rawData.value = demoRawData;
    useDemoData.value = true;
  } finally {
    training.value = false;
  }
}

async function loadAllResults() {
  await Promise.allSettled([
    loadComparison(),
    loadPredictions(),
    loadTrainingCurves(),
    loadModelInfo(),
    loadRawData(),
  ]);
}

async function loadComparison() {
  try {
    const res = await fetchComparison();
    comparison.value = res || null;
  } catch {
    comparison.value = null;
  }
}

async function loadPredictions() {
  try {
    const res = await fetchPredictions();
    predictions.value = res || null;
  } catch {
    predictions.value = null;
  }
}

async function loadTrainingCurves() {
  try {
    const res = await fetchTrainingCurves();
    trainingCurves.value = res || null;
  } catch {
    trainingCurves.value = null;
  }
}

async function loadModelInfo() {
  try {
    const res = await fetchModelInfo();
    modelInfo.value = res || null;
  } catch {
    modelInfo.value = null;
  }
}

onMounted(async () => {
  await loadStocks();
  await loadAllResults();
});
</script>

<template>
  <main class="finance-qlstm-page">
    <BannerSection />
    <StockSelectPanel
      :stocks="stocks"
      v-model:selectedStock="selectedStock"
      v-model:hiddenSize="hiddenSize"
      v-model:nQubits="nQubits"
      v-model:epochs="epochs"
      :training="training"
      @train="handleTrain"
    />
    <ModelComparePanel :comparison="comparison" />
    <PredictionChartPanel :predictions="predictions" :rawData="rawData" />
    <TrainingCurvePanel :trainingCurves="trainingCurves" />
    <ArchitectureInfoPanel :modelInfo="modelInfo" />
  </main>
</template>

<style lang="scss" scoped>
.finance-qlstm-page {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #f4f7fc;
}
</style>
