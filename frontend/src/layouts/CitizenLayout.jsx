import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authApi } from '../api/auth'
import { getInitials } from '../lib/utils'
import toast from 'react-hot-toast'
import {
  LayoutDashboard, MessageCircle, Target, CreditCard,
  TrendingUp, AlertTriangle, User, LogOut, Menu, X
} from 'lucide-react'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const navItems = [
  { to: '/dashboard',              icon: LayoutDashboard, label: 'Dashboard'    },
  { to: '/dashboard/chat',         icon: MessageCircle,   label: 'AI Chat'      },
  { to: '/dashboard/goals',        icon: Target,          label: 'Goals'        },
  { to: '/dashboard/debt',         icon: CreditCard,      label: 'Debt Manager' },
  { to: '/dashboard/spending',     icon: TrendingUp,      label: 'Spending'     },
  { to: '/dashboard/betting',      icon: AlertTriangle,   label: 'Betting Risk' },
  { to: '/dashboard/profile',      icon: User,            label: 'Profile'      },
]

export default function CitizenLayout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  async function handleLogout() {
    try {
      await authApi.logout()
    } catch { /* ignore */ }
    logout()
    navigate('/login')
    toast.success('Logged out successfully')
  }

  const Sidebar = ({ mobile = false }) => (
    <aside className={`
      flex flex-col h-full bg-white dark:bg-slate-800
      border-r border-slate-200 dark:border-slate-700
      ${mobile ? 'w-72' : 'w-64 hidden lg:flex'}
    `}>
      {/* Logo */}
      <div className="h-16 flex items-center gap-2 px-6 border-b
                      border-slate-200 dark:border-slate-700">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="text-white font-bold text-sm">YF</span>
        </div>
        <span className="font-bold text-lg">YouthFinance</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/dashboard'}
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium
              transition-all duration-200
              ${isActive
                ? 'bg-primary text-white shadow-md shadow-primary/30'
                : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
              }
            `}
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3 px-3 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700
                          flex items-center justify-center text-xs font-bold">
            {getInitials(user?.full_name)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name}</p>
            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl
                     text-sm font-medium text-red-500 hover:bg-red-50
                     dark:hover:bg-red-900/20 transition-all duration-200"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  )

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop sidebar */}
      <Sidebar />

      {/* Mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            />
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: 'spring', damping: 25 }}
              className="fixed inset-y-0 left-0 z-50 lg:hidden"
            >
              <Sidebar mobile />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar (mobile) */}
        <div className="h-16 flex items-center gap-4 px-4 bg-white dark:bg-slate-800
                        border-b border-slate-200 dark:border-slate-700 lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="btn-ghost p-2"
          >
            <Menu size={20} />
          </button>
          <span className="font-bold text-lg">YouthFinance</span>
        </div>

        {/* Page */}
        <main className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900">
          <Outlet />
        </main>
      </div>
    </div>
  )
}