import request from '@/utils/request';

export function getAppInfo() {
  return request({ url: '/api/info', method: 'get' });
}

export function getBaseline() {
  return request({ url: '/api/baseline', method: 'get' });
}

export function runVqe(params) {
  return request({ url: '/api/vqe', method: 'get', params });
}

export function getComparison() {
  return request({ url: '/api/compare', method: 'get' });
}
