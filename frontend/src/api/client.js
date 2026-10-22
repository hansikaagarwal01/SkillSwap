import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('skillswap_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Don't auto-redirect on login check failure
      if (!error.config.url.includes('/auth/login') && !error.config.url.includes('/auth/me')) {
        localStorage.removeItem('skillswap_token');
        localStorage.removeItem('skillswap_user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
