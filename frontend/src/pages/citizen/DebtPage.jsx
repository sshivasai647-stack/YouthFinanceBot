/**
 * WIRED DEBT PAGE - CONNECTED TO COMPREHENSIVE API
 * This component now uses the new comprehensiveApi to connect to Python modules
 */

import React, { useState } from 'react';
import { useFieldArray, useForm, Controller } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { comprehensiveApi } from '../../api/comprehensiveApi';

export default function DebtPage() {
  const [result, setResult] = useState(null);

  const { register, control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      monthly_income: '',
      debts: [{ name: '', balance: '', interest_rate: '', emi: '' }]
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'debts'
  });

  const mutation = useMutation({
    mutationFn: (data) => comprehensiveApi.debtBurden({
      income: parseFloat(data.monthly_income),
      debts: data.debts.map(debt => ({
        name: debt.name,
        balance: parseFloat(debt.balance),
        interest_rate: parseFloat(debt.interest_rate),
        emi: parseFloat(debt.emi)
      }))
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Debt analysis complete!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to analyze debt');
    }
  });

  const emiMutation = useMutation({
    mutationFn: (data) => comprehensiveApi.debtEMI({
      principal: parseFloat(data.principal),
      annual_interest_rate: parseFloat(data.annual_interest_rate),
      tenure_months: parseInt(data.tenure_months)
    }),
    onSuccess: (response) => {
      toast.success(`EMI calculated: ₹${response.data.emi.toFixed(2)}`);
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to calculate EMI');
    }
  });

  const prioritizeMutation = useMutation({
    mutationFn: (data) => comprehensiveApi.prioritizeDebts({
      debt_list: data.debts.map(debt => ({
        name: debt.name,
        balance: parseFloat(debt.balance),
        interest_rate: parseFloat(debt.interest_rate),
        emi: parseFloat(debt.emi)
      })),
      method: 'auto'
    }),
    onSuccess: (response) => {
      setResult(response.data.result);
      toast.success('Debt prioritization complete!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Failed to prioritize debts');
    }
  });

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          💳 Debt Analysis
        </h1>
        <p className="text-gray-600 mb-8">
          Analyse your debts and get an AI payoff strategy
        </p>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-6">
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
              Your Debts
            </label>
            {fields.map((field, index) => (
              <div key={field.id} className="flex gap-3 mb-3">
                <input
                  {...register(`debts.${index}.name`, { required: true })}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Debt name"
                />
                <input
                  {...register(`debts.${index}.balance`, { required: true })}
                  type="number"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Balance"
                />
                <input
                  {...register(`debts.${index}.interest_rate`, { required: true })}
                  type="number"
                  step="0.1"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Interest %"
                />
                <input
                  {...register(`debts.${index}.emi`, { required: true })}
                  type="number"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="EMI"
                />
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                >
                  Remove
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => append({ name: '', balance: '', interest_rate: '', emi: '' })}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              Add Debt
            </button>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={mutation.isPending}
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {mutation.isPending ? 'Analysing...' : 'Analyse My Debt'}
            </button>
            
            <button
              type="button"
              onClick={() => prioritizeMutation.mutate({ debts: fields })}
              disabled={prioritizeMutation.isPending}
              className="flex-1 bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {prioritizeMutation.isPending ? 'Prioritizing...' : 'Prioritize Debts'}
            </button>
          </div>
        </form>

        {/* EMI Calculator Section */}
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">EMI Calculator</h3>
          <div className="grid grid-cols-3 gap-4">
            <input
              type="number"
              placeholder="Principal Amount"
              className="px-3 py-2 border border-gray-300 rounded-lg"
              {...register('emi_principal')}
            />
            <input
              type="number"
              step="0.1"
              placeholder="Interest Rate (%)"
              className="px-3 py-2 border border-gray-300 rounded-lg"
              {...register('emi_rate')}
            />
            <input
              type="number"
              placeholder="Tenure (months)"
              className="px-3 py-2 border border-gray-300 rounded-lg"
              {...register('emi_tenure')}
            />
          </div>
          <button
            type="button"
            onClick={() => {
              const data = {
                principal: document.querySelector('input[placeholder="Principal Amount"]').value,
                annual_interest_rate: document.querySelector('input[placeholder="Interest Rate (%)"]').value,
                tenure_months: document.querySelector('input[placeholder="Tenure (months)"]').value
              };
              emiMutation.mutate(data);
            }}
            className="mt-4 bg-orange-500 text-white py-2 px-4 rounded-lg hover:bg-orange-600"
          >
            Calculate EMI
          </button>
        </div>

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
