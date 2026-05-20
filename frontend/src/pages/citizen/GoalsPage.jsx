/**
 * WIRED GOALS PAGE - CONNECTED TO COMPREHENSIVE API
 * This component now uses the new comprehensiveApi to connect to Python modules
 */

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { comprehensiveApi } from '../../api/comprehensiveApi';

export default function GoalsPage() {
  const [result, setResult] = useState(null);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      goal_name: '',
      target_amount: '',
      deadline_months: '',
      monthly_income: '',
      current_savings: ''
    }
  });

  const mutation = useMutation({
    mutationFn: (data) => comprehensiveApi.optimizeGoals({
      goals: [{
        name: data.goal_name,
        target_amount: parseFloat(data.target_amount),
        deadline_months: parseInt(data.deadline_months)
      }],
      available_monthly: parseFloat(data.monthly_income) * 0.3 // 30% of income for goals
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Goal plan generated!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to generate goal plan');
    }
  });

  const createGoalMutation = useMutation({
    mutationFn: (data) => comprehensiveApi.createGoal({
      goal_data: {
        name: data.goal_name,
        target_amount: parseFloat(data.target_amount),
        deadline_months: parseInt(data.deadline_months),
        current_amount: parseFloat(data.current_savings || 0)
      }
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Goal created successfully!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to create goal');
    }
  });

  const checkProgressMutation = useMutation({
    mutationFn: (data) => comprehensiveApi.checkGoalProgress({
      goal_id: data.goal_name,
      current_amount: parseFloat(data.current_savings || 0)
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Progress checked!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to check progress');
    }
  });

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          🎯 Goal Planning
        </h1>
        <p className="text-gray-600 mb-8">
          AI-powered savings plan to reach your goals
        </p>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Goal Name
            </label>
            <input
              {...register('goal_name', { required: 'Goal name is required' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Emergency Fund"
            />
            {errors.goal_name && (
              <p className="text-red-500 text-sm mt-1">{errors.goal_name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Amount (₹)
            </label>
            <input
              type="number"
              {...register('target_amount', { required: 'Target amount is required' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="100000"
            />
            {errors.target_amount && (
              <p className="text-red-500 text-sm mt-1">{errors.target_amount.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Deadline (months)
            </label>
            <input
              type="number"
              {...register('deadline_months', { required: 'Deadline is required' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="12"
            />
            {errors.deadline_months && (
              <p className="text-red-500 text-sm mt-1">{errors.deadline_months.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Monthly Income (₹)
            </label>
            <input
              type="number"
              {...register('monthly_income', { required: 'Monthly income is required' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="50000"
            />
            {errors.monthly_income && (
              <p className="text-red-500 text-sm mt-1">{errors.monthly_income.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Savings (₹) - Optional
            </label>
            <input
              type="number"
              {...register('current_savings')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="10000"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {mutation.isPending ? 'Generating plan...' : 'Generate Goal Plan'}
            </button>

            <button
              type="button"
              onClick={() => createGoalMutation.mutate({ ...register() })}
              disabled={createGoalMutation.isPending}
              className="flex-1 bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {createGoalMutation.isPending ? 'Creating...' : 'Create Goal'}
            </button>

            <button
              type="button"
              onClick={() => checkProgressMutation.mutate({ ...register() })}
              disabled={checkProgressMutation.isPending}
              className="flex-1 bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {checkProgressMutation.isPending ? 'Checking...' : 'Check Progress'}
            </button>
          </div>
        </form>

        {result && (
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Results</h3>
            <pre className="text-sm text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
