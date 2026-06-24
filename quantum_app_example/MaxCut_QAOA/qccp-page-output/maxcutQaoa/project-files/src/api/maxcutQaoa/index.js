import request from '@/utils/axios.js';

export function getGraphs() {
  return request({
    url: '/maxcut-qaoa/graphs',
    method: 'get',
  });
}

export function getGraph(name) {
  return request({
    url: `/maxcut-qaoa/graph/${name}`,
    method: 'get',
  });
}

export function solveQaoa(data) {
  return request({
    url: '/maxcut-qaoa/solve',
    method: 'post',
    data,
  });
}

export function bruteForce(data) {
  return request({
    url: '/maxcut-qaoa/brute-force',
    method: 'post',
    data,
  });
}
