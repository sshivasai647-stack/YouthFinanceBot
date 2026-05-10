import { useQuery } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { useAuthStore } from '../../store/authStore'
import { formatCurrency, crisisColor } from '../../lib/utils'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  MessageCircle, Target, CreditCard, TrendingUp,
  AlertTriangle, ArrowRight, Sparkles
} from 'lucide-react'

const quickLinks = [
  { to: '/dashboard/chat',     icon: MessageCircle, label: 'AI Chat',      color: 'bg-purple-100 text-purple-600' },
  { to: '/dashboard/goals',    icon: Target,        label: 'Goals',        color: 'bg-blue-100 text-blue-600'   },
  { to: '/dashboard/debt',     icon: CreditCard,    label: 'Debt',         color: 'bg-green-100 text-green-600' },
  { to: '/dashboard/spending', icon: TrendingUp,    label: 'Spending',     color: 'bg-yellow-100 text-yellow-600'},
  { to: '/dashboard/betting',  icon: AlertTriangle, label: 'Betting Risk', color: 'bg-red-100 text-red-600'     },
]

export default function DashboardHome() {
  const { user } = useAuthStore()

  const { data: profile } = useQuery({
    queryKey: ['citizen-profile'],
    queryFn:  () => citizenApi.profile().then((r) => r.data),
  })

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">
      {/* Welcome */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card bg-gradient-to-r from-primary to-blue-500 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-primary-100 text-sm mb-1">Good day 👋</p>
            <h1 className="text-2xl font-extrabold">
              {user?.full_name?.split(' ')[0]}
            </h1>
            <p className="text-primary-100 text-sm mt-1">
              Your financial wellness journey continues
            </p>
          </div>
          <Sparkles size={40} className="text-white/30" />
        </div>

        {/* Crisis badge */}
        {profile?.crisis_level && profile.crisis_level !== 'NONE' && (
          <div className={`mt-4 inline-flex items-center gap-2 px-3 py-1.5
                           rounded-lg text-xs font-semibold
                           ${crisisColor(profile.crisis_level)}`}>
            <AlertTriangle size={12} />
            Crisis Level: {profile.crisis_level}
          </div>
        )}
      </motion.div>

      {/* Quick links */}
      <div>
        <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4">
          Quick Access
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {quickLinks.map(({ to, icon: Icon, label, color }, i) => (
            <motion.div
              key={to}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
            >
              <Link
                to={to}
                className="card-sm flex flex-col items-center gap-3 text-center
                           hover:scale-105 transition-transform cursor-pointer"
              >
                <div className={`w-12 h-12 rounded-xl ${color}
                                 flex items-center justify-center`}>
                  <Icon size={22} />
                </div>
                <span className="text-xs font-semibold text-slate-700
                                 dark:text-slate-300">
                  {label}
                </span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Profile summary */}
      {profile && (
        <div className="grid md:grid-cols-3 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <p className="text-xs text-slate-500 mb-1">Monthly Income</p>
            <p className="text-2xl font-extrabold text-slate-900 dark:text-white">
              {profile.monthly_income
                ? formatCurrency(profile.monthly_income)
                : '—'}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <p className="text-xs text-slate-500 mb-1">Total Debt</p>
            <p className="text-2xl font-extrabold text-danger">
              {profile.total_debt
                ? formatCurrency(profile.total_debt)
                : '—'}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <p className="text-xs text-slate-500 mb-1">Savings Goal</p>
            <p className="text-2xl font-extrabold text-success">
              {profile.savings_goal
                ? formatCurrency(profile.savings_goal)
                : '—'}
            </p>
          </motion.div>
        </div>
      )}

      {/* Start chat CTA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card border-2 border-dashed border-primary-200
                   dark:border-primary-800 bg-primary-50 dark:bg-primary-900/10"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white mb-1">
              Chat with YF-AI
            </h3>
            <p className="text-sm text-slate-500">
              Ask anything about budgeting, debt, investments, or government schemes.
            </p>
          </div>
          <Link
            to="/dashboard/chat"
            className="btn-primary flex items-center gap-2 flex-shrink-0 ml-4"
          >
            Start Chat
            <ArrowRight size={16} />
          </Link>
        </div>
      </motion.div>
    </div>
  )
}