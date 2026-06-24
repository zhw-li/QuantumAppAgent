<script setup>
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { getStocks, getStockHistory } from '@/api/financeQaoa/index.js';

const { t } = useI18n();

const loading = ref(false);
const loadError = ref(false);
const stocks = ref([]);
const tiers = ref({ demo: [], standard: [], full: [] });
const currentTier = ref('demo');
const selectedSymbol = ref('');
const priceHistory = ref([]);

const chartRefs = reactive({});
const chartInstances = reactive({});

const tierSymbols = computed(() => {
  return tiers.value[currentTier.value] || [];
});

const filteredStocks = computed(() => {
  const syms = tierSymbols.value;
  return stocks.value.filter((s) => syms.includes(s.symbol));
});

const initChart = (key, el) => {
  if (!el || el.offsetWidth === 0) return null;
  if (chartInstances[key]) {
    chartInstances[key].dispose();
  }
  const instance = echarts.init(el);
  chartInstances[key] = instance;
  return instance;
};

const renderPriceTrend = () => {
  nextTick(() => {
    const el = chartRefs.priceTrend;
    if (!el || el.offsetWidth === 0 || !priceHistory.value.length) return;
    const instance = initChart('priceTrend', el);
    if (!instance) return;

    const dates = priceHistory.value.map((d) => d.date);
    const closes = priceHistory.value.map((d) => d.close);

    instance.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 60, right: 30, top: 30, bottom: 40 },
      xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', scale: true, axisLabel: { fontSize: 11 } },
      series: [
        {
          type: 'line',
          data: closes,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: '#1664FF' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(22,100,255,0.25)' },
              { offset: 1, color: 'rgba(22,100,255,0.02)' },
            ]),
          },
        },
      ],
    });
  });
};

const loadData = async () => {
  loading.value = true;
  loadError.value = false;
  try {
    const res = await getStocks();
    if (res.code === 200 && res.data) {
      stocks.value = res.data.stocks || [];
      tiers.value = res.data.tiers || { demo: [], standard: [], full: [] };
      if (tierSymbols.value.length > 0 && !selectedSymbol.value) {
        selectedSymbol.value = tierSymbols.value[0];
      }
    } else {
      loadError.value = true;
    }
  } catch {
    loadError.value = true;
    ElMessage.error(t('financeQaoa.message.networkError'));
  } finally {
    loading.value = false;
  }
};

const loadPriceHistory = async () => {
  if (!selectedSymbol.value) return;
  try {
    const res = await getStockHistory(selectedSymbol.value, 365);
    if (res.code === 200 && res.data) {
      priceHistory.value = res.data.history || [];
      renderPriceTrend();
    }
  } catch {
    ElMessage.error(t('financeQaoa.message.loadFailed'));
  }
};

watch(currentTier, () => {
  const syms = tierSymbols.value;
  if (syms.length > 0) {
    selectedSymbol.value = syms[0];
  }
});

watch(selectedSymbol, () => {
  loadPriceHistory();
});

const handleResize = () => {
  Object.values(chartInstances).forEach((inst) => {
    if (inst && !inst.isDisposed()) {
      inst.resize();
    }
  });
};

const onVisible = () => {
  setTimeout(() => {
    renderPriceTrend();
  }, 250);
};

onBeforeUnmount(() => {
  Object.values(chartInstances).forEach((inst) => {
    if (inst && !inst.isDisposed()) {
      inst.dispose();
    }
  });
  window.removeEventListener('resize', handleResize);
});

window.addEventListener('resize', handleResize);
loadData();

defineExpose({ onVisible });
</script>

<template>
  <div class="dashboard-tab">
    <div v-if="loading" class="tab-loading">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>{{ t('financeQaoa.common.loading') }}</span>
    </div>

    <div v-else-if="loadError" class="tab-error">
      <el-empty :description="t('financeQaoa.message.loadFailed')">
        <el-button type="primary" @click="loadData">{{ t('financeQaoa.common.retry') }}</el-button>
      </el-empty>
    </div>

    <template v-else>
      <!-- Tier selector -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.dashboard.tier') }}</span>
        </div>
        <el-radio-group v-model="currentTier" size="default">
          <el-radio-button value="demo">{{ t('financeQaoa.dashboard.tierDemo') }}</el-radio-button>
          <el-radio-button value="standard">{{ t('financeQaoa.dashboard.tierStandard') }}</el-radio-button>
          <el-radio-button value="full">{{ t('financeQaoa.dashboard.tierFull') }}</el-radio-button>
        </el-radio-group>
      </div>

      <!-- Stock cards -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.dashboard.stockCards') }}</span>
        </div>
        <div class="stock-cards-grid">
          <div
            v-for="stock in filteredStocks"
            :key="stock.symbol"
            class="stock-card"
            :class="{ 'stock-card--active': selectedSymbol === stock.symbol }"
            @click="selectedSymbol = stock.symbol"
          >
            <div class="stock-card__symbol">{{ stock.symbol }}</div>
            <div class="stock-card__price">
              <span class="stock-card__label">{{ t('financeQaoa.dashboard.latestPrice') }}</span>
              <span class="stock-card__value">${{ stock.latest_price }}</span>
            </div>
            <div class="stock-card__return">
              <span class="stock-card__label">{{ t('financeQaoa.dashboard.totalReturn') }}</span>
              <span
                class="stock-card__value"
                :class="stock.total_return >= 0 ? 'text-up' : 'text-down'"
              >
                {{ stock.total_return >= 0 ? '+' : '' }}{{ stock.total_return }}%
              </span>
            </div>
            <div class="stock-card__points">
              <span class="stock-card__label">{{ t('financeQaoa.dashboard.dataPoints') }}</span>
              <span class="stock-card__value text-sub">{{ stock.data_points }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Price trend -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">{{ t('financeQaoa.dashboard.priceTrend') }}</span>
          <el-select v-model="selectedSymbol" size="default" style="width: 160px">
            <el-option
              v-for="sym in tierSymbols"
              :key="sym"
              :label="sym"
              :value="sym"
            />
          </el-select>
        </div>
        <div
          ref="chartRefs.priceTrend"
          class="chart-container"
        ></div>
      </div>
    </template>
  </div>
</template>

<style lang="scss" scoped>
.dashboard-tab {
  width: 100%;
}

.tab-loading,
.tab-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 12px;
  color: #939aab;
}

.section-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #020814;
}

.stock-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.stock-card {
  background: #f3f7ff;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;

  &:hover {
    border-color: #4f9df7;
  }

  &--active {
    border-color: #1664ff;
  }

  &__symbol {
    font-size: 20px;
    font-weight: 700;
    color: #020814;
    margin-bottom: 10px;
  }

  &__label {
    font-size: 12px;
    color: #939aab;
    margin-right: 6px;
  }

  &__value {
    font-size: 14px;
    font-weight: 600;
    color: #020814;
  }

  &__price,
  &__return,
  &__points {
    display: flex;
    align-items: center;
    margin-bottom: 4px;
  }
}

.text-up {
  color: #1664ff;
}

.text-down {
  color: #fb4214;
}

.text-sub {
  color: #939aab;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
