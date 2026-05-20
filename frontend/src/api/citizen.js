import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

export const citizenApi = {
  // Profile
  profile:         ()     => api.get('/citizen/profile'),
  updateProfile:   (data) => api.put('/citizen/profile', data),

  // Chat
  chat:            (data) => api.post('/citizen/chat', data),
  chatHistory:     ()     => api.get('/citizen/chat/history'),
  clearHistory:    ()     => api.delete('/citizen/chat/history'),

  // Goals
  goalsCreate:     (data) => api.post('/citizen/goals/create', data),
  goalsList:       ()     => api.get('/citizen/goals'),
  optimizeGoals:   (data) => api.post('/citizen/goals/optimize', data),

  // Debt
  analyzeDebt:     (data) => api.post('/citizen/debt/analyse', data),
  debtEmi:         (data) => api.post('/citizen/debt/emi', data),
  debtLegalInfo:   (type) => api.get('/citizen/debt/legal-info', { params: { type } }),

  // Spending & Statement
  analyzeSpending: (data) => api.post('/citizen/spending/analyse', data),
  uploadStatement: (form) => api.post('/citizen/statement/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),

  // Investment
  investmentPlan:    (data) => api.post('/citizen/investment/plan', data),
  investmentGrowth:  (data) => api.post('/citizen/investment/growth', data),
  investmentScamCheck: (data) => api.post('/citizen/investment/scam-check', data),

  // Emergency fund & savings
  emergencyFund:   (data) => api.post('/citizen/emergency-fund/calculate', data),
  savingsPredict:  (data) => api.post('/citizen/savings/predict', data),

  // Wellness & risk
  mentalHealth:    (data) => api.post('/citizen/mental-health/assess', data),
  betting:         (data) => api.post('/citizen/betting/assess', data),   // was /risk — fixed
  legalAssess:     (data) => api.post('/citizen/legal/assess', data),

  // Earn & schemes
  earnSuggest:     (params) => api.get('/citizen/earn/suggest', { params }),
  schemes:         (params) => api.get('/citizen/schemes', { params }),

  // Report & notifications
  downloadReport:  ()     => api.get('/citizen/report/download', { responseType: 'blob' }),
  notifications:   ()     => api.get('/citizen/notifications'),
  markAllRead:     ()     => api.patch('/citizen/notifications/read-all'),
  markRead:        (id)   => api.patch(`/citizen/notifications/${id}/read`),

  // Additional modules
  zeroInvestment:  (data) => api.post('/citizen/zero-investment/analyze', data),
  situationDetect: (data) => api.post('/citizen/situation/detect', data),
  routeUser:       (data) => api.post('/citizen/route/user', data),

  // LLM Engine
  llmAdvice:       (data) => api.post('/citizen/llm/advice', data),
  llmQuickTip:     (category) => api.get('/citizen/llm/quick-tip', { params: { category } }),

  // ML Model
  mlRiskScore:     (data) => api.post('/citizen/ml/risk-score', data),
  mlTrend:         (data) => api.post('/citizen/ml/trend', data),
  mlFeatures:      (data) => api.post('/citizen/ml/features', data),
  mlTrain:         (data) => api.post('/citizen/ml/train', data),
  mlPredict:       (data) => api.post('/citizen/ml/predict', data),

  // Additional Health & Zero Investment
  mentalHealthFollowup: (data) => api.post('/citizen/mental-health/followup', data),
  zeroInvestmentSkillPath: (data) => api.post('/citizen/zero-investment/skill-path', data),
  zeroInvestmentFilter: (params) => api.get('/citizen/zero-investment/filter', { params }),

  // Additional Debt Functions
  debtPrioritize:  (data) => api.post('/citizen/debt/prioritize', data),
  debtDetectTrap:  (data) => api.post('/citizen/debt/detect-trap', data),
}