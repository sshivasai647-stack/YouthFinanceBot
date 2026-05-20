/**
 * COMPREHENSIVE API CLIENT - ALL PYTHON MODULES CONNECTED
 * This file contains API calls for every single Flask route created in comprehensive_routes.py
 * All calls point to http://127.0.0.1:5000
 */

import axios from 'axios';

// Create axios instance with base URL and CORS configuration
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ====================================================================
// ANALYZER MODULE API CALLS
// ====================================================================

export const analyzerApi = {
  analyzeSpending: (data) => api.post('/api/analyze/spending', data),
  getSavingTip: () => api.get('/api/analyze/saving-tip'),
};

// ====================================================================
// BETTING ALTERNATIVE MODULE API CALLS
// ====================================================================

export const bettingApi = {
  assessBettingBehavior: (data) => api.post('/api/betting/assess', data),
  runBettingAlternative: (data) => api.post('/api/betting/run', data),
};

// ====================================================================
// CRISIS DETECTOR MODULE API CALLS
// ====================================================================

export const crisisApi = {
  detectCrisis: (data) => api.post('/api/crisis/detect', data),
};

// ====================================================================
// DEBT HANDLER MODULE API CALLS
// ====================================================================

export const debtApi = {
  calculateBurden: (data) => api.post('/api/debt/calculate-burden', data),
  calculateEMI: (data) => api.post('/api/debt/calculate-emi', data),
  createRepaymentPlan: (data) => api.post('/api/debt/create-repayment-plan', data),
  prioritizeDebts: (data) => api.post('/api/debt/prioritize', data),
  detectDebtTrap: (data) => api.post('/api/debt/detect-trap', data),
  getLegalProtectionInfo: () => api.get('/api/debt/legal-protection-info'),
};

// ====================================================================
// EMERGENCY FUND MODULE API CALLS
// ====================================================================

export const emergencyFundApi = {
  calculateEmergencyFund: (data) => api.post('/api/emergency-fund/calculate', data),
  getBuildingPlan: (data) => api.post('/api/emergency-fund/building-plan', data),
  getEmergencyTip: (savingsRate) => api.get('/api/emergency-fund/tip', { params: { savings_rate: savingsRate } }),
};

// ====================================================================
// EARN SUGGESTER MODULE API CALLS
// ====================================================================

export const earnApi = {
  suggestEarning: (data) => api.post('/api/earn/suggest', data),
};

// ====================================================================
// GOAL TRACKER MODULE API CALLS
// ====================================================================

export const goalsApi = {
  createGoal: (data) => api.post('/api/goals/create', data),
  checkProgress: (data) => api.post('/api/goals/check-progress', data),
  optimizeGoals: (data) => api.post('/api/goals/optimize', data),
};

// ====================================================================
// INVESTMENT GUIDE MODULE API CALLS
// ====================================================================

export const investmentApi = {
  assessReadiness: (data) => api.post('/api/investment/assess-readiness', data),
  recommendInvestments: (data) => api.post('/api/investment/recommend', data),
  calculateGrowth: (data) => api.post('/api/investment/calculate-growth', data),
  createPlan: (data) => api.post('/api/investment/create-plan', data),
  getGovernmentSchemes: () => api.get('/api/investment/government-schemes'),
  detectScams: (data) => api.post('/api/investment/detect-scams', data),
};

// ====================================================================
// LEGAL PROTECTOR MODULE API CALLS
// ====================================================================

export const legalApi = {
  assessSituation: (data) => api.post('/api/legal/assess-situation', data),
  getProtectionInfo: () => api.get('/api/legal/protection-info'),
  runProtector: (data) => api.post('/api/legal/run-protector', data),
};

// ====================================================================
// LLM ENGINE MODULE API CALLS
// ====================================================================

export const llmApi = {
  getAdvice: (data) => api.post('/api/llm/get-advice', data),
  getQuickTip: (category) => api.get('/api/llm/quick-tip', { params: { category } }),
  getClient: (provider) => api.get('/api/llm/get-client', { params: { provider } }),
};

// ====================================================================
// MENTAL HEALTH GUARDIAN MODULE API CALLS
// ====================================================================

export const mentalHealthApi = {
  assessMentalHealth: (data) => api.post('/api/mental-health/assess', data),
  handleFollowup: (data) => api.post('/api/mental-health/handle-followup', data),
  runGuardian: (data) => api.post('/api/mental-health/run-guardian', data),
  getCrisisLevel: (levelStr) => api.get('/api/mental-health/get-crisis-level', { params: { level_str: levelStr } }),
};

// ====================================================================
// ML MODEL MODULE API CALLS
// ====================================================================

export const mlApi = {
  calculateFeatures: (data) => api.post('/api/ml/calculate-features', data),
  trainModel: (data) => api.post('/api/ml/train-model', data),
  saveModel: (data) => api.post('/api/ml/save-model', data),
  loadModel: (path) => api.get('/api/ml/load-model', { params: { path } }),
  predictFuture: (data) => api.post('/api/ml/predict-future', data),
  calculateRiskScore: (data) => api.post('/api/ml/calculate-risk-score', data),
  getTrend: (data) => api.post('/api/ml/get-trend', data),
};

// ====================================================================
// PDF REPORT MODULE API CALLS
// ====================================================================

export const reportApi = {
  generateReport: (data) => api.post('/api/report/generate', data),
};

// ====================================================================
// SCHEMES MODULE API CALLS
// ====================================================================

export const schemesApi = {
  getRelevantSchemes: (data) => api.post('/api/schemes/get-relevant', data),
  matchScheme: (data) => api.post('/api/schemes/match-scheme', data),
};

// ====================================================================
// SITUATION DETECTOR MODULE API CALLS
// ====================================================================

export const situationApi = {
  detectSituation: (data) => api.post('/api/situation/detect', data),
  routeUser: (data) => api.post('/api/situation/route-user', data),
};

// ====================================================================
// STATEMENT ANALYZER MODULE API CALLS
// ====================================================================

export const statementApi = {
  parseLines: (data) => api.post('/api/statement/parse-lines', data),
  analyzeStatement: (data) => api.post('/api/statement/analyze', data),
  summarizeTransactions: (data) => api.post('/api/statement/summarize-transactions', data),
  runAnalyzer: (data) => api.post('/api/statement/run-analyzer', data),
};

// ====================================================================
// ZERO INVESTMENT PATH MODULE API CALLS
// ====================================================================

export const zeroInvestmentApi = {
  handlePath: (data) => api.post('/api/zero-investment/handle-path', data),
  getOpportunities: (data) => api.post('/api/zero-investment/get-opportunities', data),
  createEarningPlan: (data) => api.post('/api/zero-investment/create-earning-plan', data),
  getSkillPath: (data) => api.post('/api/zero-investment/get-skill-path', data),
  filterByLevel: (level) => api.get('/api/zero-investment/filter-by-level', { params: { level } }),
  filterByCategory: (category) => api.get('/api/zero-investment/filter-by-category', { params: { category } }),
  getOpportunityByTitle: (title) => api.get('/api/zero-investment/get-opportunity-by-title', { params: { title } }),
};

// ====================================================================
// HEALTH CHECK API CALL
// ====================================================================

export const healthApi = {
  checkHealth: () => api.get('/api/health'),
};

// ====================================================================
// COMPREHENSIVE AGGREGATED API OBJECT
// ====================================================================

export const comprehensiveApi = {
  // Analyzer
  analyzeSpending: analyzerApi.analyzeSpending,
  getSavingTip: analyzerApi.getSavingTip,
  
  // Betting
  assessBetting: bettingApi.assessBettingBehavior,
  runBettingAlternative: bettingApi.runBettingAlternative,
  
  // Crisis
  detectCrisis: crisisApi.detectCrisis,
  
  // Debt
  debtBurden: debtApi.calculateBurden,
  debtEMI: debtApi.calculateEMI,
  debtRepaymentPlan: debtApi.createRepaymentPlan,
  prioritizeDebts: debtApi.prioritizeDebts,
  detectDebtTrap: debtApi.detectDebtTrap,
  debtLegalInfo: debtApi.getLegalProtectionInfo,
  
  // Emergency Fund
  emergencyFund: emergencyFundApi.calculateEmergencyFund,
  emergencyPlan: emergencyFundApi.getBuildingPlan,
  emergencyTip: emergencyFundApi.getEmergencyTip,
  
  // Earn
  suggestEarning: earnApi.suggestEarning,
  
  // Goals
  createGoal: goalsApi.createGoal,
  checkGoalProgress: goalsApi.checkProgress,
  optimizeGoals: goalsApi.optimizeGoals,
  
  // Investment
  investmentReadiness: investmentApi.assessReadiness,
  recommendInvestments: investmentApi.recommendInvestments,
  investmentGrowth: investmentApi.calculateGrowth,
  investmentPlan: investmentApi.createPlan,
  governmentSchemes: investmentApi.getGovernmentSchemes,
  detectInvestmentScams: investmentApi.detectScams,
  
  // Legal
  legalAssessment: legalApi.assessSituation,
  legalProtection: legalApi.getProtectionInfo,
  runLegalProtector: legalApi.runProtector,
  
  // LLM
  llmAdvice: llmApi.getAdvice,
  llmQuickTip: llmApi.getQuickTip,
  llmClient: llmApi.getClient,
  
  // Mental Health
  mentalHealthAssessment: mentalHealthApi.assessMentalHealth,
  mentalHealthFollowup: mentalHealthApi.handleFollowup,
  runMentalHealthGuardian: mentalHealthApi.runGuardian,
  getCrisisLevel: mentalHealthApi.getCrisisLevel,
  
  // ML
  mlFeatures: mlApi.calculateFeatures,
  mlTrain: mlApi.trainModel,
  mlSave: mlApi.saveModel,
  mlLoad: mlApi.loadModel,
  mlPredict: mlApi.predictFuture,
  mlRiskScore: mlApi.calculateRiskScore,
  mlTrend: mlApi.getTrend,
  
  // Report
  generateReport: reportApi.generateReport,
  
  // Schemes
  relevantSchemes: schemesApi.getRelevantSchemes,
  matchScheme: schemesApi.matchScheme,
  
  // Situation
  detectSituation: situationApi.detectSituation,
  routeUser: situationApi.routeUser,
  
  // Statement
  parseStatement: statementApi.parseLines,
  analyzeStatement: statementApi.analyzeStatement,
  summarizeStatement: statementApi.summarizeTransactions,
  runStatementAnalyzer: statementApi.runAnalyzer,
  
  // Zero Investment
  zeroInvestmentPath: zeroInvestmentApi.handlePath,
  zeroInvestmentOpportunities: zeroInvestmentApi.getOpportunities,
  zeroInvestmentPlan: zeroInvestmentApi.createEarningPlan,
  zeroInvestmentSkills: zeroInvestmentApi.getSkillPath,
  filterZeroInvestmentByLevel: zeroInvestmentApi.filterByLevel,
  filterZeroInvestmentByCategory: zeroInvestmentApi.filterByCategory,
  getZeroInvestmentOpportunity: zeroInvestmentApi.getOpportunityByTitle,
  
  // Health
  health: healthApi.checkHealth,
};

// Export default for easy importing
export default comprehensiveApi;

// ====================================================================
// UTILITY FUNCTIONS
// ====================================================================

/**
 * Wrapper for API calls with loading states and error handling
 */
export const apiCall = async (apiFunction, data = null, options = {}) => {
  try {
    const response = data ? await apiFunction(data) : await apiFunction();
    return {
      success: true,
      data: response.data,
      status: response.status,
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data || error.message,
      status: error.response?.status || 500,
    };
  }
};

/**
 * Batch API call utility for multiple simultaneous requests
 */
export const batchApiCall = async (calls) => {
  try {
    const responses = await Promise.allSettled(
      calls.map(({ apiFunction, data }) => data ? apiFunction(data) : apiFunction())
    );
    
    return responses.map((response, index) => ({
      index,
      success: response.status === 'fulfilled',
      data: response.status === 'fulfilled' ? response.value.data : null,
      error: response.status === 'rejected' ? response.reason : null,
    }));
  } catch (error) {
    console.error('Batch API call failed:', error);
    return [];
  }
};

/**
 * Retry utility for failed API calls
 */
export const retryApiCall = async (apiFunction, data = null, maxRetries = 3, delay = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = data ? await apiFunction(data) : await apiFunction();
      return {
        success: true,
        data: response.data,
        status: response.status,
        attempts: attempt,
      };
    } catch (error) {
      if (attempt === maxRetries) {
        return {
          success: false,
          error: error.response?.data || error.message,
          status: error.response?.status || 500,
          attempts: maxRetries,
        };
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
};
