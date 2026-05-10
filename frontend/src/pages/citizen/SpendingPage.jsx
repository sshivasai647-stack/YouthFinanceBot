import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { formatCurrency } from '../../lib/utils'
import { TrendingUp, Upload, Sparkles, PieChart } from 'lucide-react'
import toast from 'react-hot-toast'

const schema = z.object({
  monthly_income: z.coerce.number().min(1, 'Required'),
  spending_data:  z.string().min(10, 'Enter spending data'),
})

export default function SpendingPage() {
  const [result, setResult] = useState(null)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  })

  const mutation = useMutation({
    mutationFn: (data) => citizenApi.analyzeSpending(data),
    onSuccess:  (res)  => { setResult(res.data); toast.success('Spending analysis complete!') },
    onError:    (err)  => toast.error(err.response?.data?.error ?? 'Failed'),
  })

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-yellow-100 text-yellow-600
                        flex items-center justify-center">
          <TrendingUp size={20} />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">
            Spending Analyser
          </h1>
          <p className="text-sm text-slate-500">
            Upload your spending data and get AI insights
          </p>
        </div>
      </div>

      {/* Info card */}
      <div className="card bg-blue-50 dark:bg-blue-900/10 border border-blue-200
                      dark:border-blue-800">
        <div className="flex items-start gap-3">
          <Upload size={18} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-slate-700 dark:text-slate-300">
            <p className="font-semibold mb-1">How to format your data:</p>
            <p className="text-xs leading-relaxed">
              Enter one transaction per line in format: <br />
              <code className="bg-slate-100 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">
                Category, Amount, Date (optional)
              </code>
              <br />
              Example: <code className="bg-slate-100 dark:bg-slate-700 px-1 py-0.5 rounded text-xs">
                Food, 500, 2024-01-15
              </code>
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5">
          {/* Monthly income */}
          <div className="max-w-xs">
            <label className="label">Monthly Income (₹)</label>
            <input
              {...register('monthly_income')}
              type="number"
              placeholder="30000"
              className={`input ${errors.monthly_income ? 'input-error' : ''}`}
            />
            {errors.monthly_income && (
              <p className="text-xs text-danger mt-1">
                {errors.monthly_income.message}
              </p>
            )}
          </div>

          {/* Spending data */}
          <div>
            <label className="label">Spending Data</label>
            <textarea
              {...register('spending_data')}
              rows={12}
              placeholder="Food, 500, 2024-01-15&#10;Transport, 200, 2024-01-16&#10;Entertainment, 800, 2024-01-17&#10;Shopping, 1500, 2024-01-18"
              className={`input resize-none font-mono text-xs ${
                errors.spending_data ? 'input-error' : ''
              }`}
            />
            {errors.spending_data && (
              <p className="text-xs text-danger mt-1">
                {errors.spending_data.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <Sparkles size={16} />
            {mutation.isPending ? 'Analysing...' : 'Analyse Spending'}
          </button>
        </form>
      </div>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Summary stats */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { label: 'Total Spent',    value: formatCurrency(result.total_spending),    color: 'text-danger'  },
                { label: 'Avg Per Day',    value: formatCurrency(result.avg_daily_spend),   color: 'text-warning' },
                { label: 'Top Category',   value: result.top_category ?? '—',               color: 'text-primary' },
              ].map(({ label, value, color }) => (
                <div key={label} className="card-sm text-center">
                  <p className={`text-lg font-extrabold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {/* Category breakdown */}
            {result.category_breakdown && Object.keys(result.category_breakdown).length > 0 && (
              <div className="card">
                <h3 className="font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <PieChart size={16} className="text-primary" />
                  Category Breakdown
                </h3>
                <div className="space-y-3">
                  {Object.entries(result.category_breakdown)
                    .sort(([, a], [, b]) => b - a)
                    .map(([category, amount]) => {
                      const percent = result.total_spending
                        ? ((amount / result.total_spending) * 100).toFixed(1)
                        : 0
                      return (
                        <div key={category}>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium text-slate-700
                                             dark:text-slate-300 capitalize">
                              {category}
                            </span>
                            <span className="text-sm font-bold text-slate-900
                                             dark:text-white">
                              {formatCurrency(amount)} ({percent}%)
                            </span>
                          </div>
                          <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full
                                          overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${percent}%` }}
                              transition={{ duration: 0.6, delay: 0.1 }}
                              className="h-full bg-primary rounded-full"
                            />
                          </div>
                        </div>
                      )
                    })}
                </div>
              </div>
            )}

            {/* AI Insights */}
            {result.insights && (
              <div className="card border-l-4 border-primary">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={16} className="text-primary" />
                  <h3 className="font-bold text-slate-900 dark:text-white">
                    AI Spending Insights
                  </h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300
                              whitespace-pre-wrap leading-relaxed">
                  {result.insights}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}