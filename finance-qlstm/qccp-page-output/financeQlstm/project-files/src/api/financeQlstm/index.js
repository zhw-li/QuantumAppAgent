import request from '@/utils/axios.js';

const BASE = '/qlstm-api';

export function fetchStocks() {
  return request({ url: `${BASE}/api/stocks`, method: 'get' });
}

export function fetchComparison() {
  return request({ url: `${BASE}/api/comparison`, method: 'get' });
}

export function fetchPredictions() {
  return request({ url: `${BASE}/api/predictions`, method: 'get' });
}

export function fetchTrainingCurves() {
  return request({ url: `${BASE}/api/training-curves`, method: 'get' });
}

export function fetchRawData(stock, days = 365) {
  return request({ url: `${BASE}/api/raw-data`, method: 'get', params: { stock, days } });
}

export function trainModels(params) {
  return request({ url: `${BASE}/api/train`, method: 'post', data: params });
}

export function fetchModelInfo() {
  return request({ url: `${BASE}/api/model-info`, method: 'get' });
}
