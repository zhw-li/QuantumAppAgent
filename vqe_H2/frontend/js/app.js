/**
 * VQE-H2 分子基态能量量子计算平台 - 前端应用
 * 直接调用后端 API: http://localhost:8002/api
 */
const { createApp, ref, computed, nextTick, onBeforeUnmount } = Vue;

const API_BASE = 'http://localhost:8002/api';

const app = createApp({
    setup() {
        // ============ 数据 ============
        const availableBondLengths = [0.50, 0.60, 0.70, 0.74, 0.75, 0.80, 0.90, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00];
        const bondLengths = ref([0.74]);
        const maxIterations = ref(3);
        const solving = ref(false);
        const error = ref('');
        const results = ref([]);
        const totalTime = ref(0);
        const curveData = ref(null);

        let chartInstances = [];

        // ============ 计算属性 ============
        const canSolve = computed(() => bondLengths.value.length >= 1);

        // ============ 方法 ============
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

        // ============ 求解 ============
        async function solve() {
            solving.value = true;
            error.value = '';
            results.value = [];
            curveData.value = null;

            try {
                const resp = await fetch(`${API_BASE}/solve`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        bond_lengths: bondLengths.value,
                        max_iterations: maxIterations.value,
                    }),
                });

                if (!resp.ok) {
                    const errData = await resp.json();
                    throw new Error(errData.detail || '求解失败');
                }

                const data = await resp.json();
                results.value = data.results;
                totalTime.value = data.total_time;

                // 获取势能曲线
                try {
                    const curveResp = await fetch(`${API_BASE}/energy_curve`);
                    if (curveResp.ok) {
                        curveData.value = await curveResp.json();
                    }
                } catch (e) {
                    console.warn('获取势能曲线失败:', e);
                }

                await nextTick();
                setTimeout(() => {
                    disposeCharts();
                    renderAllCharts();
                }, 150);
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
            const dom = document.getElementById('iter-chart-' + ri);
            if (!dom) return;
            const chart = echarts.init(dom);
            chartInstances.push(chart);

            const iters = r.vqe_iterations;
            const categories = iters.map(it => '第' + it.iteration + '轮\n(p=' + it.layers + ')');
            const vqeData = iters.map(it => it.vqe_total);
            const classicalData = iters.map(it => it.classical_total);

            chart.setOption({
                tooltip: { trigger: 'axis' },
                legend: { data: ['VQE能量', '经典精确'] },
                grid: { top: 40, right: 30, bottom: 50, left: 90 },
                xAxis: { type: 'category', data: categories },
                yAxis: {
                    type: 'value',
                    name: '能量 (Hartree)',
                    splitLine: { lineStyle: { color: '#DCE0EB' } },
                    min(value) { return Math.floor(value.min * 1000) / 1000; },
                },
                series: [
                    {
                        name: 'VQE能量',
                        type: 'bar',
                        data: vqeData.map(v => ({
                            value: v,
                            itemStyle: { color: '#1664FF', borderRadius: [4, 4, 0, 0] },
                        })),
                        barWidth: '30%',
                        label: {
                            show: true, position: 'top',
                            formatter: p => p.value.toFixed(4),
                            color: '#41464F', fontSize: 11,
                        },
                    },
                    {
                        name: '经典精确',
                        type: 'line',
                        data: classicalData,
                        lineStyle: { color: '#FF7D00', width: 2, type: 'dashed' },
                        itemStyle: { color: '#FF7D00' },
                        symbol: 'diamond',
                        symbolSize: 10,
                    },
                ],
            });

            const onResize = () => chart.resize();
            window.addEventListener('resize', onResize);
            onBeforeUnmount(() => window.removeEventListener('resize', onResize));
        }

        function renderConvChart(r, ri) {
            const dom = document.getElementById('conv-chart-' + ri);
            if (!dom) return;
            const chart = echarts.init(dom);
            chartInstances.push(chart);

            const iters = r.vqe_iterations;
            const classicalTotal = r.classical_total;
            const series = [];
            const colors = ['#1664FF', '#722ED1', '#00B42A', '#FF7D00', '#FB4214'];

            iters.forEach((it, i) => {
                series.push({
                    name: '第' + it.iteration + '轮 (p=' + it.layers + ')',
                    type: 'line',
                    data: it.convergence,
                    lineStyle: { width: 2, color: colors[i % colors.length] },
                    itemStyle: { color: colors[i % colors.length] },
                    showSymbol: false,
                    smooth: true,
                });
            });

            // 经典精确参考线
            series.push({
                name: '经典精确',
                type: 'line',
                data: null,
                markLine: {
                    silent: true,
                    lineStyle: { color: '#FF7D00', type: 'dashed', width: 2 },
                    data: [{ yAxis: classicalTotal }],
                    label: {
                        formatter: '经典精确: ' + classicalTotal.toFixed(6),
                        color: '#FF7D00',
                        fontSize: 12,
                    },
                },
            });

            chart.setOption({
                tooltip: { trigger: 'axis' },
                legend: { data: series.map(s => s.name) },
                grid: { top: 40, right: 30, bottom: 30, left: 90 },
                xAxis: { type: 'category', data: undefined, show: false },
                yAxis: {
                    type: 'value',
                    name: '能量 (Hartree)',
                    splitLine: { lineStyle: { color: '#DCE0EB' } },
                },
                series,
            });

            const onResize = () => chart.resize();
            window.addEventListener('resize', onResize);
            onBeforeUnmount(() => window.removeEventListener('resize', onResize));
        }

        function renderPECChart() {
            const dom = document.getElementById('pec-chart');
            if (!dom || !curveData.value) return;
            const chart = echarts.init(dom);
            chartInstances.push(chart);

            const d = curveData.value;

            chart.setOption({
                tooltip: {
                    trigger: 'axis',
                    formatter(params) {
                        let html = 'R = ' + params[0].axisValue + ' Å<br/>';
                        params.forEach(p => {
                            html += p.marker + ' ' + p.seriesName + ': ' + p.value.toFixed(6) + ' Ha<br/>';
                        });
                        return html;
                    },
                },
                legend: { data: ['VQE量子算法', '经典精确对角化'] },
                grid: { top: 40, right: 30, bottom: 40, left: 90 },
                xAxis: {
                    type: 'category',
                    data: d.bond_lengths.map(v => v.toFixed(2)),
                    name: '键长 (Å)',
                },
                yAxis: {
                    type: 'value',
                    name: '能量 (Hartree)',
                    splitLine: { lineStyle: { color: '#DCE0EB' } },
                },
                series: [
                    {
                        name: 'VQE量子算法',
                        type: 'line',
                        data: d.vqe_energies,
                        lineStyle: { width: 3, color: '#1664FF' },
                        itemStyle: { color: '#1664FF' },
                        symbol: 'circle',
                        symbolSize: 8,
                        smooth: true,
                    },
                    {
                        name: '经典精确对角化',
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

            const onResize = () => chart.resize();
            window.addEventListener('resize', onResize);
            onBeforeUnmount(() => window.removeEventListener('resize', onResize));
        }

        onBeforeUnmount(() => {
            disposeCharts();
        });

        return {
            availableBondLengths, bondLengths, maxIterations,
            solving, error, results, totalTime, curveData,
            canSolve,
            toggleBond, formatEnergy, solve,
        };
    }
});

app.mount('#app');
