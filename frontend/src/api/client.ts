// Concept by MrHan (08974747477)
// Axios instance for the backend API. Same-origin: the /api path is proxied to
// the backend by Vite (dev) or the frontend Nginx container (production).
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// Phase 2: attach the JWT from auth storage and handle 401 refresh/redirect.
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
