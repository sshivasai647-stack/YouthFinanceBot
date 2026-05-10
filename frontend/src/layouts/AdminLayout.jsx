import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authApi } from '../api/auth'
import { getInitials } from '../lib/utils'
import toast from 'react-hot-toast'
import {
  LayoutDashboard, Users, BarChart2, Settings, LogOut, Menu, ScrollText
} from 'lucide-react'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const navItems = [
  { to: '/admin',           icon: LayoutDashboard, label: 'Dashboard'  },
  { to: '/admin/users',     icon: Users,           label: 'Users'      },
  { to: '/admin/analytics', icon: BarChart2,       label: 'Analytics'  },
  { to: '/admin/logs',      icon: ScrollText,      label: 'Audit Logs' },
  { to: '/admin/settings',  icon: Settings,        label: 'Settings'   },
]

export default function AdminLayout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  async function handleLogout() {
    try { await authApi.logout() } catch { /* ignore */ }
    logout()
    navigate('/login')
    toast.success('Logged out successfully')
  }

  const Sidebar = ({ mobile = false }) => (
    <aside className={`
      flex flex-col h-full bg-slate-900 text-white
      border-r border-slate-700
      ${mobile ? 'w-72' : 'w-64 hidden lg:flex'}
    `}>
      <div className="h-16 flex items-center gap-2 px-6 border-b border-slate-700">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="text-white font-bold text-sm">YF</span>
        </div>
        <span className="font-bold text-lg">Admin Panel</span>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/admin'}
            onClick={() => setSidebarOpen(false)}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium
              transition-all duration-200
              ${isActive
                ? 'bg-primary text-white shadow-md shadow-primary/30'
                : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }
            `}
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center gap-3 px-3 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center
                          justify-center text-xs font-bold text-white">
            {getInitials(user?.full_name)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name}</p>
            <p className="text-xs text-slate-400 truncate">Administrator</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl
                     text-sm font-medium text-red-400 hover:bg-red-900/20
                     transition-all duration-200"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  )

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />

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

      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="h-16 flex items-center gap-4 px-4 bg-slate-900
                        border-b border-slate-700 lg:hidden">
          <button onClick={() => setSidebarOpen(true)} className="text-white p-2">
            <Menu size={20} />
          </button>
          <span className="font-bold text-lg text-white">Admin Panel</span>
        </div>

        <main className="flex-1 overflow-y-auto bg-slate-50 dark:bg-slate-900">
          <Outlet />
        </main>
      </div>
    </div>
  )
}