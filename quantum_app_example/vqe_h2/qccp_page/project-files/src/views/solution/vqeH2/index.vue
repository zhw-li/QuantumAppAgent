<template>
  <div class="vqe-h2-page">
    <!-- Section 1: Algorithm Introduction -->
    <AlgorithmIntro />

    <!-- Section 2: Classical Baseline -->
    <BaselinePanel ref="baselineRef" />

    <!-- Section 3: VQE Quantum Algorithm -->
    <VqePanel ref="vqeRef" />

    <!-- Section 4: Results Comparison -->
    <ComparePanel ref="compareRef" />

    <!-- Section 5: Method Details -->
    <div class="method-section">
      <div class="method-container">
        <div class="method-card">
          <h2 class="section-title">{{ t('vqeH2.method.title') }}</h2>
          <div class="method-grid">
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.molecule') }}</span>
              <span class="method-value">{{ t('vqeH2.method.moleculeValue') }}</span>
            </div>
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.basis') }}</span>
              <span class="method-value">{{ t('vqeH2.method.basisValue') }}</span>
            </div>
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.bondLength') }}</span>
              <span class="method-value">{{ t('vqeH2.method.bondLengthValue') }}</span>
            </div>
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.ansatz') }}</span>
              <span class="method-value">{{ t('vqeH2.method.ansatzValue') }}</span>
            </div>
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.optimizer') }}</span>
              <span class="method-value">{{ t('vqeH2.method.optimizerValue') }}</span>
            </div>
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.backend') }}</span>
              <span class="method-value">{{ t('vqeH2.method.backendValue') }}</span>
            </div>
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.qubits') }}</span>
              <span class="method-value">2</span>
            </div>
            <div class="method-item">
              <span class="method-label">{{ t('vqeH2.method.layers') }}</span>
              <span class="method-value">2</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import AlgorithmIntro from './components/AlgorithmIntro.vue';
import BaselinePanel from './components/BaselinePanel.vue';
import VqePanel from './components/VqePanel.vue';
import ComparePanel from './components/ComparePanel.vue';

const route = useRoute();
const router = useRouter();
const { locale, t } = useI18n();

const baselineRef = ref(null);
const vqeRef = ref(null);
const compareRef = ref(null);

onMounted(() => {
  document.title = t('vqeH2.pageTitle');
});

onBeforeUnmount(() => {
});
</script>

<style lang="scss" scoped>
.vqe-h2-page {
  width: 100%;
  min-height: 100vh;
  background: #f4f7fc;
  padding-bottom: 60px;
}

.method-section {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0 0 24px;
}

.method-container {
  width: 100%;
  max-width: 1440px;
  padding: 0 24px;
}

.method-card {
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

.method-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.method-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px 20px;
  background: #f3f7ff;
  border-radius: 8px;
  border: 1px solid #dce0eb;
}

.method-label {
  font-size: 14px;
  color: #939aab;
}

.method-value {
  font-size: 18px;
  font-weight: 600;
  color: #020814;
}
</style>
