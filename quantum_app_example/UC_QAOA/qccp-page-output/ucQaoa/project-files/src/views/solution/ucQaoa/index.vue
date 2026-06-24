<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { getGenerators, solveQAOA, solveClassical } from '@/api/ucQaoa/index.js';
import * as echarts from 'echarts';

const { locale, t } = useI18n();

const loading = ref(false);
const solving = ref(false);
const error = ref('');
const result = ref(null);
const classicalResult = ref(null);

const selectedGens = ref([]);
const loads = ref([400, 600]);
const qaoaLayers = ref(2);
const restarts = ref(10);

const generators = ref([
  { id: 'A', name: 'Gen A', p_max: 300, a: 800, b: 12, c: 0.014 },
  { id: 'B', name: 'Gen B', p_max: 420, a: 900, b: 13, c: 0.014 },
  { id: 'C', name: 'Gen C', p_max: 550, a: 1100, b: 14, c: 0.016 },
  { id: 'D', name: 'Gen D', p_max: 700, a: 1300, b: 16, c: 0.017 },
  { id: 'E', name: 'Gen E', p_max: 850, a: 1500, b: 17, c: 0.018 },
  { id: 'F', name: 'Gen F', p_max: 1000, a: 1700, b: 18, c: 0.019 },
]);

const loadOptions = [400, 600, 700];

const qubitCount = computed(() => selectedGens.value.length * loads.value.length);

const canSolve = computed(
  () => selectedGens.value.length >= 2 && selectedGens.value.length <= 4 && loads.value.length >= 1
);

const selectedGenDetails = computed(() =>
  generators.value.filter(g => selectedGens.value.includes(g.id))
);

const gapClass = computed(() => {
  if (!result.value || result.value.optimality_gap < 0) return '';
  if (result.value.optimality_gap <= 5) return 'good';
  if (result.value.optimality_gap <= 15) return 'medium';
  return 'poor';
});

const tableData = computed(() => {
  if (!result.value || !result.value.schedule) return [];
  const genIds = selectedGens.value;
  const nPeriods = loads.value.length;
  const rows = [];
  for (let t = 1; t <= nPeriods; t++) {
    const row = { period: `Hour ${t}`, gens: {}, totalPower: 0, load: loads.value[t - 1] };
    for (const gid of genIds) {
      const entry = result.value.schedule.find(e => e.period === t && e.generator_id === gid);
      const status = entry ? entry.status === 1 : false;
      const power = entry && entry.status === 1 ? entry.power : 0;
      row.gens[gid] = { status, power };
      if (status) row.totalPower += power;
    }
    rows.push(row);
  }
  return rows;
});

function toggleGen(id) {
  const idx = selectedGens.value.indexOf(id);
  if (idx >= 0) {
    selectedGens.value.splice(idx, 1);
  } else if (selectedGens.value.length < 4) {
    selectedGens.value.push(id);
  }
}

function addPeriod() {
  if (loads.value.length < 6) {
    loads.value.push(400);
  }
}

function removePeriod(idx) {
  if (loads.value.length > 1) {
    loads.value.splice(idx, 1);
  }
}

function formatCost(cost) {
  if (cost === null || cost === undefined) return 'N/A';
  return cost.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

function formatFormula(gen) {
  return `${gen.a}+${gen.b}P+${gen.c}P\u00B2`;
}

function getGenStatus(period, genId) {
  if (!result.value || !result.value.schedule) return false;
  const entry = result.value.schedule.find(
    e => e.period === period && e.generator_id === genId
  );
  return entry ? entry.status === 1 : false;
}

function getGenPower(period, genId) {
  if (!result.value || !result.value.schedule) return 0;
  const entry = result.value.schedule.find(
    e => e.period === period && e.generator_id === genId
  );
  return entry ? entry.power : 0;
}

function getTotalPower(period) {
  if (!result.value || !result.value.schedule) return 0;
  return result.value.schedule
    .filter(e => e.period === period && e.status === 1)
    .reduce((sum, e) => sum + e.power, 0);
}

async function solve() {
  solving.value = true;
  error.value = '';
  result.value = null;
  classicalResult.value = null;

  try {
    const res = await solveQAOA({
      generator_ids: selectedGens.value,
      loads: loads.value,
      qaoa_layers: qaoaLayers.value,
      restarts: restarts.value,
    });
    if (res.code === 200) {
      result.value = res.data;
    } else {
      throw new Error(res.message || t('ucQaoa.message.solveFailed'));
    }

    if (qubitCount.value <= 20) {
      try {
        const cRes = await solveClassical({
          generator_ids: selectedGens.value,
          loads: loads.value,
          qaoa_layers: qaoaLayers.value,
          restarts: restarts.value,
        });
        if (cRes.code === 200) {
          classicalResult.value = cRes.data;
        }
      } catch (e) {
        // ignore classical solve failure
      }
    }

    await nextTick();
    setTimeout(() => {
      renderCompareChart();
      renderScheduleChart();
      renderCostChart();
    }, 150);
  } catch (e) {
    error.value = e.message || t('ucQaoa.message.networkError');
    ElMessage.error(error.value);
  } finally {
    solving.value = false;
  }
}

let chartInstances = [];

function disposeCharts() {
  chartInstances.forEach(c => c && c.dispose());
  chartInstances = [];
}

function getGenColor(index) {
  const colors = ['#1664FF', '#722ED1', '#00B42A', '#FF7D00', '#FB4214', '#00C7E7'];
  return colors[index % colors.length];
}

function renderScheduleChart() {
  const chartDom = document.getElementById('uc-schedule-chart');
  if (!chartDom || !result.value) return;
  const chart = echarts.init(chartDom);
  chartInstances.push(chart);

  const schedule = result.value.schedule;
  const genIds = selectedGens.value;
  const nPeriods = loads.value.length;

  const heatData = [];
  for (let t = 1; t <= nPeriods; t++) {
    for (let gi = 0; gi < genIds.length; gi++) {
      const entry = schedule.find(e => e.period === t && e.generator_id === genIds[gi]);
      const isOn = entry && entry.status === 1;
      heatData.push([t - 1, gi, isOn ? 1 : 0]);
    }
  }

  const genNames = genIds.map(gid => {
    const g = generators.value.find(x => x.id === gid);
    return `${g.name} (${g.p_max}MW)`;
  });

  chart.setOption({
    tooltip: {
      formatter(params) {
        const t = params.value[0] + 1;
        const gi = params.value[1];
        const isOn = params.value[2] === 1;
        const entry = schedule.find(e => e.period === t && e.generator_id === genIds[gi]);
        const power = entry && entry.status === 1 ? entry.power.toFixed(0) : 0;
        const cost = entry && entry.status === 1 ? formatCost(entry.cost) : 0;
        return `Hour ${t} - ${genNames[gi]}<br/>${
          t('ucQaoa.result.status')
        }: ${isOn ? t('ucQaoa.result.on') : t('ucQaoa.result.off')}<br/>${
          isOn ? `${t('ucQaoa.result.power')}: ${power} MW<br/>${t('ucQaoa.result.cost')}: ${cost} $` : ''
        }`;
      },
    },
    grid: { top: 20, right: 60, bottom: 40, left: 120 },
    xAxis: {
      type: 'category',
      data: Array.from({ length: nPeriods }, (_, i) => `Hour ${i + 1}`),
    },
    yAxis: {
      type: 'category',
      data: genNames,
      inverse: true,
    },
    visualMap: {
      min: 0,
      max: 1,
      show: false,
      inRange: { color: ['#DCE0EB', '#1664FF'] },
    },
    series: [
      {
        type: 'heatmap',
        data: heatData,
        label: {
          show: true,
          formatter(params) {
            const t = params.value[0] + 1;
            const gi = params.value[1];
            const entry = schedule.find(e => e.period === t && e.generator_id === genIds[gi]);
            if (entry && entry.status === 1) {
              return entry.power.toFixed(0) + 'MW';
            }
            return t('ucQaoa.result.off');
          },
          color: '#fff',
          fontSize: 11,
        },
        itemStyle: {
          borderColor: '#F4F7FC',
          borderWidth: 3,
          borderRadius: 4,
        },
      },
    ],
  });

  const resizeHandler = () => chart.resize();
  window.addEventListener('resize', resizeHandler);
  onBeforeUnmount(() => window.removeEventListener('resize', resizeHandler));
}

function renderCostChart() {
  const chartDom = document.getElementById('uc-cost-chart');
  if (!chartDom || !result.value) return;
  const chart = echarts.init(chartDom);
  chartInstances.push(chart);

  const schedule = result.value.schedule;
  const genIds = selectedGens.value;
  const nPeriods = loads.value.length;

  const series = genIds.map((gid, gi) => {
    const gen = generators.value.find(g => g.id === gid);
    const data = [];
    for (let t = 1; t <= nPeriods; t++) {
      const entry = schedule.find(e => e.period === t && e.generator_id === gid);
      data.push(entry && entry.status === 1 ? Math.round(entry.cost) : 0);
    }
    return {
      name: gen.name,
      type: 'bar',
      stack: 'cost',
      data,
      itemStyle: { color: getGenColor(gi) },
    };
  });

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter(params) {
        let html = `<b>${params[0].axisValue}</b><br/>`;
        let total = 0;
        params.forEach(p => {
          if (p.value > 0) {
            html += `${p.marker} ${p.seriesName}: ${formatCost(p.value)} $<br/>`;
            total += p.value;
          }
        });
        html += `<b>${t('ucQaoa.result.total')}: ${formatCost(total)} $</b>`;
        return html;
      },
    },
    legend: {
      data: genIds.map(gid => generators.value.find(g => g.id === gid).name),
    },
    grid: { top: 50, right: 30, bottom: 30, left: 70 },
    xAxis: {
      type: 'category',
      data: Array.from({ length: nPeriods }, (_, i) => `Hour ${i + 1}`),
    },
    yAxis: {
      type: 'value',
      name: `${t('ucQaoa.result.cost')} ($)`,
      splitLine: { lineStyle: { color: '#DCE0EB' } },
    },
    series,
  });

  const resizeHandler = () => chart.resize();
  window.addEventListener('resize', resizeHandler);
  onBeforeUnmount(() => window.removeEventListener('resize', resizeHandler));
}

function renderCompareChart() {
  const chartDom = document.getElementById('uc-compare-chart');
  if (!chartDom || !result.value) return;
  const classicCost = result.value.classical_optimal_cost;
  if (classicCost <= 0) return;

  const chart = echarts.init(chartDom);
  chartInstances.push(chart);
  const qaoaCost = result.value.total_cost;
  const gap = result.value.optimality_gap;

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter(params) {
        return params[0].name + ': ' + formatCost(params[0].value) + ' $';
      },
    },
    grid: { top: 50, right: 30, bottom: 30, left: 80 },
    xAxis: {
      type: 'category',
      data: [t('ucQaoa.result.qaoaLabel'), t('ucQaoa.result.classicalLabel')],
    },
    yAxis: {
      type: 'value',
      name: `${t('ucQaoa.result.totalCost')} ($)`,
      splitLine: { lineStyle: { color: '#DCE0EB' } },
      min(value) {
        return Math.floor(value.min * 0.95);
      },
    },
    series: [
      {
        type: 'bar',
        data: [
          {
            value: qaoaCost,
            itemStyle: { color: '#1664FF', borderRadius: [6, 6, 0, 0] },
          },
          {
            value: classicCost,
            itemStyle: { color: '#FF7D00', borderRadius: [6, 6, 0, 0] },
          },
        ],
        barWidth: '35%',
        label: {
          show: true,
          position: 'top',
          formatter: p => formatCost(p.value) + ' $',
          color: '#41464F',
          fontSize: 12,
          fontWeight: 'bold',
        },
      },
    ],
    graphic: gap >= 0
      ? [
          {
            type: 'text',
            left: 'center',
            top: 5,
            style: {
              text: `${t('ucQaoa.result.gap')}: ${gap.toFixed(2)}%`,
              fill: gap <= 5 ? '#00B42A' : gap <= 15 ? '#FF7D00' : '#FB4214',
              fontSize: 14,
              fontWeight: 'bold',
              fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
            },
          },
        ]
      : [],
  });

  const resizeHandler = () => chart.resize();
  window.addEventListener('resize', resizeHandler);
  onBeforeUnmount(() => window.removeEventListener('resize', resizeHandler));
}

onBeforeUnmount(() => {
  disposeCharts();
});
</script>

<template>
  <main class="uc-qaoa-page">
    <!-- Banner -->
    <section class="page-banner">
      <div class="wrapper">
        <h1 class="banner-title">{{ $t('ucQaoa.banner.title') }}</h1>
        <p class="banner-desc">{{ $t('ucQaoa.banner.desc') }}</p>
      </div>
    </section>

    <div class="wrapper">
      <!-- Step 1: Generator Selection -->
      <section class="section-card">
        <div class="section-header">
          <span class="step-badge">1</span>
          <h2 class="section-title">{{ $t('ucQaoa.step1.title') }}</h2>
          <span class="section-hint">{{ $t('ucQaoa.step1.hint') }}</span>
        </div>
        <div class="gen-grid">
          <div
            v-for="gen in generators"
            :key="gen.id"
            class="gen-card"
            :class="{
              selected: selectedGens.includes(gen.id),
              disabled: !selectedGens.includes(gen.id) && selectedGens.length >= 4,
            }"
            @click="toggleGen(gen.id)"
          >
            <div class="gen-id">{{ gen.id }}</div>
            <div class="gen-name">{{ gen.name }}</div>
            <div class="gen-spec">
              <div class="spec-row">
                <span class="spec-label">{{ $t('ucQaoa.gen.maxPower') }}</span>
                <span class="spec-value">{{ gen.p_max }} MW</span>
              </div>
              <div class="spec-row">
                <span class="spec-label">{{ $t('ucQaoa.gen.costFunc') }}</span>
                <span class="spec-value spec-formula">{{ formatFormula(gen) }}</span>
              </div>
              <div class="spec-row">
                <span class="spec-label">{{ $t('ucQaoa.gen.fullCost') }}</span>
                <span class="spec-value spec-cost">
                  {{ formatCost(gen.a + gen.b * gen.p_max + gen.c * gen.p_max * gen.p_max) }} $
                </span>
              </div>
            </div>
            <div v-if="selectedGens.includes(gen.id)" class="gen-check"></div>
          </div>
        </div>
      </section>

      <!-- Step 2: Period Load Config -->
      <section class="section-card">
        <div class="section-header">
          <span class="step-badge">2</span>
          <h2 class="section-title">{{ $t('ucQaoa.step2.title') }}</h2>
          <span class="section-hint">{{ $t('ucQaoa.step2.hint') }}</span>
        </div>
        <div class="period-config">
          <div v-for="(load, idx) in loads" :key="idx" class="period-row">
            <span class="period-label">Hour {{ idx + 1 }}</span>
            <div class="load-options">
              <el-button
                v-for="opt in loadOptions"
                :key="opt"
                :type="loads[idx] === opt ? 'primary' : 'default'"
                size="small"
                @click="loads[idx] = opt"
              >
                {{ opt }} MW
              </el-button>
              <el-button
                v-if="loads.length > 1"
                type="danger"
                size="small"
                text
                @click="removePeriod(idx)"
              >
                {{ $t('ucQaoa.step2.remove') }}
              </el-button>
            </div>
          </div>
          <el-button
            v-if="loads.length < 6"
            type="primary"
            text
            :disabled="selectedGens.length === 0"
            @click="addPeriod"
          >
            + {{ $t('ucQaoa.step2.addPeriod') }}
          </el-button>
        </div>
        <div class="qubit-info">
          <span>{{ $t('ucQaoa.step2.qubit') }}: {{ selectedGens.length }} x {{ loads.length }} = <strong>{{ qubitCount }}</strong></span>
        </div>
      </section>

      <!-- Step 3: QAOA Params -->
      <section class="section-card">
        <div class="section-header">
          <span class="step-badge">3</span>
          <h2 class="section-title">{{ $t('ucQaoa.step3.title') }}</h2>
        </div>
        <div class="params-grid">
          <div class="param-item">
            <label>{{ $t('ucQaoa.step3.layers') }}</label>
            <el-slider v-model="qaoaLayers" :min="1" :max="5" :step="1" show-input />
            <p class="param-desc">{{ $t('ucQaoa.step3.layersDesc') }}</p>
          </div>
          <div class="param-item">
            <label>{{ $t('ucQaoa.step3.restarts') }}</label>
            <el-slider v-model="restarts" :min="5" :max="30" :step="5" show-input />
            <p class="param-desc">{{ $t('ucQaoa.step3.restartsDesc') }}</p>
          </div>
        </div>
      </section>

      <!-- Solve -->
      <div class="solve-section">
        <el-button
          type="primary"
          size="large"
          :loading="solving"
          :disabled="!canSolve"
          @click="solve"
        >
          {{ solving ? $t('ucQaoa.solve.solving') : $t('ucQaoa.solve.start') }}
        </el-button>
      </div>

      <!-- Error -->
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-close
        @close="error = ''"
        style="margin-bottom: 20px;"
      />

      <!-- Result -->
      <section v-if="result" class="section-card result-section">
        <div class="section-header">
          <span class="step-badge step-badge--success">OK</span>
          <h2 class="section-title">{{ $t('ucQaoa.result.title') }}</h2>
          <el-tag :type="result.status === 'success' ? 'success' : 'danger'" class="result-tag">
            {{ result.status === 'success' ? $t('ucQaoa.result.success') : $t('ucQaoa.result.infeasible') }}
          </el-tag>
        </div>

        <!-- Metrics -->
        <div class="metrics-grid">
          <div class="metric-card metric-card--highlight">
            <div class="metric-label">{{ $t('ucQaoa.result.qaoaCost') }}</div>
            <div class="metric-value metric-value--primary">{{ formatCost(result.total_cost) }} $</div>
          </div>
          <div v-if="result.classical_optimal_cost > 0" class="metric-card">
            <div class="metric-label">{{ $t('ucQaoa.result.classicalCost') }}</div>
            <div class="metric-value metric-value--warning">{{ formatCost(result.classical_optimal_cost) }} $</div>
          </div>
          <div v-if="result.optimality_gap >= 0" class="metric-card">
            <div class="metric-label">{{ $t('ucQaoa.result.gap') }}</div>
            <div class="metric-value" :class="'metric-value--' + gapClass">
              {{ result.optimality_gap.toFixed(2) }}%
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('ucQaoa.result.qubits') }}</div>
            <div class="metric-value">{{ result.qubit_count }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('ucQaoa.result.layers') }}</div>
            <div class="metric-value">p = {{ result.qaoa_layers }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">{{ $t('ucQaoa.result.time') }}</div>
            <div class="metric-value">{{ result.solve_time.toFixed(1) }}s</div>
          </div>
        </div>

        <!-- Compare Chart -->
        <div v-if="result.classical_optimal_cost > 0" class="chart-block">
          <h3 class="chart-title">{{ $t('ucQaoa.result.compare') }}</h3>
          <div id="uc-compare-chart" class="chart-container" />
        </div>

        <!-- Schedule Chart -->
        <div class="chart-block">
          <h3 class="chart-title">{{ $t('ucQaoa.result.schedule') }}</h3>
          <div id="uc-schedule-chart" class="chart-container" />
        </div>

        <!-- Schedule Table -->
        <div class="table-block">
          <h3 class="chart-title">{{ $t('ucQaoa.result.detailTable') }}</h3>
          <el-table :data="tableData" border stripe style="width: 100%">
            <el-table-column prop="period" :label="$t('ucQaoa.result.period')" width="100" />
            <el-table-column
              v-for="gen in selectedGenDetails"
              :key="gen.id"
              :label="`${gen.name} (${gen.p_max}MW)`"
              width="160"
            >
              <template #default="{ row }">
                <el-tag v-if="row.gens[gen.id]?.status" type="success" size="small">
                  ON / {{ row.gens[gen.id].power.toFixed(0) }}MW
                </el-tag>
                <el-tag v-else type="info" size="small">OFF</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('ucQaoa.result.totalPower')" width="120">
              <template #default="{ row }">
                {{ row.totalPower.toFixed(0) }} MW
              </template>
            </el-table-column>
            <el-table-column :label="$t('ucQaoa.result.loadDemand')" width="120">
              <template #default="{ row }">
                {{ row.load }} MW
              </template>
            </el-table-column>
            <el-table-column :label="$t('ucQaoa.result.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="row.totalPower >= row.load ? 'success' : 'danger'" size="small">
                  {{ row.totalPower >= row.load ? $t('ucQaoa.result.satisfied') : $t('ucQaoa.result.unsatisfied') }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Cost Chart -->
        <div class="chart-block">
          <h3 class="chart-title">{{ $t('ucQaoa.result.costDistribution') }}</h3>
          <div id="uc-cost-chart" class="chart-container" />
        </div>
      </section>
    </div>
  </main>
</template>

<style lang="scss" scoped>
.uc-qaoa-page {
  width: 100%;
  min-height: calc(100vh - 60px);
  background: #f4f7fc;
}

.page-banner {
  background: #1664FF;
  padding: 60px 0 40px;

  .banner-title {
    font-size: 40px;
    font-weight: bold;
    color: #fff;
    margin: 0 0 10px;
  }

  .banner-desc {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.8);
    margin: 0;
  }
}

.section-card {
  background: #fff;
  border-radius: 8px;
  padding: 30px;
  margin: 20px 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.step-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1664FF;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;

  &--success {
    background: #00B42A;
  }
}

.section-title {
  font-size: 24px;
  font-weight: regular;
  color: #020814;
  margin: 0;
}

.section-hint {
  font-size: 14px;
  color: #939AAB;
  margin-left: auto;
}

.result-tag {
  margin-left: auto;
}

// Generator grid
.gen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.gen-card {
  background: #F4F7FC;
  border: 2px solid #DCE0EB;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: border-color 0.2s;
  position: relative;

  &:hover:not(.disabled) {
    border-color: #1664FF;
  }

  &.selected {
    border-color: #1664FF;
    background: #F3F7FF;
  }

  &.disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.gen-id {
  font-size: 30px;
  font-weight: bold;
  color: #1664FF;
  line-height: 1.2;
}

.gen-name {
  font-size: 14px;
  color: #41464F;
  margin-bottom: 10px;
}

.spec-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 4px;
}

.spec-label {
  color: #939AAB;
}

.spec-value {
  color: #41464F;
}

.spec-formula {
  font-size: 12px;
}

.spec-cost {
  color: #FF7D00;
  font-weight: bold;
}

.gen-check {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #00B42A;

  &::after {
    content: '';
    display: block;
    width: 6px;
    height: 10px;
    border: 2px solid #fff;
    border-top: none;
    border-left: none;
    transform: rotate(45deg) translate(-2px, -1px);
    margin: 3px auto 0;
  }
}

// Period config
.period-config {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.period-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.period-label {
  font-weight: bold;
  min-width: 70px;
  color: #1664FF;
  font-size: 16px;
}

.load-options {
  display: flex;
  gap: 8px;
  align-items: center;
}

.qubit-info {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 6px;
  background: #F3F7FF;
  border: 1px solid #DCE0EB;
  font-size: 14px;
  color: #41464F;
}

// Params
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.param-item {
  label {
    display: block;
    font-size: 16px;
    color: #41464F;
    margin-bottom: 8px;
  }
}

.param-desc {
  font-size: 12px;
  color: #939AAB;
  margin-top: 4px;
}

// Solve
.solve-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

// Result metrics
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: #F4F7FC;
  border: 1px solid #DCE0EB;
  border-radius: 8px;
  padding: 16px;
  text-align: center;

  &--highlight {
    border-color: #1664FF;
    background: #F3F7FF;
  }
}

.metric-label {
  font-size: 12px;
  color: #939AAB;
  margin-bottom: 6px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #020814;

  &--primary {
    color: #1664FF;
  }

  &--warning {
    color: #FF7D00;
  }

  &--good {
    color: #00B42A;
  }

  &--medium {
    color: #FF7D00;
  }

  &--poor {
    color: #FB4214;
  }
}

// Charts
.chart-block {
  margin-top: 30px;
}

.chart-title {
  font-size: 20px;
  color: #020814;
  margin: 0 0 12px;
  font-weight: regular;
}

.chart-container {
  width: 100%;
  height: 360px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #DCE0EB;
}

// Table
.table-block {
  margin-top: 30px;
}
</style>
