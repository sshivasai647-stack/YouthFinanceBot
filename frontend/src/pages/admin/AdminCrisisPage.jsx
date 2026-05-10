import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  AlertTriangle, ShieldAlert, CheckCircle2, Clock, RefreshCw,
  ChevronLeft, ChevronRight, Filter, ChevronDown, ChevronUp,
  User, Mail, Send, Undo2, MessageSquare, X
} from 'lucide-react'

/* ── API ── */
const api = axios.create({ baseURL: '/api/admin', withCredentials: true })
const crisisApi = {
  list:       (p) => api.get('/crisis', { params: p }).then((r) => r.data),
  escalate:   (id, note) => api.patch(`/crisis/${id}/escalate`, { note }),
  deescalate: (id) => api.delete(`/crisis/${id}/escalate`),
}

/* ── Severity config ── */
const SEVERITY = {
  suicidal:      { label: 'Suicidal',      color: 'bg-red-100    text-red-700    border-red-200',    dot: 'bg-red-500',    rank: 4 },
  shame_despair: { label: 'Shame/Despair', color: 'bg-orange-100 text-orange-700 border-orange-200', dot: 'bg-orange-500', rank: 3 },
  crisis:        { label: 'Crisis',        color: 'bg-orange-100 text-orange-700 border-orange-200', dot: 'bg-orange-400', rank: 3 },
  at_risk:       { label: 'At Risk',       color: 'bg-yellow-100 text-yellow-700 border-yellow-200', dot: 'bg-yellow-500', rank: 2 },
  mild:          { label: 'Mild',          color: 'bg-blue-100   text-blue-700   border-blue-200',   dot: 'bg-blue-400',   rank: 1 },
  unknown:       { label: 'Unknown',       color: 'bg-slate-100  text-slate-600  border-slate-200',   dot: 'bg-slate-400',  rank: 0 },
}
function sev(level) { return SEVERITY[level] ?? SEVERITY.unknown }

function SeverityBadge({ level }) {
  const s = sev(level)
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs
                      font-semibold border ${s.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  )
}

function fmtTs(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  const secs = Math.floor((Date.now() - d) / 1000)
  const rel =
    secs < 60    ? `${secs}s ago` :
    secs < 3600  ? `${Math.floor(secs / 60)}m ago` :
    secs < 86400 ? `${Math.floor(secs / 3600)}h ago` :
                   `${Math.floor(secs / 86400)}d ago`
  return { full: d.toLocaleString('en-IN', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' }), rel }
}

/* ── Escalate modal ── */
function EscalateModal({ entry, onClose, onDone }) {
  const [note, setNote] = useState('')
  const qc = useQueryClient()
  const mut = useMutation({
    mutationFn: () => crisisApi.escalate(entry.id, note),
    onSuccess: () => {
      toast.success('Escalated — user has been notified')
      qc.invalidateQueries({ queryKey: ['admin-crisis'] })
      onDone()
    },
    onError: (e) => toast.error(e.response?.data?.error ?? 'Escalation failed'),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 12 }}
        className="relative bg-white dark:bg-slate-800 rounded-2xl shadow-2xl
                   w-full max-w-md p-6 space-y-4"
      >
        <button onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors">
          <X size={18} />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
            <ShieldAlert size={20} className="text-red-600" />
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-white">Escalate to Counsellor</h2>
            <p className="text-xs text-slate-500">This will notify the user immediately</p>
          </div>
        </div>

        {/* User info */}
        <div className="rounded-xl bg-slate-50 dark:bg-slate-700/50 px-4 py-3 space-y-1">
          <div className="flex items-center gap-2 text-sm">
            <User size={13} className="text-slate-400" />
            <span className="font-medium text-slate-700 dark:text-slate-300">{entry.user_name}</span>
            <SeverityBadge level={entry.crisis_level} />
          </div>
          {entry.user_email && (
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Mail size={11} />
              {entry.user_email}
            </div>
          )}
        </div>

        {/* Note field */}
        <div>
          <label className="label">Internal note (optional)</label>
          <textarea
            className="input w-full resize-none"
            rows={3}
            placeholder="Reason for escalation, context…"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            maxLength={500}
          />
          <p className="text-xs text-slate-400 mt-0.5 text-right">{note.length}/500</p>
        </div>

        <div className="flex gap-3 pt-1">
          <button onClick={onClose} className="btn-secondary flex-1 text-sm">Cancel</button>
          <button
            onClick={() => mut.mutate()}
            disabled={mut.isPending}
            className="btn-primary flex-1 flex items-center justify-center gap-2 text-sm"
          >
            {mut.isPending
              ? <RefreshCw size={14} className="animate-spin" />
              : <Send size={14} />}
            Escalate &amp; Notify
          </button>
        </div>
      </motion.div>
    </div>
  )
}

/* ── Main page ── */
const PAGE_SIZES = [25, 50, 100]

export default function AdminCrisisPage() {
  const qc = useQueryClient()

  const [level,    setLevel]    = useState('all')
  const [status,   setStatus]   = useState('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo,   setDateTo]   = useState('')
  const [showDate, setShowDate] = useState(false)
  const [page,     setPage]     = useState(1)
  const [limit,    setLimit]    = useState(50)
  const [committed, setCommitted] = useState({ level: 'all', status: 'all', dateFrom: '', dateTo: '' })

  const [escalateTarget, setEscalateTarget] = useState(null)

  function apply() {
    setCommitted({ level, status, dateFrom, dateTo })
    setPage(1)
  }
  function clear() {
    setLevel('all'); setStatus('all'); setDateFrom(''); setDateTo('')
    setCommitted({ level: 'all', status: 'all', dateFrom: '', dateTo: '' })
    setPage(1)
  }

  const params = {
    page, limit,
    ...(committed.level  !== 'all' ? { level:     committed.level }    : {}),
    ...(committed.status !== 'all' ? { status:    committed.status }   : {}),
    ...(committed.dateFrom         ? { date_from: committed.dateFrom } : {}),
    ...(committed.dateTo           ? { date_to:   committed.dateTo }   : {}),
  }

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['admin-crisis', params],
    queryFn:  () => crisisApi.list(params),
    keepPreviousData: true,
    refetchInterval: 60_000,
  })

  const deescalateMut = useMutation({
    mutationFn: (id) => crisisApi.deescalate(id),
    onSuccess: () => {
      toast.success('Re-opened')
      qc.invalidateQueries({ queryKey: ['admin-crisis'] })
    },
    onError: (e) => toast.error(e.response?.data?.error ?? 'Failed'),
  })

  const entries    = data?.entries    ?? []
  const total      = data?.total      ?? 0
  const totalPages = data?.pages      ?? 1
  const summary    = data?.summary    ?? {}
  const allLevels  = data?.all_levels ?? []
  const activeFilters = committed.level !== 'all' || committed.status !== 'all' || committed.dateFrom || committed.dateTo

  const statCards = [
    { icon: AlertTriangle, label: 'Total Flagged', value: summary.total_flagged, color: 'bg-red-100 text-red-600' },
    { icon: ShieldAlert,   label: 'Suicidal',      value: summary.suicidal,      color: 'bg-red-100 text-red-700' },
    { icon: Clock,         label: 'Open',           value: summary.open,          color: 'bg-amber-100 text-amber-700' },
    { icon: CheckCircle2,  label: 'Escalated',      value: summary.escalated,     color: 'bg-green-100 text-green-700' },
  ]

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">Crisis Flags</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Flagged mental health check-ins requiring admin attention
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700
                     text-slate-500 transition-colors"
        >
          <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Alert banner if any suicidal flags */}
      {!isLoading && (summary.suicidal ?? 0) > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-4 py-3 rounded-xl
                     bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-700"
        >
          <ShieldAlert size={16} className="text-red-600 flex-shrink-0" />
          <p className="text-sm font-semibold text-red-800 dark:text-red-300">
            {summary.suicidal} suicidal-level flag{summary.suicidal !== 1 ? 's' : ''} on record — review and escalate immediately
          </p>
        </motion.div>
      )}

      {/* Stat cards */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {statCards.map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="card-sm">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center mb-3 ${color}`}>
              <Icon size={18} />
            </div>
            {isLoading ? (
              <div className="h-7 w-12 rounded bg-slate-200 dark:bg-slate-600 animate-pulse mb-1" />
            ) : (
              <p className="text-2xl font-extrabold text-slate-900 dark:text-white">{value ?? 0}</p>
            )}
            <p className="text-xs text-slate-500 mt-0.5">{label}</p>
          </div>
        ))}
      </motion.div>

      {/* Filter bar */}
      <div className="card p-4 space-y-3">
        <div className="flex flex-wrap gap-3">
          {/* Severity filter */}
          <select className="input w-44" value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="all">All severities</option>
            {allLevels.map((l) => (
              <option key={l} value={l}>{sev(l).label} ({l})</option>
            ))}
          </select>

          {/* Status filter */}
          <select className="input w-40" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="all">All statuses</option>
            <option value="open">Open only</option>
            <option value="escalated">Escalated only</option>
          </select>

          {/* Date toggle */}
          <button
            onClick={() => setShowDate((v) => !v)}
            className={`btn-secondary flex items-center gap-2 text-sm
                        ${showDate ? 'bg-slate-200 dark:bg-slate-600' : ''}`}
          >
            <Filter size={13} />
            Date range
            {showDate ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>

          <button onClick={apply} className="btn-primary text-sm px-4">Apply</button>
          {activeFilters && (
            <button onClick={clear}
              className="text-sm text-slate-500 hover:text-red-600 underline transition-colors">
              Clear
            </button>
          )}
        </div>

        <AnimatePresence>
          {showDate && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.16 }}
              className="overflow-hidden"
            >
              <div className="flex flex-wrap gap-4 pt-1">
                <div>
                  <label className="label">From</label>
                  <input type="datetime-local" className="input"
                    value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
                </div>
                <div>
                  <label className="label">To</label>
                  <input type="datetime-local" className="input"
                    value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/60 border-b
                             border-slate-200 dark:border-slate-700">
                {['Flagged At', 'User', 'Severity', 'Status', 'Actions'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold
                                         text-slate-500 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700/60">
              {isLoading ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i}>
                    {[0,1,2,3,4].map((c) => (
                      <td key={c} className="px-4 py-4">
                        <div className="h-4 rounded bg-slate-100 dark:bg-slate-700 animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : entries.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-20 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-400">
                      <CheckCircle2 size={36} strokeWidth={1.2} />
                      <p className="text-sm font-medium">No crisis flags match the current filters</p>
                      {activeFilters && (
                        <button onClick={clear}
                          className="text-xs text-indigo-600 underline">Clear filters</button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : entries.map((entry) => {
                const ts = fmtTs(entry.created_at)
                return (
                  <tr key={entry.id}
                      className={`transition-colors hover:bg-slate-50 dark:hover:bg-slate-700/30
                                  ${sev(entry.crisis_level).rank >= 3
                                    ? 'border-l-2 border-red-400'
                                    : ''}`}>
                    {/* Timestamp */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                        {ts.full}
                      </p>
                      <p className="text-xs text-slate-400">{ts.rel}</p>
                    </td>

                    {/* User */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-indigo-100 dark:bg-indigo-900/30
                                        flex items-center justify-center flex-shrink-0">
                          <span className="text-xs font-bold text-indigo-600">
                            {(entry.user_name?.[0] ?? '?').toUpperCase()}
                          </span>
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 truncate max-w-[140px]">
                            {entry.user_name}
                          </p>
                          <p className="text-xs text-slate-400 truncate max-w-[140px]">
                            {entry.user_email || entry.user_id}
                          </p>
                        </div>
                      </div>
                    </td>

                    {/* Severity */}
                    <td className="px-4 py-3">
                      <SeverityBadge level={entry.crisis_level} />
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      {entry.escalated ? (
                        <div>
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full
                                           text-xs font-semibold bg-green-100 text-green-700">
                            <CheckCircle2 size={10} />
                            Escalated
                          </span>
                          {entry.note && (
                            <div className="flex items-start gap-1 mt-1 text-xs text-slate-500 max-w-[160px]">
                              <MessageSquare size={10} className="flex-shrink-0 mt-0.5" />
                              <span className="truncate">{entry.note}</span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full
                                         text-xs font-semibold bg-amber-100 text-amber-700">
                          <Clock size={10} />
                          Open
                        </span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {!entry.escalated ? (
                          <button
                            onClick={() => setEscalateTarget(entry)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                                       bg-red-600 hover:bg-red-700 text-white text-xs font-semibold
                                       transition-colors"
                          >
                            <Send size={11} />
                            Escalate
                          </button>
                        ) : (
                          <button
                            onClick={() => deescalateMut.mutate(entry.id)}
                            disabled={deescalateMut.isPending}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                                       bg-slate-100 hover:bg-slate-200 text-slate-700
                                       text-xs font-semibold transition-colors"
                          >
                            {deescalateMut.isPending
                              ? <RefreshCw size={11} className="animate-spin" />
                              : <Undo2 size={11} />}
                            Re-open
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination footer */}
        {!isLoading && total > 0 && (
          <div className="flex items-center justify-between px-4 py-3
                          border-t border-slate-200 dark:border-slate-700
                          bg-slate-50 dark:bg-slate-800/40">
            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span>
                {((page - 1) * limit) + 1}–{Math.min(page * limit, total)} of {total.toLocaleString()}
              </span>
              <select className="input !py-1 !text-xs w-20" value={limit}
                onChange={(e) => { setLimit(Number(e.target.value)); setPage(1) }}>
                {PAGE_SIZES.map((s) => <option key={s} value={s}>{s} / page</option>)}
              </select>
            </div>
            <div className="flex items-center gap-1">
              <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}
                className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700
                           disabled:opacity-30 transition-colors">
                <ChevronLeft size={15} />
              </button>
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                let p = totalPages <= 7 ? i + 1
                      : page <= 4      ? i + 1
                      : page >= totalPages - 3 ? totalPages - 6 + i
                      : page - 3 + i
                return (
                  <button key={p} onClick={() => setPage(p)}
                    className={`w-7 h-7 rounded-lg text-xs font-medium transition-colors
                                ${p === page ? 'bg-indigo-600 text-white'
                                             : 'hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300'}`}>
                    {p}
                  </button>
                )
              })}
              <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700
                           disabled:opacity-30 transition-colors">
                <ChevronRight size={15} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Escalate modal */}
      <AnimatePresence>
        {escalateTarget && (
          <EscalateModal
            entry={escalateTarget}
            onClose={() => setEscalateTarget(null)}
            onDone={() => setEscalateTarget(null)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
