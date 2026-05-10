import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Filter, ChevronLeft, ChevronRight,
  RefreshCw, Download, Clock, Terminal,
  User, Globe, ChevronDown, ChevronUp, Tag
} from 'lucide-react'
import toast from 'react-hot-toast'

/* ── helpers ── */
function fmtTimestamp(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
}

function fmtRelative(iso) {
  if (!iso) return ''
  const secs = Math.floor((Date.now() - new Date(iso)) / 1000)
  if (secs < 60)   return `${secs}s ago`
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`
  if (secs < 86400) return `${Math.floor(secs / 3600)}h ago`
  return `${Math.floor(secs / 86400)}d ago`
}

const ACTION_COLORS = {
  block_user:        'bg-red-100    text-red-700',
  unblock_user:      'bg-green-100  text-green-700',
  update_settings:   'bg-indigo-100 text-indigo-700',
  export_analytics:  'bg-amber-100  text-amber-700',
  default:           'bg-slate-100  text-slate-600',
}

function ActionBadge({ action }) {
  const cls = ACTION_COLORS[action] ?? ACTION_COLORS.default
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${cls}`}>
      <Tag size={10} />
      {action || '—'}
    </span>
  )
}

function LogRow({ log }) {
  const [expanded, setExpanded] = useState(false)
  const hasChanges = Array.isArray(log.changes) && log.changes.length > 0

  return (
    <>
      <tr
        className="hover:bg-slate-50 dark:hover:bg-slate-700/40 transition-colors cursor-pointer"
        onClick={() => hasChanges && setExpanded((v) => !v)}
      >
        {/* Timestamp */}
        <td className="px-4 py-3 whitespace-nowrap">
          <div className="flex items-center gap-2">
            <Clock size={13} className="text-slate-400 flex-shrink-0" />
            <div>
              <p className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                {fmtTimestamp(log.timestamp)}
              </p>
              <p className="text-xs text-slate-400">{fmtRelative(log.timestamp)}</p>
            </div>
          </div>
        </td>

        {/* Action */}
        <td className="px-4 py-3">
          <ActionBadge action={log.action} />
        </td>

        {/* Endpoint */}
        <td className="px-4 py-3 max-w-xs">
          <div className="flex items-center gap-2">
            <Terminal size={12} className="text-slate-400 flex-shrink-0" />
            <code className="text-xs text-slate-600 dark:text-slate-300 truncate max-w-[200px]">
              {log.endpoint || '—'}
            </code>
          </div>
        </td>

        {/* User */}
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            <User size={12} className="text-slate-400 flex-shrink-0" />
            <code className="text-xs text-slate-500 font-mono truncate max-w-[120px]">
              {log.user_id || '—'}
            </code>
          </div>
        </td>

        {/* IP */}
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            <Globe size={12} className="text-slate-400 flex-shrink-0" />
            <span className="text-xs text-slate-500 font-mono">{log.ip || '—'}</span>
          </div>
        </td>

        {/* Expand toggle */}
        <td className="px-4 py-3 text-right">
          {hasChanges && (
            <button className="text-slate-400 hover:text-slate-600 transition-colors">
              {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </td>
      </tr>

      {/* Expanded detail row */}
      <AnimatePresence>
        {expanded && hasChanges && (
          <tr>
            <td colSpan={6} className="px-6 pb-3 pt-0 bg-indigo-50/60 dark:bg-indigo-900/10">
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.18 }}
                className="overflow-hidden"
              >
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
                  Changed fields
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {log.changes.map((c) => (
                    <span key={c}
                      className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-800
                                 border border-slate-200 dark:border-slate-600
                                 text-xs text-indigo-600 dark:text-indigo-400 font-mono">
                      {c}
                    </span>
                  ))}
                </div>
              </motion.div>
            </td>
          </tr>
        )}
      </AnimatePresence>
    </>
  )
}

const PAGE_SIZES = [25, 50, 100]

export default function AdminAuditLogsPage() {
  const [search,   setSearch]   = useState('')
  const [action,   setAction]   = useState('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo,   setDateTo]   = useState('')
  const [page,     setPage]     = useState(1)
  const [limit,    setLimit]    = useState(50)
  const [showFilters, setShowFilters] = useState(false)

  // Committed query params (only applied on search/filter submit)
  const [committed, setCommitted] = useState({
    search: '', action: 'all', dateFrom: '', dateTo: '',
  })

  function applyFilters() {
    setCommitted({ search, action, dateFrom, dateTo })
    setPage(1)
  }

  function clearFilters() {
    setSearch(''); setAction('all'); setDateFrom(''); setDateTo('')
    setCommitted({ search: '', action: 'all', dateFrom: '', dateTo: '' })
    setPage(1)
  }

  const params = {
    page,
    limit,
    ...(committed.search   ? { search:    committed.search }   : {}),
    ...(committed.action !== 'all' ? { action: committed.action } : {}),
    ...(committed.dateFrom ? { date_from: committed.dateFrom } : {}),
    ...(committed.dateTo   ? { date_to:   committed.dateTo }   : {}),
  }

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['admin-audit-logs', params],
    queryFn:  () => adminApi.auditLogs(params).then((r) => r.data),
    keepPreviousData: true,
  })

  const logs       = data?.logs       ?? []
  const total      = data?.total      ?? 0
  const totalPages = data?.pages      ?? 1
  const allActions = data?.all_actions ?? []

  const activeFilters =
    committed.search || committed.action !== 'all' || committed.dateFrom || committed.dateTo

  async function handleExport() {
    try {
      const res = await adminApi.exportExcel()
      const url = URL.createObjectURL(new Blob([res.data]))
      const a   = document.createElement('a')
      a.href     = url
      a.download = 'youthfinancebot_analytics.xlsx'
      a.click()
      URL.revokeObjectURL(url)
      toast.success('Export downloaded')
    } catch {
      toast.error('Export failed')
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">Audit Logs</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {total.toLocaleString()} total records — all admin actions on the platform
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700
                       text-slate-500 transition-colors"
          >
            <RefreshCw size={15} className={isFetching ? 'animate-spin' : ''} />
          </button>
          <button
            onClick={handleExport}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Download size={14} />
            Export
          </button>
        </div>
      </div>

      {/* Search + filter bar */}
      <div className="card p-4 space-y-4">
        <div className="flex gap-3 flex-wrap">
          {/* Search input */}
          <div className="relative flex-1 min-w-[200px]">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              className="input pl-9 w-full"
              placeholder="Search endpoint, action, user ID, IP…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
            />
          </div>

          {/* Action dropdown */}
          <select
            className="input w-48"
            value={action}
            onChange={(e) => setAction(e.target.value)}
          >
            <option value="all">All actions</option>
            {allActions.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>

          {/* Advanced toggle */}
          <button
            onClick={() => setShowFilters((v) => !v)}
            className={`btn-secondary flex items-center gap-2 text-sm
                        ${showFilters ? 'bg-slate-200 dark:bg-slate-600' : ''}`}
          >
            <Filter size={14} />
            Date range
            {showFilters ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>

          {/* Apply */}
          <button onClick={applyFilters} className="btn-primary text-sm px-4">
            Apply
          </button>

          {/* Clear */}
          {activeFilters && (
            <button onClick={clearFilters}
              className="text-sm text-slate-500 hover:text-red-600 underline transition-colors">
              Clear
            </button>
          )}
        </div>

        {/* Date range row */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.18 }}
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
                <th className="px-4 py-3 text-left text-xs font-semibold
                               text-slate-500 uppercase tracking-wide w-52">
                  Timestamp
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold
                               text-slate-500 uppercase tracking-wide">
                  Action
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold
                               text-slate-500 uppercase tracking-wide">
                  Endpoint
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold
                               text-slate-500 uppercase tracking-wide">
                  Admin ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold
                               text-slate-500 uppercase tracking-wide">
                  IP
                </th>
                <th className="w-8" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700/60">
              {isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}>
                    {[0,1,2,3,4,5].map((c) => (
                      <td key={c} className="px-4 py-3">
                        <div className="h-4 rounded bg-slate-100 dark:bg-slate-700 animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-20 text-center">
                    <div className="flex flex-col items-center gap-3 text-slate-400">
                      <Terminal size={36} strokeWidth={1.2} />
                      <p className="text-sm font-medium">No audit log entries found</p>
                      {activeFilters && (
                        <button onClick={clearFilters}
                          className="text-xs text-indigo-600 underline">
                          Clear filters
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ) : (
                logs.map((log) => <LogRow key={log.id} log={log} />)
              )}
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
                Showing {((page - 1) * limit) + 1}–{Math.min(page * limit, total)} of {total.toLocaleString()}
              </span>
              <select
                className="input !py-1 !text-xs w-20"
                value={limit}
                onChange={(e) => { setLimit(Number(e.target.value)); setPage(1) }}
              >
                {PAGE_SIZES.map((s) => <option key={s} value={s}>{s} / page</option>)}
              </select>
            </div>

            <div className="flex items-center gap-1">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700
                           disabled:opacity-30 transition-colors"
              >
                <ChevronLeft size={15} />
              </button>
              {/* Page pills */}
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                let p
                if (totalPages <= 7) {
                  p = i + 1
                } else if (page <= 4) {
                  p = i + 1
                } else if (page >= totalPages - 3) {
                  p = totalPages - 6 + i
                } else {
                  p = page - 3 + i
                }
                return (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`w-7 h-7 rounded-lg text-xs font-medium transition-colors
                                ${p === page
                                  ? 'bg-indigo-600 text-white'
                                  : 'hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300'
                                }`}
                  >
                    {p}
                  </button>
                )
              })}
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700
                           disabled:opacity-30 transition-colors"
              >
                <ChevronRight size={15} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
