import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  withCredentials: true,
})

export const citizenApi = {
  profile:         ()     => api.get('/citizen/profile'),
  updateProfile:   (data) => api.put('/citizen/profile', data),
  chat:            (data) => api.post('/citizen/chat', data),
  chatHistory:     ()     => api.get('/citizen/chat/history'),
  clearHistory:    ()     => api.delete('/citizen/chat/history'),
  optimizeGoals:   (data) => api.post('/citizen/goals/optimize', data),
  analyzeDebt:     (data) => api.post('/citizen/debt/analyse', data),
  analyzeSpending: (data) => api.post('/citizen/spending/analyse', data),
  betting:         (data) => api.post('/citizen/betting/risk', data),
}