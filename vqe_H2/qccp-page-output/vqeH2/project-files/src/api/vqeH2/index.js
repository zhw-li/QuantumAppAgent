import axios from '../../utils/axios';

const API_BASE = '/api/vqe-h2';

export const getInfo = () => {
  return axios({ url: `${API_BASE}/info`, method: 'get' });
};

export const solveVQE = data => {
  return axios({ url: `${API_BASE}/solve`, method: 'post', data });
};

export const getEnergyCurve = () => {
  return axios({ url: `${API_BASE}/energy_curve`, method: 'get' });
};
