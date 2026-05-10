import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Search, Filter, ChevronLeft, ChevronRight,
  ShieldOff, ShieldCheck, CheckCircle2, XCircle,
  Clock, Users, RefreshCw, AlertTriangle
} from 'lucide-react'

const ROLES = ['all', 'citizen', 'counsellor', 'admin']
const PAGE_SIZE = 20

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

function RoleBadge({ role }) {
  const map = {
    citizen:    'bg-blue-100 text-blue-700',
    counsellor: 'bg-purple-100 text-purple-700',
    admin:      'bg-amber-100 text-amber-700',
  }
  return (
    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-semibold capitalize
                      ${map[role] ?? 'bg-slate-100 text-slate-600'}`}>
      {role}
    </span>
  )
}

function BlockModal({ user, onConfirm, onCancel, isPending }) {
  const [reason, setReason] = useState('')
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-slate-800 rounded-2xl p-6 max-w-md w-full shadow-xl"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-red-100 text-red-600 flex items-center justify-center">
            <AlertTriangle size={20} />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white">Block User</h3>
            <p className="text-xs text-slate-500">{user.name} · {user.email}</p>
          </div>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
          This will prevent the user from logging in. You can unblock them at any time.
        </p>
        <div className="mb-5">
          <label className="label">Reason (optional)</label>
          <input
            className="input"
            placeholder="Policy violation, suspicious activity…"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
        </div>
        <div className="flex gap-3 justify-end">
          <button onClick={onCancel} className="btn-secondary" disabled={isPending}>
            Cancel
          </button>
          <button
            onClick={() => onConfirm(reason)}
            disabled={isPending}
            className="btn-danger flex items-center gap-2"
          >
            {isPending ? <RefreshCw size={14} className="animate-spin" /> : <ShieldOff size={14} />}
            Block User
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default function AdminUsersPage() {
  const qc = useQueryClient()
  const [page, setPage]           = useState(1)
  const [roleFilter, setRole]     = useState('all')
  const [activeFilter, setActive] = useState('all')  // 'all' | 'active' | 'inactive'
  const [search, setSearch]       = useState('')
  const [blocking, setBlocking]   = useState(null)   // user object to block

  const params = {
    page,
    limit: PAGE_SIZE,
    ...(roleFilter !== 'all'   && { role:   roleFilter }),
    ...(activeFilter === 'active'   && { active: 'true'  }),
    ...(activeFilter === 'inactive' && { active: 'false' }),
  }

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['admin-users', params],
    queryFn:  () => adminApi.users(params).then((r) => r.data),
    keepPreviousData: true,
  })

  const blockMutation = useMutation({
    mutationFn: ({ id, reason }) => adminApi.blockUser(id, { reason }),
    onSuccess: () => {
      toast.success('User blocked')
      setBlocking(null)
      qc.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (e) => toast.error(e.response?.data?.error ?? 'Failed to block'),
  })

  const unblockMutation = useMutation({
    mutationFn: (id) => adminApi.unblockUser(id),
    onSuccess: () => {
      toast.success('User unblocked')
      qc.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (e) => toast.error(e.response?.data?.error ?? 'Failed to unblock'),
  })

  const users = data?.users ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  // Client-side search (name / email)
  const filtered = search.trim()
    ? users.filter((u) =>
        u.name?.toLowerCase().includes(search.toLowerCase()) ||
        u.email?.toLowerCase().includes(search.toLowerCase())
      )
    : users

  function changePage(n) {
    setPage(Math.max(1, Math.min(n, totalPages)))
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">Users</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {total.toLocaleString()} total · page {page} of {totalPages}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <RefreshCw size={14} className={isFetching ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4 space-y-3">
        {/* Search */}
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            className="input pl-10"
            placeholder="Search by name or email…"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          />
        </div>

        <div className="flex flex-wrap gap-3">
          {/* Role filter */}
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-slate-400" />
            <span className="text-xs font-medium text-slate-500">Role:</span>
            <div className="flex gap-1">
              {ROLES.map((r) => (
                <button
                  key={r}
                  onClick={() => { setRole(r); setPage(1) }}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-colors
                    ${roleFilter === r
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                    }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Active filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-500">Status:</span>
            <div className="flex gap-1">
              {['all', 'active', 'inactive'].map((s) => (
                <button
                  key={s}
                  onClick={() => { setActive(s); setPage(1) }}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-colors
                    ${activeFilter === s
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                    }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/50">
                <th className="text-left px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">User</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600 dark:text-slate-300">Role</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600 dark:text-slate-300">Verified</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600 dark:text-slate-300">Status</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600 dark:text-slate-300">Joined</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600 dark:text-slate-300">Last Login</th>
                <th className="text-right px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i} className="border-b border-slate-100 dark:border-slate-700/50">
                    {Array.from({ length: 7 }).map((__, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-4 rounded bg-slate-200 dark:bg-slate-600 animate-pulse w-24" />
                      </td>
                    ))}
                  </tr>
                ))
              )}

              <AnimatePresence>
                {!isLoading && filtered.map((user, i) => (
                  <motion.tr
                    key={user.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.02 }}
                    className="border-b border-slate-100 dark:border-slate-700/50
                               hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors"
                  >
                    {/* User */}
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700
                                        flex items-center justify-center text-xs font-bold flex-shrink-0">
                          {(user.name?.[0] ?? user.email?.[0] ?? '?').toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-slate-900 dark:text-white">
                            {user.name || '—'}
                          </p>
                          <p className="text-xs text-slate-500">{user.email}</p>
                        </div>
                      </div>
                    </td>

                    {/* Role */}
                    <td className="px-4 py-3">
                      <RoleBadge role={user.role} />
                    </td>

                    {/* Verified */}
                    <td className="px-4 py-3">
                      {user.is_verified
                        ? <CheckCircle2 size={16} className="text-green-500" />
                        : <XCircle     size={16} className="text-slate-300" />
                      }
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5
                                        rounded-full text-xs font-semibold
                                        ${user.is_active
                                          ? 'bg-green-100 text-green-700'
                                          : 'bg-red-100 text-red-600'}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                        {user.is_active ? 'Active' : 'Blocked'}
                      </span>
                    </td>

                    {/* Joined */}
                    <td className="px-4 py-3 text-slate-500 text-xs">
                      <div className="flex items-center gap-1">
                        <Users size={12} />
                        {formatDate(user.created_at)}
                      </div>
                    </td>

                    {/* Last login */}
                    <td className="px-4 py-3 text-slate-500 text-xs">
                      <div className="flex items-center gap-1">
                        <Clock size={12} />
                        {formatDate(user.last_login)}
                      </div>
                    </td>

                    {/* Actions */}
                    <td className="px-5 py-3 text-right">
                      {user.role !== 'admin' && (
                        user.is_active ? (
                          <button
                            onClick={() => setBlocking(user)}
                            disabled={blockMutation.isPending || unblockMutation.isPending}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                                       text-xs font-semibold text-red-600 hover:bg-red-50
                                       dark:hover:bg-red-900/20 transition-colors disabled:opacity-40"
                          >
                            <ShieldOff size={13} />
                            Block
                          </button>
                        ) : (
                          <button
                            onClick={() => unblockMutation.mutate(user.id)}
                            disabled={blockMutation.isPending || unblockMutation.isPending}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                                       text-xs font-semibold text-green-600 hover:bg-green-50
                                       dark:hover:bg-green-900/20 transition-colors disabled:opacity-40"
                          >
                            {unblockMutation.isPending
                              ? <RefreshCw size={13} className="animate-spin" />
                              : <ShieldCheck size={13} />
                            }
                            Unblock
                          </button>
                        )
                      )}
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>

              {!isLoading && filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center py-16 text-slate-400">
                    <Users size={32} className="mx-auto mb-2 opacity-30" />
                    <p className="text-sm">No users found</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-3
                          border-t border-slate-200 dark:border-slate-700">
            <p className="text-xs text-slate-500">
              Showing {((page - 1) * PAGE_SIZE) + 1}–{Math.min(page * PAGE_SIZE, total)} of {total}
            </p>
            <div className="flex items-center gap-1">
              <button
                onClick={() => changePage(page - 1)}
                disabled={page <= 1}
                className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700
                           text-slate-500 disabled:opacity-30 transition-colors"
              >
                <ChevronLeft size={16} />
              </button>

              {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
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
                    onClick={() => changePage(p)}
                    className={`w-8 h-8 rounded-lg text-xs font-semibold transition-colors
                      ${p === page
                        ? 'bg-indigo-600 text-white'
                        : 'hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300'
                      }`}
                  >
                    {p}
                  </button>
                )
              })}

              <button
                onClick={() => changePage(page + 1)}
                disabled={page >= totalPages}
                className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700
                           text-slate-500 disabled:opacity-30 transition-colors"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Block confirmation modal */}
      <AnimatePresence>
        {blocking && (
          <BlockModal
            user={blocking}
            isPending={blockMutation.isPending}
            onConfirm={(reason) => blockMutation.mutate({ id: blocking.id, reason })}
            onCancel={() => setBlocking(null)}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
