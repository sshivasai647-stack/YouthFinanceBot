import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { formatCurrency } from '../../lib/utils'
import { TrendingUp, Upload, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'

const schema = z.object({
  monthly_income: z.coerce.number().min(1, 'Required'),
  spending_data:  z.string().min(10, 'Enter at least one spending line'),
})

// Parse "Category, Amount" lines into { Category: Amount } dict
function parseSpendingText(text) {
  const expenses = {}
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)
  for (const line of lines) {
    const parts = line.split(',').map(p => p.trim())
    if (parts.length < 2) continue
    const category = parts[0]
    const amount   = parseFloat(parts[1])
    if (!category || isNaN(amount) || amount < 0) continue
    expenses[category] = (expenses[category] || 0) + amount
  }
  return expenses
}

export default function SpendingPage() {
  const [result, setResult] = useState(null)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  })

  const mutation = useMutation({
    mutationFn: (data) => {
      const expenses = parseSpendingText(data.spending_data)
      if (Object.keys(expenses).length === 0) {
        throw new Error('No valid lines found. Use format: Category, Amount')
      }
      // Backend SpendingAnalyseSchema expects: { income, expenses{}, debt }
      return citizenApi.analyzeSpending({
        income:   data.monthly_income,
        expenses,
        debt:     0,
      })
    },
    onSuccess: (res) => { setResult(res.data); toast.success('Spending analysis complete!') },
    onError:   (err) => toast.error(err.response?.data?.error ?? err.message ?? 'Failed'),
  })

  // Backend returns: { analysis: { total_income, total_expenses, savings, savings_rate,
  //   financial_health, highest_expense_category, highest_expense_amount }, saving_tip }
  const analysis = result?.analysis ?? {}

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-yellow-100 text-yellow-600 flex items-center justify-center">
          <TrendingUp size={20} />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">Spending Analyser</h1>
          <p className="text-sm text-slate-500">Enter your spending data and get AI insights</p>
        </div>
      </div>

      {/* Info card */}
      <div className="card bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-3">
          <Upload size={18} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-slate-700 dark:text-slate-300">
            <p className="font-semibold mb-1">Format: one line per transaction</p>
            <p className="text-xs leading-relaxed">
              <code className="bg-slate-100 dark:bg-slate-700 px-1 py-0.5 rounded">Category, Amount</code>
              &nbsp;or&nbsp;
              <code className="bg-slate-100 dark:bg-slate-700 px-1 py-0.5 rounded">Category, Amount, Date</code>
              <br />Example: <code className="bg-slate-100 dark:bg-slate-700 px-1 py-0.5 rounded">Food, 500, 2024-01-15</code>
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5">
          <div className="max-w-xs">
            <label className="label">Monthly Income (₹)</label>
            <input
              {...register('monthly_income')}
              type="number"
              placeholder="30000"
              className={`input ${errors.monthly_income ? 'input-error' : ''}`}
            />
            {errors.monthly_income && <p className="text-xs text-danger mt-1">{errors.monthly_income.message}</p>}
          </div>

          <div>
            <label className="label">Spending Data</label>
            <textarea
              {...register('spending_data')}
              rows={12}
              placeholder={"Food, 500\nTransport, 200\nEntertainment, 800\nShopping, 1500"}
              className={`input resize-none font-mono text-xs ${errors.spending_data ? 'input-error' : ''}`}
            />
            {errors.spending_data && <p className="text-xs text-danger mt-1">{errors.spending_data.message}</p>}
          </div>

          <button type="submit" disabled={mutation.isPending} className="btn-primary flex items-center gap-2">
            <Sparkles size={16} />
            {mutation.isPending ? 'Analysing...' : 'Analyse Spending'}
          </button>
        </form>
      </div>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {/* Stats grid — mapped to actual backend fields */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Income',   value: formatCurrency(analysis.total_income),   color: 'text-success'  },
                { label: 'Total Expenses', value: formatCurrency(analysis.total_expenses), color: 'text-danger'   },
                { label: 'Savings',        value: formatCurrency(analysis.savings),         color: 'text-primary'  },
                { label: 'Savings Rate',   value: `${analysis.savings_rate ?? 0}%`,         color: (analysis.savings_rate ?? 0) >= 20 ? 'text-success' : 'text-warning' },
              ].map(({ label, value, color }) => (
                <div key={label} className="card-sm text-center">
                  <p className={`text-lg font-extrabold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {/* Financial health */}
            {analysis.financial_health && (
              <div className="card bg-slate-50 dark:bg-slate-700/50 flex items-center gap-3">
                <span className="text-2xl">{analysis.financial_health.split(' ')[0]}</span>
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">
                    Financial Health: {analysis.financial_health.replace(/^[^\s]+\s/, '')}
                  </p>
                  {analysis.highest_expense_category && (
                    <p className="text-xs text-slate-500 mt-0.5">
                      Biggest spend: <span className="font-medium capitalize">{analysis.highest_expense_category}</span>
                      &nbsp;— {formatCurrency(analysis.highest_expense_amount)}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Saving tip */}
            {result.saving_tip && (
              <div className="card border-l-4 border-primary">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={16} className="text-primary" />
                  <h3 className="font-bold text-slate-900 dark:text-white">AI Saving Tip</h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{result.saving_tip}</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
