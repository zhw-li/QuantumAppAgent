/* ============================================
   QLSTM 时间序列预测系统 — Vue 3 应用逻辑
   ============================================ */

const { createApp, ref, reactive, computed, watch, onMounted, nextTick } = Vue;

const API_BASE = 'http://localhost:8001/api';

const app = createApp({
  setup() {
    // ---- 响应式状态 ----
    const activeTab = ref('comparison');
    const loading = reactive({
      comparison: false,
      predictions: false,
      training: false,
      rawData: false,
      future: false,
    });

    const comparison = ref(null);
    const predictions = ref(null);
    const trainingCurves = ref(null);
    const rawData = ref(null);
    const futurePredictions = ref(null);
    const predictDays = ref(7);
    const backendOnline = ref(false);
    const lastUpdate = ref('');

    // 图表实例引用
    let predictionChart = null;
    let trainingChart = null;
    let futureChart = null;
    let rawDataChart = null;

    // ---- 工具方法 ----
    function formatNumber(val, digits = 4) {
      if (val == null || isNaN(val)) return '—';
      return Number(val).toFixed(digits);
    }

    function formatPercent(val, digits = 2) {
      if (val == null || isNaN(val)) return '—';
      const num = Number(val);
      return (num >= 0 ? '+' : '') + num.toFixed(digits) + '%';
    }

    function getImprovementClass(val) {
      return Number(val) >= 0 ? 'improvement-tag--positive' : 'improvement-tag--negative';
    }

    function updateTimestamp() {
      const now = new Date();
      lastUpdate.value = now.toLocaleString('zh-CN', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      });
    }

    // ---- 计算属性 ----
    const overallImprovement = computed(() => {
      if (!comparison.value) return null;
      const cRMSE = comparison.value.classic.metrics.rmse;
      const qRMSE = comparison.value.quantum.metrics.rmse;
      return ((cRMSE - qRMSE) / cRMSE * 100);
    });

    const comparisonTableData = computed(() => {
      if (!comparison.value) return [];
      const cM = comparison.value.classic.metrics;
      const qM = comparison.value.quantum.metrics;
      const rows = [
        { metric: 'RMSE', label: '均方根误差', classic: cM.rmse, quantum: qM.rmse },
        { metric: 'MAE', label: '平均绝对误差', classic: cM.mae, quantum: qM.mae },
        { metric: 'MAPE', label: '平均绝对百分比误差 (%)', classic: cM.mape, quantum: qM.mape },
        { metric: 'MSE', label: '均方误差', classic: cM.mse, quantum: qM.mse },
      ];
      return rows.map(r => ({
        ...r,
        improvement: ((r.classic - r.quantum) / Math.abs(r.classic) * 100),
      }));
    });

    // ---- API 请求 ----
    async function fetchComparison() {
      loading.comparison = true;
      try {
        const { data } = await axios.get(`${API_BASE}/comparison`);
        comparison.value = {
          classic: { metrics: data.classic_metrics },
          quantum: { metrics: data.quantum_metrics },
          improvement_pct: data.improvement_pct,
          train_time_classic: data.train_time_classic,
          train_time_quantum: data.train_time_quantum,
          quantum_iterations: data.quantum_iterations,
          best_iteration: data.best_iteration
        };
        backendOnline.value = true;
        updateTimestamp();
      } catch (err) {
        console.error('获取对比数据失败:', err);
        backendOnline.value = false;
        ElMessage.error('获取模型对比数据失败，请确认后端服务已启动');
      } finally {
        loading.comparison = false;
      }
    }

    async function fetchPredictions() {
      loading.predictions = true;
      try {
        const { data } = await axios.get(`${API_BASE}/predictions`);
        predictions.value = data;
        backendOnline.value = true;
        updateTimestamp();
      } catch (err) {
        console.error('获取预测数据失败:', err);
        backendOnline.value = false;
        ElMessage.error('获取预测数据失败');
      } finally {
        loading.predictions = false;
      }
    }

    async function fetchTrainingCurves() {
      loading.training = true;
      try {
        const { data } = await axios.get(`${API_BASE}/training-curves`);
        // API 返回 {classic: [{epoch, train_loss, val_loss}], quantum: [...]}
        trainingCurves.value = {
          classic: { train_losses: data.classic.map(e => e.train_loss), val_losses: data.classic.map(e => e.val_loss) },
          quantum: { train_losses: data.quantum.map(e => e.train_loss), val_losses: data.quantum.map(e => e.val_loss) }
        };
        backendOnline.value = true;
        updateTimestamp();
      } catch (err) {
        console.error('获取训练曲线失败:', err);
        backendOnline.value = false;
        ElMessage.error('获取训练曲线数据失败');
      } finally {
        loading.training = false;
      }
    }

    async function fetchRawData() {
      loading.rawData = true;
      try {
        const { data } = await axios.get(`${API_BASE}/raw-data?days=365`);
        rawData.value = data;
        backendOnline.value = true;
        updateTimestamp();
      } catch (err) {
        console.error('获取原始数据失败:', err);
        backendOnline.value = false;
        ElMessage.error('获取原始数据失败');
      } finally {
        loading.rawData = false;
      }
    }

    async function predictFuture() {
      if (predictDays.value < 1 || predictDays.value > 30) {
        ElMessage.warning('预测天数需在 1-30 之间');
        return;
      }
      loading.future = true;
      try {
        const { data } = await axios.post(`${API_BASE}/predict`, {
          n_days: predictDays.value,
        });
        futurePredictions.value = {
          dates: data.dates,
          classic: data.predictions_classic,
          quantum: data.predictions_quantum,
          confidence: data.confidence
        };
        backendOnline.value = true;
        updateTimestamp();
        ElMessage.success(`未来 ${predictDays.value} 天预测完成`);
        await nextTick();
        initFutureChart();
      } catch (err) {
        console.error('未来预测失败:', err);
        ElMessage.error('未来预测失败，请确认后端服务已启动');
      } finally {
        loading.future = false;
      }
    }

    // ---- ECharts 初始化 ----
    const chartTheme = {
      color: ['#8A8F98', '#1664FF', '#00D4FF'],
      textStyle: { fontFamily: '-apple-system, BlinkMacSystemFont, PingFang SC, Microsoft YaHei, sans-serif' },
    };

    function disposeChart(chartRef) {
      if (chartRef) {
        chartRef.dispose();
        return null;
      }
      return chartRef;
    }

    function initPredictionChart() {
      if (!predictions.value) return;
      const dom = document.getElementById('prediction-chart');
      if (!dom) return;

      predictionChart = disposeChart(predictionChart);
      predictionChart = echarts.init(dom);

      const d = predictions.value;
      const dates = d.dates || [];
      const actual = d.actuals || [];
      const classic = d.classic_predictions || [];
      const quantum = d.quantum_predictions || [];

      const option = {
        backgroundColor: '#fff',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255,255,255,0.96)',
          borderColor: '#EBEEF5',
          borderWidth: 1,
          textStyle: { color: '#020814', fontSize: 13 },
          formatter: function(params) {
            let html = `<div style="font-weight:600;margin-bottom:6px">${params[0].axisValue}</div>`;
            params.forEach(p => {
              html += `<div style="display:flex;align-items:center;gap:6px;margin:3px 0">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${p.color}"></span>
                <span>${p.seriesName}:</span>
                <span style="font-weight:600">$${Number(p.value).toFixed(2)}</span>
              </div>`;
            });
            return html;
          }
        },
        legend: {
          top: 16,
          textStyle: { color: '#41464F', fontSize: 13 },
          itemWidth: 24,
          itemHeight: 3,
          itemGap: 24,
        },
        grid: { top: 64, right: 32, bottom: 48, left: 72 },
        xAxis: {
          type: 'category',
          data: dates,
          axisLine: { lineStyle: { color: '#E4E7ED' } },
          axisTick: { show: false },
          axisLabel: {
            color: '#8A8F98',
            fontSize: 11,
            formatter: function(val) {
              if (!val) return '';
              return val.length > 10 ? val.substring(0, 10) : val;
            }
          },
        },
        yAxis: {
          type: 'value',
          name: '价格 ($)',
          nameTextStyle: { color: '#8A8F98', fontSize: 12 },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#F4F5F7', type: 'dashed' } },
          axisLabel: { color: '#8A8F98', fontSize: 11 },
        },
        series: [
          {
            name: '实际值',
            type: 'line',
            data: actual,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2.5, color: '#8A8F98' },
            itemStyle: { color: '#8A8F98' },
            z: 10,
          },
          {
            name: '经典 LSTM',
            type: 'line',
            data: classic,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2, type: 'dashed', color: '#1664FF' },
            itemStyle: { color: '#1664FF' },
            z: 20,
          },
          {
            name: 'QLSTM',
            type: 'line',
            data: quantum,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2.5, color: '#00D4FF' },
            itemStyle: { color: '#00D4FF' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(0, 212, 255, 0.12)' },
                { offset: 1, color: 'rgba(0, 212, 255, 0.01)' },
              ]),
            },
            z: 30,
          },
        ],
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100,
          },
        ],
      };

      predictionChart.setOption(option);
    }

    function initTrainingChart() {
      if (!trainingCurves.value) return;
      const dom = document.getElementById('training-chart');
      if (!dom) return;

      trainingChart = disposeChart(trainingChart);
      trainingChart = echarts.init(dom);

      const d = trainingCurves.value;
      const cTrain = (d.classic && d.classic.train_losses) || [];
      const cVal = (d.classic && d.classic.val_losses) || [];
      const qTrain = (d.quantum && d.quantum.train_losses) || [];
      const qVal = (d.quantum && d.quantum.val_losses) || [];
      const epochs = cTrain.map((_, i) => i + 1);

      const option = {
        backgroundColor: '#fff',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255,255,255,0.96)',
          borderColor: '#EBEEF5',
          borderWidth: 1,
          textStyle: { color: '#020814', fontSize: 13 },
        },
        legend: {
          top: 16,
          textStyle: { color: '#41464F', fontSize: 13 },
          itemWidth: 24,
          itemHeight: 3,
          itemGap: 20,
        },
        grid: { top: 64, right: 72, bottom: 48, left: 72 },
        xAxis: {
          type: 'category',
          data: epochs,
          name: 'Epoch',
          nameTextStyle: { color: '#8A8F98', fontSize: 12 },
          axisLine: { lineStyle: { color: '#E4E7ED' } },
          axisTick: { show: false },
          axisLabel: { color: '#8A8F98', fontSize: 11 },
        },
        yAxis: [
          {
            type: 'value',
            name: '经典 LSTM Loss',
            nameTextStyle: { color: '#8A8F98', fontSize: 12 },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: '#F4F5F7', type: 'dashed' } },
            axisLabel: { color: '#8A8F98', fontSize: 11 },
          },
          {
            type: 'value',
            name: 'QLSTM Loss',
            nameTextStyle: { color: '#8A8F98', fontSize: 12 },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { color: '#8A8F98', fontSize: 11 },
          },
        ],
        series: [
          {
            name: '经典-训练损失',
            type: 'line',
            data: cTrain,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2, color: '#1664FF' },
            itemStyle: { color: '#1664FF' },
          },
          {
            name: '经典-验证损失',
            type: 'line',
            data: cVal,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2, type: 'dashed', color: '#1664FF', opacity: 0.6 },
            itemStyle: { color: '#1664FF', opacity: 0.6 },
          },
          {
            name: 'QLSTM-训练损失',
            type: 'line',
            yAxisIndex: 1,
            data: qTrain,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2.5, color: '#00D4FF' },
            itemStyle: { color: '#00D4FF' },
          },
          {
            name: 'QLSTM-验证损失',
            type: 'line',
            yAxisIndex: 1,
            data: qVal,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2.5, type: 'dashed', color: '#00D4FF', opacity: 0.6 },
            itemStyle: { color: '#00D4FF', opacity: 0.6 },
          },
        ],
        dataZoom: [
          { type: 'inside', start: 0, end: 100 },
        ],
      };

      trainingChart.setOption(option);
    }

    function initFutureChart() {
      const dom = document.getElementById('future-chart');
      if (!dom) return;

      futureChart = disposeChart(futureChart);

      // 需要原始数据或未来预测数据
      if (!rawData.value && !futurePredictions.value) return;
      futureChart = echarts.init(dom);

      const histDates = (rawData.value?.dates || []);
      const histClose = (rawData.value?.close || []);
      const predDates = (futurePredictions.value?.dates || []);
      const predClassic = (futurePredictions.value?.classic || []);
      const predQuantum = (futurePredictions.value?.quantum || []);

      // 拼接历史 + 未来日期
      const allDates = [...histDates, ...predDates];

      // 历史数据: close 值后面补 null
      const histSeries = [...histClose, ...new Array(predDates.length).fill(null)];

      // 经典预测: 前面补 null + 衔接点
      const classicSeries = new Array(histDates.length - 1).fill(null);
      if (histClose.length > 0) classicSeries.push(histClose[histClose.length - 1]);
      classicSeries.push(...predClassic);

      // 量子预测: 前面补 null + 衔接点
      const quantumSeries = new Array(histDates.length - 1).fill(null);
      if (histClose.length > 0) quantumSeries.push(histClose[histClose.length - 1]);
      quantumSeries.push(...predQuantum);

      const option = {
        backgroundColor: '#fff',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255,255,255,0.96)',
          borderColor: '#EBEEF5',
          borderWidth: 1,
          textStyle: { color: '#020814', fontSize: 13 },
          formatter: function(params) {
            const validParams = params.filter(p => p.value != null);
            if (validParams.length === 0) return '';
            let html = `<div style="font-weight:600;margin-bottom:6px">${validParams[0].axisValue}</div>`;
            validParams.forEach(p => {
              html += `<div style="display:flex;align-items:center;gap:6px;margin:3px 0">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${p.color}"></span>
                <span>${p.seriesName}:</span>
                <span style="font-weight:600">$${Number(p.value).toFixed(2)}</span>
              </div>`;
            });
            return html;
          }
        },
        legend: {
          top: 16,
          textStyle: { color: '#41464F', fontSize: 13 },
          itemWidth: 24,
          itemHeight: 3,
        },
        grid: { top: 64, right: 32, bottom: 48, left: 72 },
        xAxis: {
          type: 'category',
          data: allDates,
          axisLine: { lineStyle: { color: '#E4E7ED' } },
          axisTick: { show: false },
          axisLabel: {
            color: '#8A8F98',
            fontSize: 11,
            formatter: function(val) {
              if (!val) return '';
              return val.length > 10 ? val.substring(0, 10) : val;
            }
          },
        },
        yAxis: {
          type: 'value',
          name: '价格 ($)',
          nameTextStyle: { color: '#8A8F98', fontSize: 12 },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#F4F5F7', type: 'dashed' } },
          axisLabel: { color: '#8A8F98', fontSize: 11 },
        },
        visualMap: {
          show: false,
          dimension: 0,
          seriesIndex: 0,
          pieces: [
            { lte: histDates.length - 1, color: '#8A8F98' },
            { gt: histDates.length - 1, color: '#8A8F98' },
          ],
        },
        series: [
          {
            name: '历史价格',
            type: 'line',
            data: histSeries,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2, color: '#8A8F98' },
            itemStyle: { color: '#8A8F98' },
            connectNulls: false,
          },
          {
            name: 'LSTM预测',
            type: 'line',
            data: classicSeries,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2.5, type: 'dashed', color: '#FB4214' },
            itemStyle: { color: '#FB4214' },
            connectNulls: false,
          },
          {
            name: 'QLSTM预测',
            type: 'line',
            data: quantumSeries,
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: { width: 2.5, type: 'dashed', color: '#1664FF' },
            itemStyle: { color: '#1664FF' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(22, 100, 255, 0.15)' },
                { offset: 1, color: 'rgba(22, 100, 255, 0.02)' },
              ]),
            },
            connectNulls: false,
          },
        ],
        dataZoom: [
          { type: 'inside', start: Math.max(0, (1 - 120 / allDates.length) * 100), end: 100 },
        ],
      };

      futureChart.setOption(option);
    }

    function initRawDataChart() {
      if (!rawData.value) return;
      const dom = document.getElementById('rawdata-chart');
      if (!dom) return;

      rawDataChart = disposeChart(rawDataChart);
      rawDataChart = echarts.init(dom);

      const d = rawData.value;
      const dates = d.dates || [];
      const close = d.close || [];
      const open = d.open || [];
      const high = d.high || [];
      const low = d.low || [];
      const volume = d.volume || [];

      // 有 OHLC 数据时用 K 线图，否则用折线图
      const hasOHLC = open.length > 0 && high.length > 0 && low.length > 0;

      const option = {
        backgroundColor: '#fff',
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255,255,255,0.96)',
          borderColor: '#EBEEF5',
          borderWidth: 1,
          textStyle: { color: '#020814', fontSize: 13 },
          axisPointer: { type: 'cross' },
        },
        legend: {
          top: 16,
          textStyle: { color: '#41464F', fontSize: 13 },
          itemWidth: 24,
          itemHeight: 3,
        },
        grid: [
          { top: 64, right: 32, bottom: '32%', left: 72 },
          { top: '76%', right: 32, bottom: 48, left: 72 },
        ],
        xAxis: [
          {
            type: 'category',
            data: dates,
            gridIndex: 0,
            axisLine: { lineStyle: { color: '#E4E7ED' } },
            axisTick: { show: false },
            axisLabel: { show: false },
          },
          {
            type: 'category',
            data: dates,
            gridIndex: 1,
            axisLine: { lineStyle: { color: '#E4E7ED' } },
            axisTick: { show: false },
            axisLabel: {
              color: '#8A8F98',
              fontSize: 11,
              formatter: function(val) {
                if (!val) return '';
                return val.length > 10 ? val.substring(0, 10) : val;
              }
            },
          },
        ],
        yAxis: [
          {
            type: 'value',
            name: '价格 ($)',
            gridIndex: 0,
            nameTextStyle: { color: '#8A8F98', fontSize: 12 },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: '#F4F5F7', type: 'dashed' } },
            axisLabel: { color: '#8A8F98', fontSize: 11 },
            scale: true,
          },
          {
            type: 'value',
            name: '成交量',
            gridIndex: 1,
            nameTextStyle: { color: '#8A8F98', fontSize: 12 },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: '#F4F5F7', type: 'dashed' } },
            axisLabel: { color: '#8A8F98', fontSize: 11 },
          },
        ],
        series: hasOHLC ? [
          {
            name: 'K线',
            type: 'candlestick',
            data: dates.map((_, i) => [open[i], close[i], low[i], high[i]]),
            xAxisIndex: 0,
            yAxisIndex: 0,
            itemStyle: {
              color: '#17C653',
              color0: '#F53F3F',
              borderColor: '#17C653',
              borderColor0: '#F53F3F',
            },
          },
          {
            name: '成交量',
            type: 'bar',
            data: volume,
            xAxisIndex: 1,
            yAxisIndex: 1,
            itemStyle: {
              color: 'rgba(22, 100, 255, 0.3)',
            },
            barMaxWidth: 8,
          },
        ] : [
          {
            name: '收盘价',
            type: 'line',
            data: close,
            xAxisIndex: 0,
            yAxisIndex: 0,
            smooth: true,
            symbol: 'none',
            lineStyle: { width: 2, color: '#1664FF' },
            itemStyle: { color: '#1664FF' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(22, 100, 255, 0.12)' },
                { offset: 1, color: 'rgba(22, 100, 255, 0.01)' },
              ]),
            },
          },
          {
            name: '成交量',
            type: 'bar',
            data: volume,
            xAxisIndex: 1,
            yAxisIndex: 1,
            itemStyle: {
              color: 'rgba(22, 100, 255, 0.3)',
            },
            barMaxWidth: 8,
          },
        ],
        dataZoom: [
          { type: 'inside', xAxisIndex: [0, 1], start: Math.max(0, (1 - 120 / dates.length) * 100), end: 100 },
        ],
      };

      rawDataChart.setOption(option);
    }

    // ---- Tab 切换 ----
    async function handleTabChange(tab) {
      activeTab.value = tab;
      await nextTick();

      // 根据当前 tab 渲染对应图表
      switch (tab) {
        case 'predictions':
          if (predictions.value) initPredictionChart();
          break;
        case 'training':
          if (trainingCurves.value) initTrainingChart();
          break;
        case 'future':
          if (rawData.value) initFutureChart();
          break;
        case 'rawdata':
          if (rawData.value) initRawDataChart();
          break;
      }

      // resize 图表
      [predictionChart, trainingChart, futureChart, rawDataChart].forEach(c => {
        if (c) c.resize();
      });
    }

    // ---- 窗口 resize ----
    function handleResize() {
      [predictionChart, trainingChart, futureChart, rawDataChart].forEach(c => {
        if (c) c.resize();
      });
    }

    // ---- 生命周期 ----
    onMounted(async () => {
      window.addEventListener('resize', handleResize);

      // 并行加载所有数据
      await Promise.all([
        fetchComparison(),
        fetchPredictions(),
        fetchTrainingCurves(),
        fetchRawData(),
      ]);

      // 渲染默认 tab 的图表
      await nextTick();
      if (activeTab.value === 'comparison' && predictions.value) {
        // 对比页不需要图表
      }
    });

    return {
      activeTab,
      loading,
      comparison,
      predictions,
      trainingCurves,
      rawData,
      futurePredictions,
      predictDays,
      backendOnline,
      lastUpdate,
      overallImprovement,
      comparisonTableData,
      formatNumber,
      formatPercent,
      getImprovementClass,
      predictFuture,
      handleTabChange,
    };
  },
});

app.use(ElementPlus, { locale: ElementPlusLocaleZhCn });
app.mount('#app');
