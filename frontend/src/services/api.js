import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const api = {
  // Health
  checkHealth: async () => {
    const response = await client.get('/api/health');
    return response.data;
  },

  // Sessions
  createSession: async (title = 'Personal Wishes Document') => {
    const response = await client.post('/api/sessions', { title });
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await client.get(`/api/sessions/${sessionId}`);
    return response.data;
  },

  listSessions: async () => {
    const response = await client.get('/api/sessions');
    return response.data;
  },

  // Messages
  getMessages: async (sessionId) => {
    const response = await client.get(`/api/sessions/${sessionId}/messages`);
    return response.data;
  },

  sendMessage: async (sessionId, message) => {
    const response = await client.post(`/api/sessions/${sessionId}/messages`, { message });
    return response.data;
  },

  resetMessages: async (sessionId) => {
    const response = await client.post(`/api/sessions/${sessionId}/messages/reset`);
    return response.data;
  },

  // Structured State
  getState: async (sessionId) => {
    const response = await client.get(`/api/sessions/${sessionId}/state`);
    return response.data;
  },

  updateState: async (sessionId, updates) => {
    const response = await client.patch(`/api/sessions/${sessionId}/state`, updates);
    return response.data;
  },

  // Document
  getDocument: async (sessionId) => {
    const response = await client.get(`/api/sessions/${sessionId}/document`);
    return response.data;
  },

  regenerateDocument: async (sessionId) => {
    const response = await client.post(`/api/sessions/${sessionId}/document/regenerate`);
    return response.data;
  },

  getDocumentPdfUrl: (sessionId) => {
    return `${API_BASE_URL}/api/sessions/${sessionId}/document/pdf`;
  },
};

export default api;
