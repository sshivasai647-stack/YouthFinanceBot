import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { useAuthStore } from '../../store/authStore'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { formatCurrency, crisisColor, getInitials } from '../../lib/utils'
import { User, Save, Shield, CreditCard, Target } from 'lucide-react'
import toast from 'react-hot-toast'

const schema = z.object({
  monthly_income:   z.coerce.number().min(0).optional(),
  monthly_expenses: z.coerce.number().min(0).optional(),
  total_debt:       z.coerce.number().min(0).optional(),
  savings_goal:     z.coerce.number().min(0).optional(),
  emergency_fund:   z.coerce.number().min(0).optional(),
})

export default function ProfilePage() {
  const { user } = useAuthStore()
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)

  const { data: profile, isLoading } = useQuery({
    queryKey: ['citizen-profile'],
    queryFn:  () => citizenApi.profile().then((r) => r.data),
  })

  const { register, handleSubmit, reset } = useForm({
    resolver: zodResolver(schema),
    values: profile ?? {},
  })

  const mutation = useMutation({
    mutationFn: (data) => citizenApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['citizen-profile'])
      toast.success('Profile updated!')
      setEditing(false)
    },
    onError: (err) => toast.error(err.response?.data?.error ?? 'Update failed'),
  })

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent
                          rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-500">Loading profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-primary text-white flex items-center
                          justify-center text-2xl font-bold">
            {getInitials(user?.full_name)}
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              {user?.full_name}
            </h1>
            <p className="text-sm text-slate-500">{user?.email}</p>
            <p className="text-xs text-slate-400 mt-0.5">
              {user?.phone} · Age {user?.age}
            </p>
          </div>
        </div>

        {profile?.crisis_level && profile.crisis_level !== 'NONE' && (
          <div className={`px-3 py-1.5 rounded-lg text-xs font-semibold
                           ${crisisColor(profile.crisis_level)}`}>
            {profile.crisis_level}
          </div>
        )}
      </div>

      {/* Account info */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Shield size={16} className="text-primary" />
          <h2 className="font-bold text-slate-900 dark:text-white">
            Account Details
          </h2>
        </div>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-500 mb-1">Role</p>
            <p className="font-medium text-slate-900 dark:text-white capitalize">
              {user?.role}
            </p>
          </div>
          <div>
            <p className="text-slate-500 mb-1">Joined</p>
            <p className="font-medium text-slate-900 dark:text-white">
              {new Date(user?.created_at).toLocaleDateString('en-IN', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
              })}
            </p>
          </div>
          {profile?.assigned_counsellor && (
            <div>
              <p className="text-slate-500 mb-1">Assigned Counsellor</p>
              <p className="font-medium text-slate-900 dark:text-white">
                {profile.assigned_counsellor}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Financial overview */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <CreditCard size={16} className="text-primary" />
            <h2 className="font-bold text-slate-900 dark:text-white">
              Financial Overview
            </h2>
          </div>
          <button
            onClick={() => {
              setEditing(!editing)
              if (!editing) reset(profile)
            }}
            className="btn-secondary text-sm"
          >
            {editing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))}>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              { name: 'monthly_income',   label: 'Monthly Income',   icon: Target },
              { name: 'monthly_expenses', label: 'Monthly Expenses', icon: Target },
              { name: 'total_debt',       label: 'Total Debt',       icon: Target },
              { name: 'savings_goal',     label: 'Savings Goal',     icon: Target },
              { name: 'emergency_fund',   label: 'Emergency Fund',   icon: Target },
            ].map(({ name, label, icon: Icon }) => (
              <div key={name}>
                <label className="label flex items-center gap-2">
                  <Icon size={13} className="text-slate-400" />
                  {label}
                </label>
                {editing ? (
                  <input
                    {...register(name)}
                    type="number"
                    placeholder="0"
                    className="input"
                  />
                ) : (
                  <p className="text-lg font-bold text-slate-900 dark:text-white">
                    {profile?.[name]
                      ? formatCurrency(profile[name])
                      : '—'}
                  </p>
                )}
              </div>
            ))}
          </div>

          {editing && (
            <div className="mt-6 flex gap-3">
              <button
                type="submit"
                disabled={mutation.isPending}
                className="btn-primary flex items-center gap-2"
              >
                <Save size={16} />
                {mutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}
        </form>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Chats',       value: profile?.chat_count ?? 0 },
          { label: 'Goals Set',   value: profile?.goals_count ?? 0 },
          { label: 'Debts',       value: profile?.debts_count ?? 0 },
          { label: 'Last Active', value: 'Today' },
        ].map(({ label, value }) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card-sm text-center"
          >
            <p className="text-2xl font-extrabold text-primary">{value}</p>
            <p className="text-xs text-slate-500 mt-1">{label}</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}