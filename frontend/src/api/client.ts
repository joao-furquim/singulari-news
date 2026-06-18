import axios from 'axios';

const BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : '/api';

const client = axios.create({
  baseURL: BASE_URL,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.debug('[auth] Authorization header added');
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('preferences');
      window.location.href = '/';
    }
    return Promise.reject(error);
  },
);

export default client;
