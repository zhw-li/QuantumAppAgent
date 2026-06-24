<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { getInfo, solveVQE, getEnergyCurve } from '@/api/vqeH2/index.js';
import * as echarts from 'echarts';

const { t } = useI18n();

const solving = ref(false);
const error = ref('');
const results = ref([]);
const totalTime = ref(0);
const curveData = ref(null);

const availableBondLengths = [0.40, 0.50, 0.60, 0.70, 0.74, 0.80, 0.90, 1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.50, 3.00];
const bondLengths = ref([0.74]);
const maxIterations = ref(3);

const canSolve = computed(() => bondLengths.value.length >= 1);

function toggleBond(bl) {
  const idx = bondLengths.value.indexOf(bl);
  if (idx >= 0) {
    bondLengths.value.splice(idx, 1);
  } else {
    bondLengths.value.push(bl);
  }
}

function formatEnergy(e) {
  if (e === null || e === undefined) return 'N/A';
  return e.toFixed(6);
}

let chartInstances = [];

function disposeCharts() {
  chartInstances.forEach(c => c && c.dispose());
  chartInstances = [];
}

async function solve() {
  solving.value = true;
  error.value = '';
  results.value = [];
  curveData.value = null;

  try {
    const res = await solveVQE({
      bond_lengths: bondLengths.value,
      max_iterations: maxIterations.value,
    });
    if (res.code === 200) {
      results.value = res.data.results;
      totalTime.value = res.data.total_time;
    } else {
      throw new Error(res.message || t('vqeH2.message.solveFailed'));
    }

    try {
      const cRes = await getEnergyCurve();
      if (cRes.code === 200) {
        curveData.value = cRes.data;
      }
    } catch (e) { /* ignore */ }

    await nextTick();
    setTimeout(() => {
      disposeCharts();
      renderAllCharts();
    }, 150);
  } catch (e) {
    error.value = e.message;
    ElMessage.error(error.value);
  } finally {
    solving.value = false;
  }
}

function renderAllCharts() {
  results.value.forEach((r, ri) => {
    renderIterChart(r, ri);
    renderConvChart(r, ri);
  });
  if (curveData.value) {
    renderPECChart();
  }
}

function renderIterChart(r, ri) {
  const dom = document.getElementById('vqe-iter-' + ri);
  if (!dom) return;
  const chart = echarts.init(dom);
  chartInstances.push(chart);

  const iters = r.vqe_iterations;
  const categories = iters.map(it => t('vqeH2.result.iterN', { n: it.iteration }) + '\n(p=' + it.layers + ')');

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: [t('vqeH2.result.vqeEnergy'), t('vqeH2.result.classicalExact')] },
    grid: { top: 40, right: 30, bottom: 50, left: 90 },
    xAxis: { type: 'category', data: categories },
    yAxis: {
      type: 'value',
      name: t('vqeH2.result.energyUnit'),
      splitLine: { lineStyle: { color: '#DCE0EB' } },
    },
    series: [
      {
        name: t('vqeH2.result.vqeEnergy'),
        type: 'bar',
        data: iters.map(it => ({ value: it.vqe_total, itemStyle: { color: '#1664FF', borderRadius: [4, 4, 0, 0] } })),
        barWidth: '30%',
        label: { show: true, position: 'top', formatter: p => p.value.toFixed(4), color: '#41464F', fontSize: 11 },
      },
      {
        name: t('vqeH2.result.classicalExact'),
        type: 'line',
        data: iters.map(() => r.classical_total),
        lineStyle: { color: '#FF7D00', width: 2, type: 'dashed' },
        itemStyle: { color: '#FF7D00' },
        symbol: 'diamond',
        symbolSize: 10,
      },
    ],
  });
  window.addEventListener('resize', () => chart.resize());
}

function renderConvChart(r, ri) {
  const dom = document.getElementById('vqe-conv-' + ri);
  if (!dom) return;
  const chart = echarts.init(dom);
  chartInstances.push(chart);

  const iters = r.vqe_iterations;
  const colors = ['#1664FF', '#722ED1', '#00B42A', '#FF7D00', '#FB4214'];
  const series = iters.map((it, i) => ({
    name: t('vqeH2.result.iterN', { n: it.iteration }) + ' (p=' + it.layers + ')',
    type: 'line',
    data: it.convergence,
    lineStyle: { width: 2, color: colors[i % colors.length] },
    itemStyle: { color: colors[i % colors.length] },
    showSymbol: false,
    smooth: true,
  }));

  series.push({
    name: t('vqeH2.result.classicalExact'),
    type: 'line',
    data: null,
    markLine: {
      silent: true,
      lineStyle: { color: '#FF7D00', type: 'dashed', width: 2 },
      data: [{ yAxis: r.classical_total }],
      label: { formatter: t('vqeH2.result.classicalExact') + ': ' + r.classical_total.toFixed(6), color: '#FF7D00' },
    },
  });

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: series.map(s => s.name) },
    grid: { top: 40, right: 30, bottom: 30, left: 90 },
    xAxis: { type: 'value', show: false },
    yAxis: { type: 'value', name: t('vqeH2.result.energyUnit'), splitLine: { lineStyle: { color: '#DCE0EB' } } },
    series,
  });
  window.addEventListener('resize', () => chart.resize());
}

function renderPECChart() {
  const dom = document.getElementById('vqe-pec');
  if (!dom || !curveData.value) return;
  const chart = echarts.init(dom);
  chartInstances.push(chart);
  const d = curveData.value;

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: [t('vqeH2.result.vqeLabel'), t('vqeH2.result.classicalLabel')] },
    grid: { top: 40, right: 30, bottom: 40, left: 90 },
    xAxis: { type: 'category', data: d.bond_lengths.map(v => v.toFixed(2)), name: t('vqeH2.config.bondLengthUnit') },
    yAxis: { type: 'value', name: t('vqeH2.result.energyUnit'), splitLine: { lineStyle: { color: '#DCE0EB' } } },
    series: [
      {
        name: t('vqeH2.result.vqeLabel'),
        type: 'line',
        data: d.vqe_energies,
        lineStyle: { width: 3, color: '#1664FF' },
        itemStyle: { color: '#1664FF' },
        symbol: 'circle',
        symbolSize: 8,
        smooth: true,
      },
      {
        name: t('vqeH2.result.classicalLabel'),
        type: 'line',
        data: d.classical_energies,
        lineStyle: { width: 2, color: '#FF7D00', type: 'dashed' },
        itemStyle: { color: '#FF7D00' },
        symbol: 'diamond',
        symbolSize: 8,
        smooth: true,
      },
    ],
  });
  window.addEventListener('resize', () => chart.resize());
}

onBeforeUnmount(() => disposeCharts());
</script>

<template>
  <main class="vqe-h2-page">
    <section class="page-banner">
      <div class="wrapper">
        <h1 class="banner-title">{{ $t('vqeH2.banner.title') }}</h1>
        <p class="banner-desc">{{ $t('vqeH2.banner.desc') }}</p>
      </div>
    </section>

    <div class="wrapper">
      <!-- Config -->
      <section class="section-card">
        <div class="section-header">
          <span class="step-badge">1</span>
          <h2 class="section-title">{{ $t('vqeH2.config.title') }}</h2>
          <span class="section-hint">{{ $t('vqeH2.config.hint') }}</span>
        </div>

        <div class="config-grid">
          <div class="config-block">
            <h3 class="config-label">{{ $t('vqeH2.config.selectBond') }}</h3>
            <div class="bond-grid">
              <div v-for="bl in availableBondLengths" :key="bl"
                   class="bond-card" :class="{ selected: bondLengths.includes(bl) }"
                   @click="toggleBond(bl)">
                <div class="bond-value">{{ bl }}</div>
                <div class="bond-unit">Å</div>
              </div>
            </div>
          </div>

          <div class="config-block">
            <h3 class="config-label">{{ $t('vqeH2.config.optParams') }}</h3>
            <div class="param-row">
              <label>{{ $t('vqeH2.config.maxIter') }}</label>
              <el-slider v-model="maxIterations" :min="1" :max="5" :step="1" show-input />
              <p class="param-desc">{{ $t('vqeH2.config.maxIterDesc') }}</p>
            </div>
          </div>
        </div>

        <div class="molecule-info">
          <div class="info-item"><span class="info-label">{{ $t('vqeH2.info.molecule') }}</span><span class="info-value">H2</span></div>
          <div class="info-item"><span class="info-label">{{ $t('vqeH2.info.basis') }}</span><span class="info-value">STO-3G</span></div>
          <div class="info-item"><span class="info-label">{{ $t('vqeH2.info.mapping') }}</span><span class="info-value">Parity + 2-qubit reduction</span></div>
          <div class="info-item"><span class="info-label">{{ $t('vqeH2.info.qubits') }}</span><span class="info-value">2</span></div>
          <div class="info-item"><span class="info-label">{{ $t('vqeH2.info.accuracy') }}</span><span class="info-value">1.6 mHa</span></div>
        </div>
      </section>

      <!-- Solve -->
      <div class="solve-section">
        <el-button type="primary" size="large" :loading="solving" :disabled="!canSolve" @click="solve">
          {{ solving ? $t('vqeH2.solve.solving') : $t('vqeH2.solve.start') }}
        </el-button>
      </div>

      <el-alert v-if="error" :title="error" type="error" show-close @close="error = ''" style="margin-bottom: 20px;" />

      <!-- Results -->
      <section v-if="results.length" class="section-card">
        <div class="section-header">
          <span class="step-badge step-badge--success">OK</span>
          <h2 class="section-title">{{ $t('vqeH2.result.title') }}</h2>
          <span class="result-time">{{ $t('vqeH2.result.totalTime') }}: {{ totalTime.toFixed(1) }}s</span>
        </div>

        <div v-for="(r, ri) in results" :key="ri" class="bond-result">
          <h3 class="bond-result-title">R = {{ r.bond_length }} Å</h3>

          <div class="metrics-row">
            <div class="metric-card metric-card--hl">
              <div class="metric-label">{{ $t('vqeH2.result.vqeEnergy') }}</div>
              <div class="metric-value mv-primary">{{ formatEnergy(r.final_vqe_total) }} Ha</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">{{ $t('vqeH2.result.classicalEnergy') }}</div>
              <div class="metric-value mv-warning">{{ formatEnergy(r.classical_total) }} Ha</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">{{ $t('vqeH2.result.gap') }}</div>
              <div class="metric-value" :class="r.final_gap_mhartree < 1.6 ? 'mv-good' : 'mv-poor'">
                {{ r.final_gap_mhartree.toFixed(2) }} mHa
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-label">{{ $t('vqeH2.result.status') }}</div>
              <div class="metric-value">
                <el-tag :type="r.optimized ? 'success' : 'danger'" size="small">
                  {{ r.optimized ? $t('vqeH2.result.reached') : $t('vqeH2.result.notReached') }}
                </el-tag>
              </div>
            </div>
          </div>

          <div class="chart-block">
            <h4 class="chart-sub">{{ $t('vqeH2.result.iterProcess') }}</h4>
            <div :id="'vqe-iter-' + ri" class="chart-box"></div>
          </div>

          <div class="chart-block">
            <h4 class="chart-sub">{{ $t('vqeH2.result.convergence') }}</h4>
            <div :id="'vqe-conv-' + ri" class="chart-box"></div>
          </div>

          <div class="table-block">
            <h4 class="chart-sub">{{ $t('vqeH2.result.iterDetail') }}</h4>
            <el-table :data="r.vqe_iterations" border stripe>
              <el-table-column prop="iteration" :label="$t('vqeH2.result.iteration')" width="70" />
              <el-table-column prop="layers" :label="$t('vqeH2.result.layers')" width="80" />
              <el-table-column prop="restarts" :label="$t('vqeH2.result.restarts')" width="90" />
              <el-table-column prop="n_params" :label="$t('vqeH2.result.nParams')" width="80" />
              <el-table-column :label="$t('vqeH2.result.vqeEnergy')" width="140">
                <template #default="{ row }">{{ row.vqe_total.toFixed(6) }}</template>
              </el-table-column>
              <el-table-column :label="$t('vqeH2.result.gap')" width="100">
                <template #default="{ row }">
                  <span :class="row.gap_mhartree < 1.6 ? 'td-good' : 'td-poor'">{{ row.gap_mhartree.toFixed(2) }} mHa</span>
                </template>
              </el-table-column>
              <el-table-column :label="$t('vqeH2.result.time')" width="80">
                <template #default="{ row }">{{ row.solve_time.toFixed(1) }}s</template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <div v-if="curveData" class="chart-block">
          <h3 class="bond-result-title">{{ $t('vqeH2.result.pecTitle') }}</h3>
          <div id="vqe-pec" class="chart-box"></div>
        </div>
      </section>
    </div>
  </main>
</template>

<style lang="scss" scoped>
.vqe-h2-page { width: 100%; min-height: calc(100vh - 60px); background: #f4f7fc; }
.page-banner { background: #1664FF; padding: 60px 0 40px; }
.banner-title { font-size: 40px; font-weight: bold; color: #fff; margin: 0 0 10px; }
.banner-desc { font-size: 18px; color: rgba(255,255,255,0.8); margin: 0; }

.section-card { background: #fff; border-radius: 8px; padding: 30px; margin: 20px 0; border: 1px solid #DCE0EB; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.step-badge { width: 28px; height: 28px; border-radius: 50%; background: #1664FF; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold; &--success { background: #00B42A; } }
.section-title { font-size: 24px; font-weight: regular; color: #020814; margin: 0; }
.section-hint { font-size: 14px; color: #939AAB; margin-left: auto; }

.config-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
.config-block { padding: 20px; background: #F4F7FC; border-radius: 8px; border: 1px solid #DCE0EB; }
.config-label { font-size: 18px; font-weight: bold; color: #41464F; margin: 0 0 16px; }

.bond-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 10px; }
.bond-card { background: #fff; border: 2px solid #DCE0EB; border-radius: 8px; padding: 12px 8px; cursor: pointer; text-align: center; transition: border-color 0.2s; &:hover { border-color: #1664FF; } &.selected { border-color: #1664FF; background: #F3F7FF; } }
.bond-value { font-size: 22px; font-weight: bold; color: #1664FF; line-height: 1.2; }
.bond-unit { font-size: 12px; color: #939AAB; }

.param-desc { font-size: 12px; color: #939AAB; margin-top: 4px; }

.molecule-info { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px; padding: 16px; background: #F3F7FF; border-radius: 6px; border: 1px solid #DCE0EB; }
.info-item { display: flex; flex-direction: column; gap: 4px; min-width: 100px; }
.info-label { font-size: 12px; color: #939AAB; }
.info-value { font-size: 14px; font-weight: bold; color: #41464F; }

.solve-section { display: flex; justify-content: center; padding: 24px 0; }

.bond-result { margin-bottom: 40px; padding-bottom: 40px; border-bottom: 1px solid #DCE0EB; &:last-of-type { border-bottom: none; } }
.bond-result-title { font-size: 20px; font-weight: bold; color: #1664FF; margin: 0 0 16px; }

.metrics-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
.metric-card { background: #F4F7FC; border: 1px solid #DCE0EB; border-radius: 8px; padding: 16px; text-align: center; &--hl { border-color: #1664FF; background: #F3F7FF; } }
.metric-label { font-size: 13px; color: #939AAB; margin-bottom: 6px; }
.metric-value { font-size: 22px; font-weight: bold; color: #020814; }
.mv-primary { color: #1664FF; } .mv-warning { color: #FF7D00; } .mv-good { color: #00B42A; } .mv-poor { color: #FB4214; }

.chart-block { margin-top: 30px; }
.chart-sub { font-size: 16px; font-weight: bold; color: #41464F; margin: 0 0 12px; }
.chart-box { width: 100%; height: 380px; background: #fff; border-radius: 8px; border: 1px solid #DCE0EB; }
.table-block { margin-top: 30px; }
.td-good { color: #00B42A; font-weight: bold; } .td-poor { color: #FB4214; font-weight: bold; }
</style>
