import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../../api/admin'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Settings, Shield, MessageCircle, Server,
  CheckCircle2, XCircle, RefreshCw, Save, Info
} from 'lucide-react'

/* ── helpers ── */
function SectionHeader({ icon: Icon, title, description, color }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${color}`}>
        <Icon size={18} />
      </div>
      <div>
        <h2 className="font-bold text-slate-900 dark:text-white text-base">{title}</h2>
        {description && <p className="text-xs text-slate-500">{description}</p>}
      </div>
    </div>
  )
}

function FieldRow({ label, hint, children }) {
  return (
    <div className="grid md:grid-cols-5 gap-3 items-start py-4
                    border-b border-slate-100 dark:border-slate-700/60 last:border-0">
      <div className="md:col-span-2">
        <p className="text-sm font-medium text-slate-700 dark:text-slate-300">{label}</p>
        {hint && <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{hint}</p>}
      </div>
      <div className="md:col-span-3">{children}</div>
    </div>
  )
}

function NumInput({ value, onChange, min, max, suffix }) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="number"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="input w-28"
      />
      {suffix && <span className="text-xs text-slate-500">{suffix}</span>}
    </div>
  )
}

function Toggle({ checked, onChange, label }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full
                  transition-colors duration-200 focus:outline-none
                  ${checked ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-600'}`}
      aria-label={label}
    >
      <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow
                        transition-transform duration-200
                        ${checked ? 'translate-x-6' : 'translate-x-1'}`} />
    </button>
  )
}

function EnvChip({ ok, label }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full
                      text-xs font-semibold
                      ${ok
                        ? 'bg-green-100 text-green-700'
                        : 'bg-slate-100 text-slate-500'}`}>
      {ok
        ? <CheckCircle2 size={11} />
        : <XCircle      size={11} />}
      {label}
    </span>
  )
}

export default function AdminSettingsPage() {
  const qc = useQueryClient()

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-settings'],
    queryFn:  () => adminApi.settings().then((r) => r.data),
  })

  const [form, setForm] = useState(null)
  const [dirty, setDirty] = useState(false)

  // Populate form when data arrives
  useEffect(() => {
    if (data?.settings && !form) {
      setForm({ ...data.settings })
    }
  }, [data])

  function set(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
    setDirty(true)
  }

  const saveMutation = useMutation({
    mutationFn: (payload) => adminApi.updateSettings(payload),
    onSuccess: (res) => {
      toast.success(`Saved ${res.data.updated.length} setting${res.data.updated.length !== 1 ? 's' : ''}`)
      setDirty(false)
      qc.invalidateQueries({ queryKey: ['admin-settings'] })
    },
    onError: (e) => toast.error(e.response?.data?.error ?? 'Save failed'),
  })

  function handleSave() {
    if (!form) return
    const { ...payload } = form
    saveMutation.mutate(payload)
  }

  const env = data?.env_info ?? {}
  const s   = form ?? {}

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-8">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">Settings</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Platform configuration — changes apply immediately to new requests
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700
                       text-slate-500 transition-colors"
          >
            <RefreshCw size={15} />
          </button>
          <button
            onClick={handleSave}
            disabled={!dirty || saveMutation.isPending || isLoading}
            className="btn-primary flex items-center gap-2 text-sm disabled:opacity-40"
          >
            {saveMutation.isPending
              ? <RefreshCw size={14} className="animate-spin" />
              : <Save size={14} />}
            Save Changes
          </button>
        </div>
      </div>

      {/* Unsaved changes banner */}
      {dirty && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-4 py-3 rounded-xl
                     bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700"
        >
          <Info size={15} className="text-amber-600 flex-shrink-0" />
          <p className="text-sm text-amber-800 dark:text-amber-300">
            You have unsaved changes. Click <strong>Save Changes</strong> to apply them.
          </p>
        </motion.div>
      )}

      {/* ── Auth settings ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <SectionHeader
          icon={Shield}
          title="Authentication"
          description="OTP and password reset token behaviour"
          color="bg-indigo-100 text-indigo-600"
        />
        {isLoading ? (
          <div className="space-y-4">
            {[0,1,2,3].map(i => (
              <div key={i} className="h-10 rounded-xl bg-slate-100 dark:bg-slate-700 animate-pulse" />
            ))}
          </div>
        ) : (
          <>
            <FieldRow
              label="OTP Expiry"
              hint="How long a registration OTP stays valid"
            >
              <NumInput value={s.otp_exp_minutes} min={1} max={60}
                onChange={(v) => set('otp_exp_minutes', v)} suffix="minutes" />
            </FieldRow>
            <FieldRow
              label="Password Reset Expiry"
              hint="Lifetime of a password-reset link"
            >
              <NumInput value={s.reset_exp_minutes} min={5} max={1440}
                onChange={(v) => set('reset_exp_minutes', v)} suffix="minutes" />
            </FieldRow>
            <FieldRow
              label="Session Timeout"
              hint="Access token lifetime — users must re-authenticate after this"
            >
              <NumInput value={s.session_timeout_min} min={5} max={1440}
                onChange={(v) => set('session_timeout_min', v)} suffix="minutes" />
            </FieldRow>
            <FieldRow
              label="Min Password Length"
              hint="Minimum characters required for new passwords"
            >
              <NumInput value={s.min_password_length} min={6} max={32}
                onChange={(v) => set('min_password_length', v)} suffix="characters" />
            </FieldRow>
            <FieldRow
              label="Max Login Attempts"
              hint="Failed attempts before rate-limit kicks in"
            >
              <NumInput value={s.max_login_attempts} min={1} max={20}
                onChange={(v) => set('max_login_attempts', v)} suffix="attempts" />
            </FieldRow>
          </>
        )}
      </motion.div>

      {/* ── Platform settings ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.06 }}
        className="card"
      >
        <SectionHeader
          icon={Settings}
          title="Platform"
          description="General platform behaviour and identity"
          color="bg-emerald-100 text-emerald-600"
        />
        {isLoading ? (
          <div className="space-y-4">
            {[0,1,2].map(i => (
              <div key={i} className="h-10 rounded-xl bg-slate-100 dark:bg-slate-700 animate-pulse" />
            ))}
          </div>
        ) : (
          <>
            <FieldRow
              label="Platform Name"
              hint="Displayed in emails and UI headings"
            >
              <input
                className="input max-w-xs"
                value={s.platform_name ?? ''}
                onChange={(e) => set('platform_name', e.target.value)}
                maxLength={80}
              />
            </FieldRow>
            <FieldRow
              label="Support Email"
              hint="Shown to users who need help"
            >
              <input
                className="input max-w-xs"
                type="email"
                value={s.support_email ?? ''}
                onChange={(e) => set('support_email', e.target.value)}
              />
            </FieldRow>
            <FieldRow
              label="Crisis Alert Email"
              hint="Receives a copy when a high-severity crisis is flagged (leave blank to disable)"
            >
              <input
                className="input max-w-xs"
                type="email"
                value={s.crisis_alert_email ?? ''}
                onChange={(e) => set('crisis_alert_email', e.target.value)}
              />
            </FieldRow>
            <FieldRow
              label="Maintenance Mode"
              hint="Blocks all non-admin logins and shows a maintenance message"
            >
              <div className="flex items-center gap-3">
                <Toggle
                  checked={!!s.maintenance_mode}
                  onChange={(v) => set('maintenance_mode', v)}
                  label="Toggle maintenance mode"
                />
                <span className={`text-sm font-medium ${
                  s.maintenance_mode ? 'text-red-600' : 'text-slate-400'
                }`}>
                  {s.maintenance_mode ? 'On — logins blocked' : 'Off'}
                </span>
              </div>
            </FieldRow>
          </>
        )}
      </motion.div>

      {/* ── Guest chat settings ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12 }}
        className="card"
      >
        <SectionHeader
          icon={MessageCircle}
          title="Guest Chat"
          description="Controls for unauthenticated Try as Guest sessions"
          color="bg-purple-100 text-purple-600"
        />
        {isLoading ? (
          <div className="space-y-4">
            {[0,1].map(i => (
              <div key={i} className="h-10 rounded-xl bg-slate-100 dark:bg-slate-700 animate-pulse" />
            ))}
          </div>
        ) : (
          <>
            <FieldRow
              label="Guest Chat Enabled"
              hint="When off, the /guest route returns a 503"
            >
              <div className="flex items-center gap-3">
                <Toggle
                  checked={!!s.guest_chat_enabled}
                  onChange={(v) => set('guest_chat_enabled', v)}
                  label="Toggle guest chat"
                />
                <span className={`text-sm font-medium ${
                  s.guest_chat_enabled ? 'text-green-600' : 'text-slate-400'
                }`}>
                  {s.guest_chat_enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </FieldRow>
            <FieldRow
              label="Max Guest Messages"
              hint="Messages stored per guest session (oldest are dropped)"
            >
              <NumInput value={s.max_guest_messages} min={10} max={1000}
                onChange={(v) => set('max_guest_messages', v)} suffix="messages" />
            </FieldRow>
          </>
        )}
      </motion.div>

      {/* ── Environment info (read-only) ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.18 }}
        className="card"
      >
        <SectionHeader
          icon={Server}
          title="Environment"
          description="Read-only — set via environment variables"
          color="bg-slate-100 text-slate-600"
        />
        {isLoading ? (
          <div className="h-24 rounded-xl bg-slate-100 dark:bg-slate-700 animate-pulse" />
        ) : (
          <>
            <div className="flex flex-wrap gap-2 mb-5">
              <EnvChip ok={env.groq_key_set}   label="Groq API Key" />
              <EnvChip ok={env.hcaptcha_set}    label="hCaptcha Secret" />
              <EnvChip ok={!env.debug_mode}     label="Production Mode" />
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-3 px-4 py-3 rounded-xl
                              bg-slate-50 dark:bg-slate-700/50">
                <span className="text-slate-500 w-28 flex-shrink-0 text-xs font-medium uppercase tracking-wide">
                  Flask Env
                </span>
                <code className="text-slate-800 dark:text-slate-200 text-xs">
                  {env.flask_env ?? '—'}
                </code>
              </div>
              <div className="flex items-center gap-3 px-4 py-3 rounded-xl
                              bg-slate-50 dark:bg-slate-700/50">
                <span className="text-slate-500 w-28 flex-shrink-0 text-xs font-medium uppercase tracking-wide">
                  MongoDB URI
                </span>
                <code className="text-slate-800 dark:text-slate-200 text-xs break-all">
                  {env.mongo_uri_safe ?? '—'}
                </code>
              </div>
              <div className="flex items-center gap-3 px-4 py-3 rounded-xl
                              bg-slate-50 dark:bg-slate-700/50">
                <span className="text-slate-500 w-28 flex-shrink-0 text-xs font-medium uppercase tracking-wide">
                  Mail Sender
                </span>
                <code className="text-slate-800 dark:text-slate-200 text-xs">
                  {env.mail_sender ?? '—'}
                </code>
              </div>
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
