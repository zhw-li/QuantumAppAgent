<script setup>
import { onBeforeUnmount, ref, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import DashboardTab from './components/DashboardTab.vue';
import StatisticsTab from './components/StatisticsTab.vue';
import ClassicalTab from './components/ClassicalTab.vue';
import QuantumTab from './components/QuantumTab.vue';
import CompareTab from './components/CompareTab.vue';
import { getHealth } from '@/api/financeQaoa/index.js';

const { t } = useI18n();

const activeTab = ref('dashboard');
const currentTier = ref('demo');
const serviceStatus = ref(null);
const statusLoading = ref(false);

const dashboardRef = ref(null);
const statisticsRef = ref(null);
const classicalRef = ref(null);
const quantumRef = ref(null);
const compareRef = ref(null);

const tabRefs = {
  dashboard: dashboardRef,
  statistics: statisticsRef,
  classical: classicalRef,
  quantum: quantumRef,
  compare: compareRef,
};

const checkHealth = async () => {
  statusLoading.value = true;
  try {
    const res = await getHealth();
    if (res.code === 200 && res.data) {
      serviceStatus.value = res.data;
    }
  } catch {
    serviceStatus.value = null;
  } finally {
    statusLoading.value = false;
  }
};

const handleTabChange = (tab) => {
  nextTick(() => {
    setTimeout(() => {
      const comp = tabRefs[tab];
      if (comp.value && typeof comp.value.onVisible === 'function') {
        comp.value.onVisible();
      }
    }, 200);
  });
};

checkHealth();
</script>

<template>
  <main class="finance-qaoa-page">
    <!-- Hero banner -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">{{ $t('financeQaoa.hero.title') }}</h1>
        <p class="hero-subtitle">{{ $t('financeQaoa.hero.subtitle') }}</p>
        <div v-if="serviceStatus" class="hero-status">
          <span class="status-dot" />
          <span class="status-text">{{ serviceStatus.service }} - OK</span>
        </div>
      </div>
    </section>

    <!-- Main content with tabs -->
    <section class="content-section">
      <div class="content-wrapper">
        <el-tabs v-model="activeTab" class="main-tabs" @tab-change="handleTabChange">
          <el-tab-pane :label="$t('financeQaoa.tabs.dashboard')" name="dashboard">
            <DashboardTab ref="dashboardRef" :tier="currentTier" />
          </el-tab-pane>

          <el-tab-pane :label="$t('financeQaoa.tabs.statistics')" name="statistics">
            <StatisticsTab ref="statisticsRef" :tier="currentTier" />
          </el-tab-pane>

          <el-tab-pane :label="$t('financeQaoa.tabs.classical')" name="classical">
            <ClassicalTab ref="classicalRef" :tier="currentTier" />
          </el-tab-pane>

          <el-tab-pane :label="$t('financeQaoa.tabs.quantum')" name="quantum">
            <QuantumTab ref="quantumRef" :tier="currentTier" />
          </el-tab-pane>

          <el-tab-pane :label="$t('financeQaoa.tabs.compare')" name="compare">
            <CompareTab ref="compareRef" :tier="currentTier" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </section>
  </main>
</template>

<style lang="scss" scoped>
.finance-qaoa-page {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #f4f7fc;
}

.hero-section {
  background: linear-gradient(135deg, #1664ff 0%, #4f9df7 100%);
  padding: 60px 0;
}

.hero-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 140px;
}

.hero-title {
  font-size: 40px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 12px 0;
}

.hero-subtitle {
  font-size: 18px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.85);
  margin: 0 0 16px 0;
}

.hero-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00c7e7;
}

.status-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
}

.content-section {
  padding: 30px 0;
}

.content-wrapper {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 140px;
}

.main-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 20px;
  }

  :deep(.el-tabs__item) {
    font-size: 16px;
    font-weight: 500;
  }

  :deep(.el-tabs__item.is-active) {
    color: #1664ff;
  }

  :deep(.el-tabs__active-bar) {
    background-color: #1664ff;
  }
}

@media (max-width: 1600px) {
  .hero-content,
  .content-wrapper {
    padding-left: 60px;
    padding-right: 60px;
  }
}

@media (max-width: 1200px) {
  .hero-content,
  .content-wrapper {
    padding-left: 30px;
    padding-right: 30px;
  }

  .hero-title {
    font-size: 32px;
  }
}
</style>
