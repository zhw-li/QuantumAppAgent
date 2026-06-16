/**
 * UC-QAOA 机组组合优化平台 - 前端应用
 * 直接调用后端 API: http://localhost:8001/api
 */
const { createApp, ref, computed, nextTick, onBeforeUnmount } = Vue;

const API_BASE = 'http://localhost:8001/api';

const app = createApp({
    setup() {
        // ============ 数据 ============
        const generators = ref([
            { id: 'A', p_max: 300, a: 800, b: 12, c: 0.014 },
            { id: 'B', p_max: 420, a: 900, b: 13, c: 0.014 },
            { id: 'C', p_max: 550, a: 1100, b: 14, c: 0.016 },
            { id: 'D', p_max: 700, a: 1300, b: 16, c: 0.017 },
            { id: 'E', p_max: 850, a: 1500, b: 17, c: 0.018 },
            { id: 'F', p_max: 1000, a: 1700, b: 18, c: 0.019 },
        ]);

        const loadOptions = [400, 600, 700];
        const selectedGens = ref([]);
        const loads = ref([400, 600]);
        const qaoaLayers = ref(2);
        const restarts = ref(10);
        const solving = ref(false);
        const error = ref('');
        const result = ref(null);

        let chartInstances = [];

        // ============ 计算属性 ============
        const qubitCount = computed(() => selectedGens.value.length * loads.value.length);

        const canSolve = computed(() =>
            selectedGens.value.length >= 2 &&
            selectedGens.value.length <= 4 &&
            loads.value.length >= 1
        );

        const selectedGenDetails = computed(() =>
            generators.value.filter(g => selectedGens.value.includes(g.id))
        );

        const gapClass = computed(() => {
            if (!result.value || result.value.optimality_gap < 0) return '';
            if (result.value.optimality_gap <= 5) return 'metric-value--good';
            if (result.value.optimality_gap <= 15) return 'metric-value--medium';
            return 'metric-value--poor';
        });

        // ============ 方法 ============
        function fullCost(gen) {
            return gen.a + gen.b * gen.p_max + gen.c * gen.p_max * gen.p_max;
        }

        function toggleGen(id) {
            const idx = selectedGens.value.indexOf(id);
            if (idx >= 0) {
                selectedGens.value.splice(idx, 1);
            } else if (selectedGens.value.length < 4) {
                selectedGens.value.push(id);
            }
        }

        function addPeriod() {
            if (loads.value.length < 6) loads.value.push(400);
        }

        function removePeriod(idx) {
            if (loads.value.length > 1) loads.value.splice(idx, 1);
        }

        function formatCost(cost) {
            if (cost === null || cost === undefined) return 'N/A';
            return cost.toLocaleString('en-US', { maximumFractionDigits: 0 });
        }

        function getGenStatus(period, genId) {
            if (!result.value || !result.value.schedule) return false;
            const e = result.value.schedule.find(
                e => e.period === period && e.generator_id === genId
            );
            return e ? e.status === 1 : false;
        }

        function getGenPower(period, genId) {
            if (!result.value || !result.value.schedule) return 0;
            const e = result.value.schedule.find(
                e => e.period === period && e.generator_id === genId
            );
            return e ? e.power : 0;
        }

        function getTotalPower(period) {
            if (!result.value || !result.value.schedule) return 0;
            return result.value.schedule
                .filter(e => e.period === period && e.status === 1)
                .reduce((sum, e) => sum + e.power, 0);
        }

        // ============ 求解 ============
        async function solve() {
            solving.value = true;
            error.value = '';
            result.value = null;

            try {
                const resp = await fetch(`${API_BASE}/solve`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        generator_ids: selectedGens.value,
                        loads: loads.value,
                        qaoa_layers: qaoaLayers.value,
                        restarts: restarts.value,
                    }),
                });

                if (!resp.ok) {
                    const errData = await resp.json();
                    throw new Error(errData.detail || '求解失败');
                }

                result.value = await resp.json();

                await nextTick();
                setTimeout(() => {
                    disposeCharts();
                    renderCompareChart();
                    renderScheduleChart();
                    renderCostChart();
                }, 120);
            } catch (e) {
                error.value = e.message;
            } finally {
                solving.value = false;
            }
        }

        // ============ 图表 ============
        function disposeCharts() {
            chartInstances.forEach(c => c && c.dispose());
            chartInstances = [];
        }

        function getGenColor(index) {
            const colors = ['#1664FF', '#722ED1', '#00B42A', '#FF7D00', '#FB4214', '#00C7E7'];
            return colors[index % colors.length];
        }

        function renderScheduleChart() {
            const dom = document.getElementById('schedule-chart');
            if (!dom || !result.value) return;
            const chart = echarts.init(dom);
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

            const genNames = genIds.map(id => {
                const g = generators.value.find(x => x.id === id);
                return '机组' + id + ' (' + g.p_max + 'MW)';
            });

            chart.setOption({
                tooltip: {
                    formatter(params) {
                        const t = params.value[0] + 1;
                        const gi = params.value[1];
                        const isOn = params.value[2] === 1;
                        const entry = schedule.find(e => e.period === t && e.generator_id === genIds[gi]);
                        let tip = 'Hour ' + t + ' - ' + genNames[gi] + '<br/>状态: ' + (isOn ? '开机' : '关机');
                        if (isOn && entry) {
                            tip += '<br/>出力: ' + entry.power.toFixed(0) + ' MW<br/>成本: ' + formatCost(entry.cost) + ' $';
                        }
                        return tip;
                    },
                },
                grid: { top: 20, right: 60, bottom: 40, left: 130 },
                xAxis: {
                    type: 'category',
                    data: Array.from({ length: nPeriods }, (_, i) => 'Hour ' + (i + 1)),
                },
                yAxis: {
                    type: 'category',
                    data: genNames,
                    inverse: true,
                },
                visualMap: {
                    min: 0, max: 1, show: false,
                    inRange: { color: ['#DCE0EB', '#1664FF'] },
                },
                series: [{
                    type: 'heatmap',
                    data: heatData,
                    label: {
                        show: true,
                        formatter(params) {
                            const t = params.value[0] + 1;
                            const gi = params.value[1];
                            const entry = schedule.find(e => e.period === t && e.generator_id === genIds[gi]);
                            if (entry && entry.status === 1) return entry.power.toFixed(0) + 'MW';
                            return 'OFF';
                        },
                        color: '#fff', fontSize: 11,
                    },
                    itemStyle: { borderColor: '#F4F7FC', borderWidth: 3, borderRadius: 4 },
                }],
            });

            const onResize = () => chart.resize();
            window.addEventListener('resize', onResize);
            onBeforeUnmount(() => window.removeEventListener('resize', onResize));
        }

        function renderCostChart() {
            const dom = document.getElementById('cost-chart');
            if (!dom || !result.value) return;
            const chart = echarts.init(dom);
            chartInstances.push(chart);

            const schedule = result.value.schedule;
            const genIds = selectedGens.value;
            const nPeriods = loads.value.length;

            const series = genIds.map((gid, gi) => {
                const data = [];
                for (let t = 1; t <= nPeriods; t++) {
                    const entry = schedule.find(e => e.period === t && e.generator_id === gid);
                    data.push(entry && entry.status === 1 ? Math.round(entry.cost) : 0);
                }
                return {
                    name: '机组' + gid,
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
                        let html = '<b>' + params[0].axisValue + '</b><br/>';
                        let total = 0;
                        params.forEach(p => {
                            if (p.value > 0) {
                                html += p.marker + ' ' + p.seriesName + ': ' + formatCost(p.value) + ' $<br/>';
                                total += p.value;
                            }
                        });
                        html += '<b>合计: ' + formatCost(total) + ' $</b>';
                        return html;
                    },
                },
                legend: {
                    data: genIds.map(id => '机组' + id),
                },
                grid: { top: 50, right: 30, bottom: 30, left: 70 },
                xAxis: {
                    type: 'category',
                    data: Array.from({ length: nPeriods }, (_, i) => 'Hour ' + (i + 1)),
                },
                yAxis: {
                    type: 'value',
                    name: '成本 ($)',
                    splitLine: { lineStyle: { color: '#DCE0EB' } },
                },
                series,
            });

            const onResize = () => chart.resize();
            window.addEventListener('resize', onResize);
            onBeforeUnmount(() => window.removeEventListener('resize', onResize));
        }

        function renderCompareChart() {
            const dom = document.getElementById('compare-chart');
            if (!dom || !result.value) return;
            const classicCost = result.value.classical_optimal_cost;
            if (classicCost <= 0) return;

            const chart = echarts.init(dom);
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
                    data: ['QAOA 量子算法', '经典最优解'],
                },
                yAxis: {
                    type: 'value',
                    name: '总成本 ($)',
                    splitLine: { lineStyle: { color: '#DCE0EB' } },
                    min(value) { return Math.floor(value.min * 0.95); },
                },
                series: [{
                    type: 'bar',
                    data: [
                        { value: qaoaCost, itemStyle: { color: '#1664FF', borderRadius: [6, 6, 0, 0] } },
                        { value: classicCost, itemStyle: { color: '#FF7D00', borderRadius: [6, 6, 0, 0] } },
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
                }],
                graphic: gap >= 0 ? [{
                    type: 'text',
                    left: 'center',
                    top: 5,
                    style: {
                        text: '最优性差距: ' + gap.toFixed(2) + '%',
                        fill: gap <= 5 ? '#00B42A' : gap <= 15 ? '#FF7D00' : '#FB4214',
                        fontSize: 14,
                        fontWeight: 'bold',
                        fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
                    },
                }] : [],
            });

            const onResize = () => chart.resize();
            window.addEventListener('resize', onResize);
            onBeforeUnmount(() => window.removeEventListener('resize', onResize));
        }

        onBeforeUnmount(() => {
            disposeCharts();
        });

        return {
            generators, loadOptions, selectedGens, loads,
            qaoaLayers, restarts, solving, error, result,
            qubitCount, canSolve, selectedGenDetails, gapClass,
            fullCost, toggleGen, addPeriod, removePeriod, formatCost,
            getGenStatus, getGenPower, getTotalPower, solve,
        };
    }
});

app.mount('#app');
