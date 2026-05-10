import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { formatCurrency } from '../../lib/utils'
import { CreditCard, Plus, Trash2, Sparkles, TrendingDown } from 'lucide-react'
import toast from 'react-hot-toast'

const debtSchema = z.object({
  monthly_income: z.coerce.number().min(1, 'Required'),
  debts: z.array(z.object({
    name:          z.string().min(1, 'Required'),
    balance:       z.coerce.number().min(1, 'Required'),
    interest_rate: z.coerce.number().min(0),
    emi:           z.coerce.number().min(0),
  })).min(1, 'Add at least one debt'),
})

export default function DebtPage() {
  const [result, setResult] = useState(null)

  const { register, control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(debtSchema),
    defaultValues: {
      monthly_income: '',
      debts: [{ name: '', balance: '', interest_rate: '', emi: '' }],
    },
  })

  const { fields, append, remove } = useFieldArray({ control, name: 'debts' })

  const mutation = useMutation({
    mutationFn: (data) => citizenApi.analyzeDebt(data),
    onSuccess:  (res)  => { setResult(res.data); toast.success('Debt analysis complete!') },
    onError:    (err)  => toast.error(err.response?.data?.error ?? 'Failed'),
  })

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-green-100 text-green-600
                        flex items-center justify-center">
          <CreditCard size={20} />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">
            Debt Manager
          </h1>
          <p className="text-sm text-slate-500">
            Analyse your debts and get an AI payoff strategy
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-6">

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

          {/* Debt rows */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-slate-900 dark:text-white">
                Your Debts
              </h3>
              <button
                type="button"
                onClick={() => append({ name: '', balance: '', interest_rate: '', emi: '' })}
                className="btn-secondary text-sm flex items-center gap-2"
              >
                <Plus size={15} />
                Add Debt
              </button>
            </div>

            {fields.map((field, index) => (
              <motion.div
                key={field.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-slate-50 dark:bg-slate-700/50
                           rounded-xl border border-slate-200 dark:border-slate-600"
              >
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div>
                    <label className="label">Debt Name</label>
                    <input
                      {...register(`debts.${index}.name`)}
                      placeholder="e.g. Personal Loan"
                      className={`input ${errors.debts?.[index]?.name ? 'input-error' : ''}`}
                    />
                    {errors.debts?.[index]?.name && (
                      <p className="text-xs text-danger mt-1">
                        {errors.debts[index].name.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="label">Balance (₹)</label>
                    <input
                      {...register(`debts.${index}.balance`)}
                      type="number"
                      placeholder="50000"
                      className={`input ${errors.debts?.[index]?.balance ? 'input-error' : ''}`}
                    />
                    {errors.debts?.[index]?.balance && (
                      <p className="text-xs text-danger mt-1">
                        {errors.debts[index].balance.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="label">Interest Rate (%)</label>
                    <input
                      {...register(`debts.${index}.interest_rate`)}
                      type="number"
                      step="0.1"
                      placeholder="18"
                      className="input"
                    />
                  </div>

                  <div>
                    <label className="label">Current EMI (₹)</label>
                    <input
                      {...register(`debts.${index}.emi`)}
                      type="number"
                      placeholder="2000"
                      className="input"
                    />
                  </div>
                </div>

                {fields.length > 1 && (
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className="mt-3 flex items-center gap-1 text-xs text-red-500
                               hover:text-red-700 transition-colors"
                  >
                    <Trash2 size={13} />
                    Remove
                  </button>
                )}
              </motion.div>
            ))}

            {errors.debts?.root && (
              <p className="text-xs text-danger">{errors.debts.root.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <Sparkles size={16} />
            {mutation.isPending ? 'Analysing...' : 'Analyse My Debt'}
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
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Debt',     value: formatCurrency(result.total_debt),     color: 'text-danger'  },
                { label: 'Total EMI',      value: formatCurrency(result.total_emi),      color: 'text-warning' },
                { label: 'Debt-to-Income', value: `${result.debt_to_income_ratio}%`,     color: result.debt_to_income_ratio > 40 ? 'text-danger' : 'text-success' },
                { label: 'Strategy',       value: result.recommended_strategy ?? '—',    color: 'text-primary' },
              ].map(({ label, value, color }) => (
                <div key={label} className="card-sm text-center">
                  <p className={`text-lg font-extrabold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {/* Debt breakdown */}
            {result.debt_details?.length > 0 && (
              <div className="card">
                <h3 className="font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <TrendingDown size={16} className="text-primary" />
                  Debt Breakdown
                </h3>
                <div className="space-y-3">
                  {result.debt_details.map((debt, i) => (
                    <div key={i} className="flex items-center justify-between
                                            p-3 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                      <div>
                        <p className="font-medium text-sm text-slate-900 dark:text-white">
                          {debt.name}
                        </p>
                        <p className="text-xs text-slate-500">
                          {debt.interest_rate}% interest · EMI {formatCurrency(debt.emi)}
                        </p>
                      </div>
                      <p className="font-bold text-danger">
                        {formatCurrency(debt.balance)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Advice */}
            {result.advice && (
              <div className="card border-l-4 border-primary">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={16} className="text-primary" />
                  <h3 className="font-bold text-slate-900 dark:text-white">
                    AI Payoff Strategy
                  </h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300
                              whitespace-pre-wrap leading-relaxed">
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