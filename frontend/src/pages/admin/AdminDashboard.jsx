import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Database, CheckCircle2, XCircle, RefreshCw,
  Users, MessageCircle, AlertTriangle, Zap, Table2
} from 'lucide-react'

function StatusDot({ status }) {
  if (status === 'connected') return (
    <span className="relative flex h-3 w-3">
      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
      <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500" />
    </span>
  )
  if (status === 'disconnected' || status === 'error') return (
    <span className="relative flex h-3 w-3">
      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
    </span>
  )
  return (
    <span className="relative flex h-3 w-3">
      <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-400 animate-pulse" />
    </span>
  )
}

export default function AdminDashboard() {
  const {
    data: db,
    isLoading: dbLoading,
    isError: dbError,
    refetch: refetchDb,
    isFetching: dbFetching,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ['admin-db-status'],
    queryFn: () => adminApi.dbStatus().then((r) => r.data),
    refetchInterval: 30_000,
    retry: false,
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: () => adminApi.stats().then((r) => r.data),
    refetchInterval: 60_000,
  })

  const dbStatus = dbError ? 'disconnected' : db?.status ?? 'checking'
  const isConnected = dbStatus === 'connected'
  const lastChecked = dataUpdatedAt
    ? new Date(dataUpdatedAt).toLocaleTimeString()
    : '—'

  const statCards = [
    { label: 'Total Users',         value: stats?.users_total ?? '—',            icon: Users,          color: 'text-blue-600',   bg: 'bg-blue-50'   },
    { label: 'Weekly Active',        value: stats?.weekly_active_users ?? '—',    icon: Zap,            color: 'text-purple-600', bg: 'bg-purple-50' },
    { label: 'Crisis Alerts (24h)', value: stats?.crisis_alerts_last_24h ?? '—', icon: AlertTriangle,  color: 'text-red-600',    bg: 'bg-red-50'    },
    { label: 'Chats Today',          value: stats?.chat_sessions_today ?? '—',    icon: MessageCircle,  color: 'text-green-600',  bg: 'bg-green-50'  },
  ]

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">
          Admin Dashboard
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Platform health and live system status
        </p>
      </div>

      {/* ── MongoDB Status Card ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`card border-2 ${
          isConnected
            ? 'border-green-200 dark:border-green-800'
            : dbStatus === 'checking'
            ? 'border-amber-200 dark:border-amber-800'
            : 'border-red-200 dark:border-red-800'
        }`}
      >
        {/* Card header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              isConnected ? 'bg-green-100 text-green-600' :
              dbStatus === 'checking' ? 'bg-amber-100 text-amber-600' :
              'bg-red-100 text-red-600'
            }`}>
              <Database size={20} />
            </div>
            <div>
              <h2 className="font-bold text-slate-900 dark:text-white text-base">
                MongoDB Connection
              </h2>
              <p className="text-xs text-slate-500">Last checked: {lastChecked}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <StatusDot status={dbStatus} />
              <span className={`text-sm font-semibold capitalize ${
                isConnected ? 'text-green-600' :
                dbStatus === 'checking' ? 'text-amber-600' :
                'text-red-600'
              }`}>
                {dbLoading ? 'Checking…' : dbStatus}
              </span>
            </div>
            <button
              onClick={() => refetchDb()}
              disabled={dbFetching}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700
                         text-slate-500 transition-colors disabled:opacity-40"
              title="Refresh status"
            >
              <RefreshCw size={16} className={dbFetching ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {/* Status body */}
        <AnimatePresence mode="wait">
          {dbLoading && (
            <motion.div key="loading"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex items-center gap-3 py-3 text-slate-500 text-sm"
            >
              <RefreshCw size={14} className="animate-spin" />
              Pinging database…
            </motion.div>
          )}

          {!dbLoading && isConnected && db && (
            <motion.div key="connected"
              initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Version badge */}
              <div className="flex flex-wrap gap-3">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full
                                 bg-green-100 text-green-700 text-xs font-semibold">
                  <CheckCircle2 size={12} />
                  MongoDB v{db.mongo_version}
                </span>
              </div>

              {/* Collections table */}
              {db.collections && Object.keys(db.collections).length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2 text-slate-600 dark:text-slate-400">
                    <Table2 size={14} />
                    <span className="text-xs font-semibold uppercase tracking-wide">
                      Collections ({Object.keys(db.collections).length})
                    </span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {Object.entries(db.collections)
                      .sort(([, a], [, b]) => b - a)
                      .map(([name, count]) => (
                        <div key={name}
                          className="flex items-center justify-between px-3 py-2
                                     rounded-lg bg-slate-50 dark:bg-slate-700/50
                                     border border-slate-200 dark:border-slate-600"
                        >
                          <span className="text-xs font-medium text-slate-700
                                           dark:text-slate-300 truncate max-w-[70%]">
                            {name}
                          </span>
                          <span className="text-xs font-bold text-slate-500
                                           dark:text-slate-400 ml-2 flex-shrink-0">
                            {count.toLocaleString()}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {!dbLoading && !isConnected && (
            <motion.div key="error"
              initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              className="flex items-start gap-3 p-4 rounded-xl bg-red-50
                         dark:bg-red-900/10 border border-red-200 dark:border-red-800"
            >
              <XCircle size={18} className="text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-800 dark:text-red-300">
                  Cannot reach MongoDB
                </p>
                <p className="text-xs text-red-600 dark:text-red-400 mt-0.5">
                  {db?.error ?? 'Connection timed out. Check MONGO_URI and database availability.'}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* ── Platform Stats ── */}
      <div>
        <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">
          Platform Overview
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {statCards.map(({ label, value, icon: Icon, color, bg }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className="card-sm"
            >
              <div className={`w-9 h-9 rounded-xl ${bg} ${color}
                               flex items-center justify-center mb-3`}>
                <Icon size={18} />
              </div>
              {statsLoading ? (
                <div className="h-7 w-12 rounded bg-slate-200 dark:bg-slate-600 animate-pulse mb-1" />
              ) : (
                <p className="text-2xl font-extrabold text-slate-900 dark:text-white">
                  {value}
                </p>
              )}
              <p className="text-xs text-slate-500 mt-0.5">{label}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
