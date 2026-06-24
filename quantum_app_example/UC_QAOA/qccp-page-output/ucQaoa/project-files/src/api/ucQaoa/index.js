import axios from '../../utils/axios';

const API_BASE = '/api/uc-qaoa';

export const getGenerators = () => {
  return axios({
    url: `${API_BASE}/generators`,
    method: 'get',
  });
};

export const solveQAOA = data => {
  return axios({
    url: `${API_BASE}/solve`,
    method: 'post',
    data,
  });
};

export const solveClassical = data => {
  return axios({
    url: `${API_BASE}/solve-classical`,
    method: 'post',
    data,
  });
};
