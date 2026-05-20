/**
 * WIRED DASHBOARD HOME - CONNECTED TO COMPREHENSIVE API
 * This component now uses the new comprehensiveApi to connect to all Python modules
 */

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { comprehensiveApi } from '../../api/comprehensiveApi';

export default function DashboardHome() {
  const [activeModule, setActiveModule] = useState('overview');

  // Health check to ensure backend is connected
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: comprehensiveApi.health,
    refetchInterval: 30000, // Check every 30 seconds
  });

  // Quick actions for different modules
  const quickActions = [
    {
      id: 'spending',
      title: 'Analyze Spending',
      description: 'Get AI-powered spending analysis',
      icon: '💰',
      api: 'analyzeSpending',
      color: 'blue'
    },
    {
      id: 'debt',
      title: 'Debt Analysis',
      description: 'Analyze and optimize your debt',
      icon: '💳',
      api: 'debtBurden',
      color: 'purple'
    },
    {
      id: 'goals',
      title: 'Goal Planning',
      description: 'Create and optimize financial goals',
      icon: '🎯',
      api: 'optimizeGoals',
      color: 'green'
    },
    {
      id: 'investment',
      title: 'Investment Advice',
      description: 'Get AI investment recommendations',
      icon: '📈',
      api: 'recommendInvestments',
      color: 'orange'
    },
    {
      id: 'mental',
      title: 'Mental Health',
      description: 'Assess your financial stress',
      icon: '🧠',
      api: 'mentalHealthAssessment',
      color: 'pink'
    },
    {
      id: 'betting',
      title: 'Betting Assessment',
      description: 'Analyze gambling behavior',
      icon: '🎲',
      api: 'assessBetting',
      color: 'red'
    },
    {
      id: 'emergency',
      title: 'Emergency Fund',
      description: 'Calculate emergency fund needs',
      icon: '🆘',
      api: 'emergencyFund',
      color: 'yellow'
    },
    {
      id: 'ml',
      title: 'ML Predictions',
      description: 'Get AI financial predictions',
      icon: '🤖',
      api: 'mlPredict',
      color: 'indigo'
    }
  ];

  const [quickResults, setQuickResults] = useState({});

  const handleQuickAction = async (action) => {
    try {
      let result;
      switch (action.api) {
        case 'analyzeSpending':
          result = await comprehensiveApi.analyzeSpending({
            income: 50000,
            expenses: { food: 5000, transport: 2000, entertainment: 1500 }
          });
          break;
        case 'debtBurden':
          result = await comprehensiveApi.debtBurden({
            income: 50000,
            debts: [{ name: 'Personal Loan', balance: 100000, interest_rate: 12, emi: 5000 }]
          });
          break;
        case 'optimizeGoals':
          result = await comprehensiveApi.optimizeGoals({
            goals: [{ name: 'Emergency Fund', target_amount: 100000, deadline_months: 12 }],
            available_monthly: 15000
          });
          break;
        case 'recommendInvestments':
          result = await comprehensiveApi.recommendInvestments({
            user_profile: { age: 25, risk_level: 'moderate', income: 50000 }
          });
          break;
        case 'mentalHealthAssessment':
          result = await comprehensiveApi.mentalHealthAssessment({
            user_input: 'I am stressed about my finances'
          });
          break;
        case 'assessBetting':
          result = await comprehensiveApi.assessBetting({
            user_input: 'I occasionally bet on sports'
          });
          break;
        case 'emergencyFund':
          result = await comprehensiveApi.emergencyFund({
            monthly_expenses: 30000,
            dependents: 0
          });
          break;
        case 'mlPredict':
          result = await comprehensiveApi.mlPredict({
            financial_history: [1000, 1200, 1100, 1300, 1400],
            months_ahead: 6
          });
          break;
        default:
          result = { data: { message: 'Module not available' } };
      }
      
      setQuickResults(prev => ({ ...prev, [action.id]: result.data }));
      toast.success(`${action.title} completed!`);
    } catch (error) {
      toast.error(`${action.title} failed: ${error.message}`);
    }
  };

  if (healthLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Connecting to Python modules...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">
              🚀 Youth Finance Bot - All Modules Connected
            </h1>
            <p className="text-gray-600 mt-2">
              Complete AI-powered financial analysis system
            </p>
          </div>
          <div className="text-right">
            <div className={`px-4 py-2 rounded-lg ${healthData?.data?.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {healthData?.data?.status === 'healthy' ? '✅ All Systems Online' : '❌ System Error'}
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {healthData?.data?.modules_loaded?.length || 0} Python modules loaded
            </p>
          </div>
        </div>

        {/* Module Status */}
        {healthData?.data?.modules_loaded && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Loaded Python Modules:</h3>
            <div className="flex flex-wrap gap-2">
              {healthData.data.modules_loaded.map((module, index) => (
                <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  {module}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {quickActions.map((action) => (
          <div key={action.id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="text-4xl mb-4">{action.icon}</div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">{action.title}</h3>
            <p className="text-sm text-gray-600 mb-4">{action.description}</p>
            <button
              onClick={() => handleQuickAction(action)}
              className={`w-full bg-${action.color}-600 text-white py-2 px-4 rounded-lg hover:bg-${action.color}-700 transition-colors`}
            >
              Test Module
            </button>
            
            {quickResults[action.id] && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600 font-semibold mb-1">Result:</p>
                <pre className="text-xs text-gray-500 whitespace-pre-wrap overflow-hidden max-h-20">
                  {JSON.stringify(quickResults[action.id], null, 2)}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Module Details */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Module Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-700 mb-3">📊 Analysis Modules</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✅ Spending Analysis - AI-powered expense tracking</li>
              <li>✅ Debt Analysis - Smart debt optimization</li>
              <li>✅ Investment Analysis - Risk assessment & recommendations</li>
              <li>✅ Statement Analysis - Bank statement parsing</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-700 mb-3">🤖 AI/ML Modules</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✅ ML Predictions - Financial forecasting</li>
              <li>✅ LLM Engine - AI advice generation</li>
              <li>✅ Mental Health - Stress assessment</li>
              <li>✅ Crisis Detection - Risk monitoring</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-700 mb-3">🎯 Planning Modules</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✅ Goal Planning - Smart goal optimization</li>
              <li>✅ Emergency Fund - Safety net calculation</li>
              <li>✅ Zero Investment - Earning opportunities</li>
              <li>✅ Schemes - Government benefits matching</li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-700 mb-3">🛡️ Protection Modules</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>✅ Legal Protection - Rights & guidance</li>
              <li>✅ Betting Assessment - Gambling analysis</li>
              <li>✅ Debt Trap Detection - Early warning system</li>
              <li>✅ Report Generation - PDF documentation</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
