import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { motion } from 'framer-motion'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import {
  BarChart2, Zap, AlertTriangle, Download,
  Clock, RefreshCw, Activity, Brain
} from 'lucide-react'
import toast from 'react-hot-toast'

/* ── helpers ── */
function shortDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })
}

function StatCard({ icon: Icon, label, value, sub, color, loading }) {
  return (
    <div className="card-sm">
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-3 ${color}`}>
        <Icon size={18} />
      </div>
      {loading ? (
        <div className="h-7 w-16 rounded bg-slate-200 dark:bg-slate-600 animate-pulse mb-1" />
      ) : (
        <p className="text-2xl font-extrabold text-slate-900 dark:text-white">{value ?? '—'}</p>
      )}
      <p className="text-xs text-slate-500 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700
                    rounded-xl px-4 py-3 shadow-lg text-xs">
      <p className="font-semibold text-slate-700 dark:text-slate-300 mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }} className="font-medium">
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  )
}

export default function AdminAnalyticsPage() {
  /* ── Data queries ── */
  const { data: trends, isLoading: tLoading, refetch: refetchTrends } = useQuery({
    queryKey: ['admin-trends'],
    queryFn:  () => adminApi.moduleAnalytics().then(() => null) // just warm; use trends endpoint
      .catch(() => null),
    enabled: false,   // we use the real trends query below
  })

  const { data: trendsData, isLoading: trendsLoading } = useQuery({
    queryKey: ['admin-trends-real'],
    queryFn:  () => fetch('/api/admin/analytics/trends', { credentials: 'include' })
                      .then((r) => r.json()),
    refetchInterval: 120_000,
  })

  const { data: modulesData, isLoading: modulesLoading } = useQuery({
    queryKey: ['admin-modules'],
    queryFn:  () => adminApi.moduleAnalytics().then((r) => r.data),
    refetchInterval: 120_000,
  })

  const { data: aiData, isLoading: aiLoading } = useQuery({
    queryKey: ['admin-ai-usage'],
    queryFn:  () => adminApi.aiUsage().then((r) => r.data),
    refetchInterval: 60_000,
  })

  /* ── Derived data ── */
  const weeklyChartData = (trendsData?.weeks ?? []).map((w) => ({
    week: shortDate(w.week_start),
    'Active Logins': w.weekly_active_logins,
    'Crisis Flags':  w.flagged_mental_health_events,
  }))

  const moduleChartData = Object.entries(modulesData?.module_hits ?? {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([mod, count]) => ({ module: mod, Requests: count }))

  /* ── Excel export ── */
  async function handleExport() {
    try {
      const res = await adminApi.exportExcel()
      const url = URL.createObjectURL(new Blob([res.data]))
      const a   = document.createElement('a')
      a.href    = url
      a.download = 'youthfinancebot_analytics.xlsx'
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Export downloaded')
    } catch {
      toast.error('Export failed')
    }
  }

  const anyLoading = trendsLoading || modulesLoading || aiLoading

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">Analytics</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Platform usage trends · last 8 weeks
          </p>
        </div>
        <button
          onClick={handleExport}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <Download size={14} />
          Export Excel
        </button>
      </div>

      {/* ── AI Usage stat cards ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        <StatCard
          icon={Brain}
          label="AI Calls (7d)"
          value={aiData?.calls}
          color="bg-purple-100 text-purple-600"
          loading={aiLoading}
        />
        <StatCard
          icon={Clock}
          label="Avg Latency"
          value={aiData?.avg_latency_ms != null ? `${aiData.avg_latency_ms} ms` : '—'}
          color="bg-blue-100 text-blue-600"
          loading={aiLoading}
        />
        <StatCard
          icon={AlertTriangle}
          label="LLM Errors (7d)"
          value={aiData?.llm_errors}
          color="bg-red-100 text-red-600"
          loading={aiLoading}
        />
        <StatCard
          icon={Activity}
          label="Module Types"
          value={Object.keys(modulesData?.module_hits ?? {}).length || '—'}
          sub="tracked endpoints"
          color="bg-green-100 text-green-600"
          loading={modulesLoading}
        />
      </motion.div>

      {/* ── Weekly trend chart ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.08 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-100 text-indigo-600
                            flex items-center justify-center">
              <Zap size={18} />
            </div>
            <div>
              <h2 className="font-bold text-slate-900 dark:text-white text-base">
                Weekly Activity
              </h2>
              <p className="text-xs text-slate-500">Active logins &amp; crisis flags · last 8 weeks</p>
            </div>
          </div>
          {trendsLoading && <RefreshCw size={14} className="animate-spin text-slate-400" />}
        </div>

        {trendsLoading ? (
          <div className="h-52 rounded-xl bg-slate-100 dark:bg-slate-700 animate-pulse" />
        ) : weeklyChartData.length === 0 ? (
          <div className="h-52 flex items-center justify-center text-slate-400 text-sm">
            No trend data yet
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={weeklyChartData}
              margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorLogins" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorCrisis" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: 12, paddingTop: 12 }}
                formatter={(v) => <span className="text-slate-600 dark:text-slate-300">{v}</span>}
              />
              <Area
                type="monotone"
                dataKey="Active Logins"
                stroke="#6366f1"
                strokeWidth={2}
                fill="url(#colorLogins)"
                dot={{ r: 3, fill: '#6366f1' }}
                activeDot={{ r: 5 }}
              />
              <Area
                type="monotone"
                dataKey="Crisis Flags"
                stroke="#ef4444"
                strokeWidth={2}
                fill="url(#colorCrisis)"
                dot={{ r: 3, fill: '#ef4444' }}
                activeDot={{ r: 5 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </motion.div>

      {/* ── Module usage bar chart ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.14 }}
        className="card"
      >
        <div className="flex items-center gap-3 mb-5">
          <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-600
                          flex items-center justify-center">
            <BarChart2 size={18} />
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-white text-base">
              API Module Usage
            </h2>
            <p className="text-xs text-slate-500">Request hits per endpoint group · last 30 days</p>
          </div>
          {modulesLoading && <RefreshCw size={14} className="animate-spin text-slate-400 ml-auto" />}
        </div>

        {modulesLoading ? (
          <div className="h-52 rounded-xl bg-slate-100 dark:bg-slate-700 animate-pulse" />
        ) : moduleChartData.length === 0 ? (
          <div className="h-52 flex items-center justify-center text-slate-400 text-sm">
            No module data yet — audit logs are empty
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={moduleChartData}
              margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="module" tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar
                dataKey="Requests"
                fill="#6366f1"
                radius={[6, 6, 0, 0]}
                maxBarSize={48}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </motion.div>

      {/* ── AI Usage breakdown ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <div className="flex items-center gap-3 mb-5">
          <div className="w-9 h-9 rounded-xl bg-purple-100 text-purple-600
                          flex items-center justify-center">
            <Brain size={18} />
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-white text-base">
              AI / LLM Usage
            </h2>
            <p className="text-xs text-slate-500">Groq API performance · last 7 days</p>
          </div>
        </div>

        {aiLoading ? (
          <div className="grid md:grid-cols-3 gap-4">
            {[0,1,2].map(i => (
              <div key={i} className="h-20 rounded-xl bg-slate-100 dark:bg-slate-700 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {[
              {
                label: 'Total AI Calls',
                value: aiData?.calls ?? 0,
                color: 'text-purple-600',
                bg:    'bg-purple-50 dark:bg-purple-900/10 border-purple-200 dark:border-purple-800',
              },
              {
                label: 'Avg Response Time',
                value: `${aiData?.avg_latency_ms ?? 0} ms`,
                color: aiData?.avg_latency_ms > 3000 ? 'text-red-600' : 'text-blue-600',
                bg:    'bg-blue-50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800',
              },
              {
                label: 'Failed Calls',
                value: aiData?.llm_errors ?? 0,
                color: (aiData?.llm_errors ?? 0) > 0 ? 'text-red-600' : 'text-green-600',
                bg:    (aiData?.llm_errors ?? 0) > 0
                  ? 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800'
                  : 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800',
              },
            ].map(({ label, value, color, bg }) => (
              <div key={label} className={`rounded-xl border p-5 ${bg}`}>
                <p className={`text-3xl font-extrabold ${color}`}>{value}</p>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{label}</p>
                <p className="text-xs text-slate-400 mt-0.5">last 7 days</p>
              </div>
            ))}
          </div>
        )}

        {/* Health bar */}
        {!aiLoading && (aiData?.calls ?? 0) > 0 && (
          <div className="mt-5">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-1.5">
              <span>Success rate</span>
              <span className="font-semibold">
                {(((aiData.calls - aiData.llm_errors) / aiData.calls) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{
                  width: `${((aiData.calls - aiData.llm_errors) / aiData.calls) * 100}%`
                }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full"
              />
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
