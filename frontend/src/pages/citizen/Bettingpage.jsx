import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { formatCurrency } from '../../lib/utils'
import { AlertTriangle, Sparkles, TrendingDown, Shield } from 'lucide-react'
import toast from 'react-hot-toast'

const schema = z.object({
  monthly_income:    z.coerce.number().min(1, 'Required'),
  betting_amount:    z.coerce.number().min(0, 'Required'),
  frequency:         z.enum(['daily', 'weekly', 'monthly']),
  duration_months:   z.coerce.number().min(1).max(120),
})

export default function BettingPage() {
  const [result, setResult] = useState(null)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { frequency: 'weekly', duration_months: 6 },
  })

  const mutation = useMutation({
    mutationFn: (data) => citizenApi.betting(data),
    onSuccess:  (res)  => { setResult(res.data); toast.success('Risk analysis complete') },
    onError:    (err)  => toast.error(err.response?.data?.error ?? 'Failed'),
  })

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-red-100 text-red-600
                        flex items-center justify-center">
          <AlertTriangle size={20} />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">
            Betting Risk Calculator
          </h1>
          <p className="text-sm text-slate-500">
            Understand the real financial impact of betting/gambling
          </p>
        </div>
      </div>

      {/* Warning banner */}
      <div className="card bg-red-50 dark:bg-red-900/10 border-2 border-red-200
                      dark:border-red-800">
        <div className="flex items-start gap-3">
          <Shield size={18} className="text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-semibold text-red-900 dark:text-red-200 mb-1">
              ⚠️ Financial Risk Warning
            </p>
            <p className="text-red-700 dark:text-red-300 text-xs leading-relaxed">
              Betting and gambling apps are designed to make you lose money over time.
              This calculator shows you the real long-term financial damage.
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5">
          <div className="grid md:grid-cols-2 gap-5">
            <div>
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

            <div>
              <label className="label">Amount Per Bet (₹)</label>
              <input
                {...register('betting_amount')}
                type="number"
                placeholder="500"
                className={`input ${errors.betting_amount ? 'input-error' : ''}`}
              />
              {errors.betting_amount && (
                <p className="text-xs text-danger mt-1">
                  {errors.betting_amount.message}
                </p>
              )}
            </div>

            <div>
              <label className="label">Betting Frequency</label>
              <select {...register('frequency')} className="input">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div>
              <label className="label">Time Period (Months)</label>
              <input
                {...register('duration_months')}
                type="number"
                placeholder="6"
                className={`input ${errors.duration_months ? 'input-error' : ''}`}
              />
              {errors.duration_months && (
                <p className="text-xs text-danger mt-1">
                  {errors.duration_months.message}
                </p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="btn-danger flex items-center gap-2"
          >
            <Sparkles size={16} />
            {mutation.isPending ? 'Calculating...' : 'Calculate Risk'}
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
            {/* Shocking stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Lost',       value: formatCurrency(result.total_loss),         color: 'text-danger'   },
                { label: 'Monthly Loss',     value: formatCurrency(result.monthly_loss),       color: 'text-red-600'  },
                { label: '% of Income',      value: `${result.income_percentage}%`,            color: 'text-warning'  },
                { label: 'Risk Level',       value: result.risk_level ?? 'HIGH',               color: 'text-danger'   },
              ].map(({ label, value, color }) => (
                <div key={label} className="card-sm text-center border-2 border-red-200
                                            dark:border-red-800">
                  <p className={`text-lg font-extrabold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {/* Alternative use */}
            {result.alternative_use && (
              <div className="card border-l-4 border-green-500 bg-green-50
                              dark:bg-green-900/10">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingDown size={16} className="text-green-600" />
                  <h3 className="font-bold text-slate-900 dark:text-white">
                    What You Could Do Instead
                  </h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300
                              whitespace-pre-wrap leading-relaxed">
                  {result.alternative_use}
                </p>
              </div>
            )}

            {/* AI Warning */}
            {result.warning && (
              <div className="card border-l-4 border-red-500 bg-red-50
                              dark:bg-red-900/10">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle size={16} className="text-red-600" />
                  <h3 className="font-bold text-red-900 dark:text-red-200">
                    AI Financial Warning
                  </h3>
                </div>
                <p className="text-sm text-red-700 dark:text-red-300
                              whitespace-pre-wrap leading-relaxed">
                  {result.warning}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}