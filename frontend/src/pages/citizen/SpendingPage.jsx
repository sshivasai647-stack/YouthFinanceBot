/**
 * WIRED SPENDING PAGE - CONNECTED TO COMPREHENSIVE API
 * This component now uses the new comprehensiveApi to connect to Python modules
 */

import React, { useState } from 'react';
import { useFieldArray, useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { comprehensiveApi } from '../../api/comprehensiveApi';

export default function SpendingPage() {
  const [result, setResult] = useState(null);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      monthly_income: '',
      spending_data: ''
    }
  });

  const mutation = useMutation({
    mutationFn: (data) => comprehensiveApi.analyzeSpending({
      income: parseFloat(data.monthly_income),
      expenses: data.spending_data
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Spending analysis complete!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to analyze spending');
    }
  });

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          💰 Spending Analyser
        </h1>
        <p className="text-gray-600 mb-8">
          AI-powered analysis of your spending patterns
        </p>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5">
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
              Spending Data (comma-separated: category,amount,date)
            </label>
            <textarea
              {...register('spending_data', { required: 'Spending data is required' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={6}
              placeholder="Food,5000,2024-01-15&#10;Transport,2000,2024-01-16&#10;Entertainment,1500,2024-01-17"
            />
            {errors.spending_data && (
              <p className="text-red-500 text-sm mt-1">{errors.spending_data.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {mutation.isPending ? 'Analysing...' : 'Analyse Spending'}
          </button>
        </form>

        {result && (
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Analysis Results</h3>
            <pre className="text-sm text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
