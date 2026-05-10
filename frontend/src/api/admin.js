import axios from 'axios'

const api = axios.create({
  baseURL: '/api/admin',
  withCredentials: true,
})

export const adminApi = {
  dbStatus:        () => api.get('/db-status'),
  stats:           () => api.get('/stats'),
  users:           (params) => api.get('/users', { params }),
  blockUser:       (id, data) => api.patch(`/users/${id}/block`, data),
  unblockUser:     (id) => api.patch(`/users/${id}/unblock`),
  moduleAnalytics: () => api.get('/analytics/modules'),
  aiUsage:         () => api.get('/analytics/ai-usage'),
  auditLogs:       (params) => api.get('/logs', { params }),
  exportExcel:     () => api.get('/analytics/export', { responseType: 'blob' }),
  settings:        () => api.get('/settings'),
  updateSettings:  (payload) => api.put('/settings', payload),
}
