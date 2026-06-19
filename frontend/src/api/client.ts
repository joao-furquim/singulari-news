/**
 * Pre-configured Axios instance for the Singulari News API.
 *
 * Provides two behaviours via interceptors:
 *
 * **Request interceptor** — attaches the stored JWT as a `Bearer` token in
 * the `Authorization` header whenever a token is present in `localStorage`.
 *
 * **Response interceptor** — on a `401 Unauthorized` response, clears all
 * auth data from `localStorage` and redirects to `/`, effectively logging
 * the user out when their token has expired or been invalidated.
 *
 * Base URL:
 * - Development (`import.meta.env.DEV`): `http://localhost:8000`
 * - Production: `/api` (proxied by the Nginx frontend container)
 *
 * @module client
 */

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
