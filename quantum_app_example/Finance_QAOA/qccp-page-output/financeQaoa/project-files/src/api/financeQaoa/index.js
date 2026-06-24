import axios from '@/utils/axios';

const BASE = '/finance-qaoa';

export const getHealth = () => {
  return axios({
    url: `${BASE}/api/health`,
    method: 'get',
  });
};

export const getStocks = () => {
  return axios({
    url: `${BASE}/api/stocks`,
    method: 'get',
  });
};

export const getStockHistory = (symbol, days = 365) => {
  return axios({
    url: `${BASE}/api/stock/${symbol}/history`,
    method: 'get',
    params: { days },
  });
};

export const getStatistics = (tier = 'demo') => {
  return axios({
    url: `${BASE}/api/statistics`,
    method: 'get',
    params: { tier },
  });
};

export const optimizeClassical = (data) => {
  return axios({
    url: `${BASE}/api/optimize/classical`,
    method: 'post',
    data,
  });
};

export const optimizeQuantum = (data) => {
  return axios({
    url: `${BASE}/api/optimize/quantum`,
    method: 'post',
    data,
  });
};

export const compareOptimization = (data) => {
  return axios({
    url: `${BASE}/api/compare`,
    method: 'post',
    data,
  });
};
