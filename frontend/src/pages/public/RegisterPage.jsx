import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Eye, EyeOff, UserPlus, ArrowLeft } from 'lucide-react'
import { authApi } from '../../api/auth'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

const registerSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email:     z.string().email('Enter a valid email'),
  phone:     z.string().regex(/^[6-9]\d{9}$/, 'Enter a valid 10-digit Indian mobile number'),
  password:  z.string().min(8, 'Password must be at least 8 characters'),
  confirm:   z.string(),
  age:       z.coerce.number().min(16, 'Must be at least 16').max(35, 'Must be under 35'),
}).refine((d) => d.password === d.confirm, {
  message: "Passwords don't match",
  path: ['confirm'],
})

const otpSchema = z.object({
  otp: z.string().length(6, 'OTP must be 6 digits'),
})

export default function RegisterPage() {
  const navigate  = useNavigate()
  const setUser   = useAuthStore((s) => s.setUser)
  const [step, setStep]       = useState(1) // 1 = form, 2 = otp
  const [showPw, setShowPw]   = useState(false)
  const [loading, setLoading] = useState(false)
  const [email, setEmail]     = useState('')

  const registerForm = useForm({ resolver: zodResolver(registerSchema) })
  const otpForm      = useForm({ resolver: zodResolver(otpSchema) })

  async function onRegister(data) {
    setLoading(true)
    try {
      await authApi.register(data)
      setEmail(data.email)
      toast.success('OTP sent to your email!')
      setStep(2)
    } catch (err) {
      toast.error(err.response?.data?.error ?? 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  async function onVerifyOtp(data) {
  setLoading(true)
  try {
    await authApi.verifyOtp({ email, otp: data.otp })
    toast.success('Account verified! Welcome 🎉')
    navigate('/login')              // go to login, backend returns no user here
  } catch (err) {
    toast.error(err.response?.data?.error ?? 'Invalid OTP')
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="min-h-[90vh] flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="card">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center
                            justify-center mx-auto mb-4">
              <UserPlus size={22} className="text-white" />
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white">
              {step === 1 ? 'Create your account' : 'Verify your email'}
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              {step === 1
                ? 'Start your financial wellness journey'
                : `Enter the 6-digit OTP sent to ${email}`}
            </p>
          </div>

          {/* Step 1 — Register form */}
          {step === 1 && (
            <form
              onSubmit={registerForm.handleSubmit(onRegister)}
              className="space-y-4"
            >
              <div>
                <label className="label">Full Name</label>
                <input
                  {...registerForm.register('full_name')}
                  placeholder="Riya Sharma"
                  className={`input ${registerForm.formState.errors.full_name ? 'input-error' : ''}`}
                />
                {registerForm.formState.errors.full_name && (
                  <p className="text-xs text-danger mt-1">
                    {registerForm.formState.errors.full_name.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">Email</label>
                <input
                  {...registerForm.register('email')}
                  type="email"
                  placeholder="riya@example.com"
                  className={`input ${registerForm.formState.errors.email ? 'input-error' : ''}`}
                />
                {registerForm.formState.errors.email && (
                  <p className="text-xs text-danger mt-1">
                    {registerForm.formState.errors.email.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">Phone</label>
                <input
                  {...registerForm.register('phone')}
                  placeholder="9876543210"
                  className={`input ${registerForm.formState.errors.phone ? 'input-error' : ''}`}
                />
                {registerForm.formState.errors.phone && (
                  <p className="text-xs text-danger mt-1">
                    {registerForm.formState.errors.phone.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">Age</label>
                <input
                  {...registerForm.register('age')}
                  type="number"
                  placeholder="22"
                  className={`input ${registerForm.formState.errors.age ? 'input-error' : ''}`}
                />
                {registerForm.formState.errors.age && (
                  <p className="text-xs text-danger mt-1">
                    {registerForm.formState.errors.age.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">Password</label>
                <div className="relative">
                  <input
                    {...registerForm.register('password')}
                    type={showPw ? 'text' : 'password'}
                    placeholder="Min 8 characters"
                    className={`input pr-10 ${registerForm.formState.errors.password ? 'input-error' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPw(!showPw)}
                    className="absolute right-3 top-1/2 -translate-y-1/2
                               text-slate-400 hover:text-slate-600"
                  >
                    {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {registerForm.formState.errors.password && (
                  <p className="text-xs text-danger mt-1">
                    {registerForm.formState.errors.password.message}
                  </p>
                )}
              </div>

              <div>
                <label className="label">Confirm Password</label>
                <input
                  {...registerForm.register('confirm')}
                  type="password"
                  placeholder="••••••••"
                  className={`input ${registerForm.formState.errors.confirm ? 'input-error' : ''}`}
                />
                {registerForm.formState.errors.confirm && (
                  <p className="text-xs text-danger mt-1">
                    {registerForm.formState.errors.confirm.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full py-3 mt-2"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>
          )}

          {/* Step 2 — OTP verification */}
          {step === 2 && (
            <form
              onSubmit={otpForm.handleSubmit(onVerifyOtp)}
              className="space-y-5"
            >
              <div>
                <label className="label">6-digit OTP</label>
                <input
                  {...otpForm.register('otp')}
                  placeholder="123456"
                  maxLength={6}
                  className={`input text-center text-2xl tracking-widest
                              ${otpForm.formState.errors.otp ? 'input-error' : ''}`}
                />
                {otpForm.formState.errors.otp && (
                  <p className="text-xs text-danger mt-1">
                    {otpForm.formState.errors.otp.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full py-3"
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>

              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-full flex items-center justify-center gap-2
                           text-sm text-slate-500 hover:text-slate-700"
              >
                <ArrowLeft size={14} />
                Back to registration
              </button>
            </form>
          )}

          {/* Footer */}
          {step === 1 && (
            <p className="text-center text-sm text-slate-500 mt-6">
              Already have an account?{' '}
              <Link to="/login" className="text-primary font-medium hover:underline">
                Sign in
              </Link>
            </p>
          )}
        </div>
      </motion.div>
    </div>
  )
}