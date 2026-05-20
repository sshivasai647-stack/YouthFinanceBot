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
    principal:     z.coerce.number().min(1, 'Required'),  // was "balance" — fixed
    rate:          z.coerce.number().min(0),               // was "interest_rate" — fixed
    emi:           z.coerce.number().min(0),
  })).min(1, 'Add at least one debt'),
})

export default function DebtPage() {
  const [result, setResult] = useState(null)

  const { register, control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(debtSchema),
    defaultValues: {
      monthly_income: '',
      debts: [{ name: '', principal: '', rate: '', emi: '' }],
    },
  })

  const { fields, append, remove } = useFieldArray({ control, name: 'debts' })

  const mutation = useMutation({
    mutationFn: (data) =>
      // Backend DebtAnalyseSchema expects: { income, debts[{principal, rate, tenure, name, emi}], expenses }
      citizenApi.analyzeDebt({
        income:   data.monthly_income,
        expenses: 0,
        debts: data.debts.map(d => ({
          name:      d.name,
          principal: d.principal,
          rate:      d.rate,
          tenure:    36,       // sensible default; not shown in form
          emi:       d.emi || null,
        })),
      }),
    onSuccess: (res) => { setResult(res.data); toast.success('Debt analysis complete!') },
    onError:   (err) => toast.error(err.response?.data?.error ?? 'Failed'),
  })

  // Backend returns: { burden{}, debt_trap{}, repayment_plan{} }
  // burden: { dti_ratio, emi_burden_pct, status, classification, monthly_emi, total_debt }
  const burden       = result?.burden       ?? {}
  const trap         = result?.debt_trap    ?? {}
  const repayment    = result?.repayment_plan ?? {}

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-green-100 text-green-600 flex items-center justify-center">
          <CreditCard size={20} />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 dark:text-white">Debt Manager</h1>
          <p className="text-sm text-slate-500">Analyse your debts and get an AI payoff strategy</p>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-6">
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

          {/* Debt rows */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-slate-900 dark:text-white">Your Debts</h3>
              <button
                type="button"
                onClick={() => append({ name: '', principal: '', rate: '', emi: '' })}
                className="btn-secondary text-sm flex items-center gap-2"
              >
                <Plus size={15} /> Add Debt
              </button>
            </div>

            {fields.map((field, index) => (
              <motion.div
                key={field.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl border border-slate-200 dark:border-slate-600"
              >
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div>
                    <label className="label">Debt Name</label>
                    <input
                      {...register(`debts.${index}.name`)}
                      placeholder="Personal Loan"
                      className={`input ${errors.debts?.[index]?.name ? 'input-error' : ''}`}
                    />
                    {errors.debts?.[index]?.name && (
                      <p className="text-xs text-danger mt-1">{errors.debts[index].name.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="label">Balance / Principal (₹)</label>
                    <input
                      {...register(`debts.${index}.principal`)}
                      type="number"
                      placeholder="50000"
                      className={`input ${errors.debts?.[index]?.principal ? 'input-error' : ''}`}
                    />
                    {errors.debts?.[index]?.principal && (
                      <p className="text-xs text-danger mt-1">{errors.debts[index].principal.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="label">Interest Rate (%)</label>
                    <input
                      {...register(`debts.${index}.rate`)}
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
                    className="mt-3 flex items-center gap-1 text-xs text-red-500 hover:text-red-700 transition-colors"
                  >
                    <Trash2 size={13} /> Remove
                  </button>
                )}
              </motion.div>
            ))}

            {errors.debts?.root && <p className="text-xs text-danger">{errors.debts.root.message}</p>}
          </div>

          <button type="submit" disabled={mutation.isPending} className="btn-primary flex items-center gap-2">
            <Sparkles size={16} />
            {mutation.isPending ? 'Analysing...' : 'Analyse My Debt'}
          </button>
        </form>
      </div>

      {/* Result — mapped to actual backend response fields */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {/* Summary stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Debt',      value: formatCurrency(burden.total_debt),                               color: 'text-danger'   },
                { label: 'Monthly EMI',     value: formatCurrency(burden.monthly_emi),                              color: 'text-warning'  },
                { label: 'EMI Burden',      value: `${burden.emi_burden_pct ?? 0}%`,                                color: (burden.emi_burden_pct ?? 0) > 40 ? 'text-danger' : 'text-success' },
                { label: 'Status',          value: burden.classification ?? burden.status ?? '—',                   color: 'text-primary'  },
              ].map(({ label, value, color }) => (
                <div key={label} className="card-sm text-center">
                  <p className={`text-lg font-extrabold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>

            {/* Debt trap warning */}
            {trap.spiral_detected && (
              <div className="card bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800">
                <p className="font-semibold text-red-700 dark:text-red-400 mb-1">⚠️ Debt Trap Detected</p>
                <p className="text-sm text-slate-600 dark:text-slate-300">{trap.status}</p>
              </div>
            )}

            {/* Repayment plan */}
            {repayment && repayment.status !== 'error' && (
              <div className="card">
                <h3 className="font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <TrendingDown size={16} className="text-primary" />
                  AI Repayment Plan
                </h3>
                <div className="space-y-2 text-sm text-slate-700 dark:text-slate-300">
                  {repayment.strategy      && <p><span className="font-medium">Strategy:</span> {repayment.strategy}</p>}
                  {repayment.monthly_extra && <p><span className="font-medium">Suggested extra payment:</span> {formatCurrency(repayment.monthly_extra)}/month</p>}
                  {repayment.months_saved  && <p><span className="font-medium">Months saved:</span> {repayment.months_saved}</p>}
                  {repayment.advice        && <p className="mt-2 text-slate-500 whitespace-pre-wrap">{repayment.advice}</p>}
                  {/* Fallback: show full repayment object as JSON if fields are different */}
                  {!repayment.strategy && !repayment.advice && (
                    <pre className="text-xs bg-slate-100 dark:bg-slate-700 p-3 rounded-lg overflow-x-auto">
                      {JSON.stringify(repayment, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
