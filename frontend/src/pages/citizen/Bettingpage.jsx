/**
 * WIRED BETTING PAGE - CONNECTED TO COMPREHENSIVE API
 * This component now uses the new comprehensiveApi to connect to Python modules
 */

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { comprehensiveApi } from '../../api/comprehensiveApi';

export default function BettingPage() {
  const [result, setResult] = useState(null);

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      text_input: ''
    }
  });

  const mutation = useMutation({
    mutationFn: (data) => comprehensiveApi.assessBetting({
      user_input: data.text_input
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Betting risk assessment complete!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to assess betting behavior');
    }
  });

  const runBettingMutation = useMutation({
    mutationFn: (data) => comprehensiveApi.runBettingAlternative({
      user_input: data.text_input,
      user_profile: {}
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Betting alternatives generated!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to generate alternatives');
    }
  });

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          🎲 Betting Risk Assessment
        </h1>
        <p className="text-gray-600 mb-8">
          AI-powered analysis of gambling behavior and alternatives
        </p>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Describe your betting/gambling habits
            </label>
            <textarea
              {...register('text_input', { required: 'Please describe your betting habits' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={6}
              placeholder="I spend about 5000 rupees on betting every week and I am worried about my gambling habits..."
            />
            {errors.text_input && (
              <p className="text-red-500 text-sm mt-1">{errors.text_input.message}</p>
            )}
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {mutation.isPending ? 'Calculating...' : 'Calculate Risk'}
            </button>

            <button
              type="button"
              onClick={() => runBettingMutation.mutate({ text_input: register('text_input').value })}
              disabled={runBettingMutation.isPending}
              className="flex-1 bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {runBettingMutation.isPending ? 'Generating...' : 'Get Alternatives'}
            </button>
          </div>
        </form>

        {result && (
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Assessment Results</h3>
            <pre className="text-sm text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
