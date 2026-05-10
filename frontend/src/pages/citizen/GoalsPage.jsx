import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { formatCurrency } from '../../lib/utils'
import {
  Target, Sparkles, TrendingUp, Calendar,
  DollarSign, PiggyBank
} from 'lucide-react'
import toast from 'react-hot-toast'

const schema = z.object({
  goal_name:        z.string().min(2, 'Enter a goal name'),
  goal_amount:      z.coerce.number().min(1000, 'Min ₹1,000'),
  monthly_income:   z.coerce.number().min(1, 'Enter income'),
  monthly_expenses: z.coerce.number().min(0, 'Enter expenses'),
  current_savings:  z.coerce.number().min(0, 'Enter savings'),
  timeline_months:  z.coerce.number().min(1).max(360),
})

export default function GoalsPage() {
  const [result, setResult] = useState(null)

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { timeline_months: 12 },
  })

  const mutation = useMutation({
    mutationFn: (data) => citizenApi.optimizeGoals(data),
    onSuccess: (res) => {
      setResult(res.data)
      toast.success('Goal plan generated!')
    },
    onError: (err) => toast.error(err.response?.data?.error ?? 'Failed'),
  })

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-600
                        flex items-center justify-center">
          <Target size={20} />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">
            Goal Optimizer
          </h1>
          <p className="text-sm text-slate-500">
            AI-powered savings plan to reach your goals
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5">
          <div className="grid md:grid-cols-2 gap-5">
            <div>
              <label className="label">Goal Name</label>
              <input
                {...register('goal_name')}
                placeholder="e.g. Buy a Laptop"
                className={`input ${errors.goal_name ? 'input-error' : ''}`}
              />
              {errors.goal_name && (
                <p className="text-xs text-danger mt-1">{errors.goal_name.message}</p>
              )}
            </div>

            <div>
              <label className="label">Goal Amount (₹)</label>
              <input
                {...register('goal_amount')}
                type="number"
                placeholder="50000"
                className={`input ${errors.goal_amount ? 'input-error' : ''}`}
              />
              {errors.goal_amount && (
                <p className="text-xs text-danger mt-1">{errors.goal_amount.message}</p>
              )}
            </div>

            <div>
              <label className="label">Monthly Income (₹)</label>
              <input
                {...register('monthly_income')}
                type="number"
                placeholder="30000"
                className={`input ${errors.monthly_income ? 'input-error' : ''}`}
              />
              {errors.monthly_income && (
                <p className="text-xs text-danger mt-1">{errors.monthly_income.message}</p>
              )}
            </div>

            <div>
              <label className="label">Monthly Expenses (₹)</label>
              <input
                {...register('monthly_expenses')}
                type="number"
                placeholder="20000"
                className={`input ${errors.monthly_expenses ? 'input-error' : ''}`}
              />
              {errors.monthly_expenses && (
                <p className="text-xs text-danger mt-1">{errors.monthly_expenses.message}</p>
              )}
            </div>

            <div>
              <label className="label">Current Savings (₹)</label>
              <input
                {...register('current_savings')}
                type="number"
                placeholder="5000"
                className={`input ${errors.current_savings ? 'input-error' : ''}`}
              />
              {errors.current_savings && (
                <p className="text-xs text-danger mt-1">{errors.current_savings.message}</p>
              )}
            </div>

            <div>
              <label className="label">Timeline (Months)</label>
              <input
                {...register('timeline_months')}
                type="number"
                placeholder="12"
                className={`input ${errors.timeline_months ? 'input-error' : ''}`}
              />
              {errors.timeline_months && (
                <p className="text-xs text-danger mt-1">{errors.timeline_months.message}</p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <Sparkles size={16} />
            {mutation.isPending ? 'Generating plan...' : 'Generate Goal Plan'}
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
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { icon: DollarSign,  label: 'Monthly Save',    value: formatCurrency(result.monthly_savings_needed), color: 'text-primary'  },
                { icon: PiggyBank,   label: 'Surplus',         value: formatCurrency(result.monthly_surplus),        color: 'text-success'  },
                { icon: Calendar,    label: 'Achievable In',   value: `${result.achievable_months} mo`,              color: 'text-blue-600' },
                { icon: TrendingUp,  label: 'Feasibility',     value: result.feasibility,                            color: result.feasibility === 'HIGH' ? 'text-success' : 'text-warning' },
              ].map(({ icon: Icon, label, value, color }) => (
                <div key={label} className="card-sm text-center">
                  <Icon size={20} className={`${color} mx-auto mb-2`} />
                  <p className={`text-lg font-extrabold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {/* AI Advice */}
            {result.advice && (
              <div className="card border-l-4 border-primary">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={16} className="text-primary" />
                  <h3 className="font-bold text-slate-900 dark:text-white">
                    AI Recommendations
                  </h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {result.advice}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}