import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { motion } from 'framer-motion'

export default function PublicLayout() {
  const { isAuthenticated, user } = useAuthStore()
  const location = useLocation()

  const dashboardPath =
    user?.role === 'admin'       ? '/admin'      :
    user?.role === 'counsellor'  ? '/counsellor' : '/dashboard'

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80
                      backdrop-blur border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-white font-bold text-sm">YF</span>
            </div>
            <span className="font-bold text-lg text-slate-900 dark:text-white">
              YouthFinance
            </span>
          </Link>

          {/* Nav links */}
          <div className="flex items-center gap-2">
            <Link to="/guest" className="btn-ghost text-sm">
              Try as Guest
            </Link>

            {isAuthenticated ? (
              <Link to={dashboardPath} className="btn-primary text-sm">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className={`btn-ghost text-sm ${
                    location.pathname === '/login' ? 'text-primary font-semibold' : ''
                  }`}
                >
                  Login
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Page content */}
      <main className="flex-1">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <Outlet />
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-slate-900 border-t border-slate-200
                         dark:border-slate-700 py-6 text-center text-sm text-slate-500">
        © {new Date().getFullYear()} YouthFinance · Built for financial wellness
      </footer>
    </div>
  )
}