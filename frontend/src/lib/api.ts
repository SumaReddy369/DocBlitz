import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't clear auth on login 401 (wrong credentials) - let the form show the error
    const isLoginRequest = error.config?.url?.includes('/api/auth/login');
    // Only clear auth if we had a token and got 401 on a protected route (session expired/invalid)
    if (
      !isLoginRequest &&
      error.response?.status === 401 &&
      error.config?.headers?.Authorization &&
      typeof window !== 'undefined'
    ) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post('/api/auth/register', data),

  login: (username: string, password: string) => {
    const body = new URLSearchParams({ username, password }).toString();
    return api.post('/api/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
};

export const documentsAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  list: () => api.get('/api/documents/'),

  delete: (id: string) => api.delete(`/api/documents/${id}`),
};

export const queryAPI = {
  ask: (question: string, documentId?: string) =>
    api.post('/api/query/', {
      question,
      document_id: documentId || null,
      top_k: 5,
    }),

  history: () => api.get('/api/query/history'),
};

export default api;