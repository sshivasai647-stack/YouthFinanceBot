import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Layouts
import PublicLayout      from './layouts/PublicLayout'
import CitizenLayout     from './layouts/CitizenLayout'
import CounsellorLayout  from './layouts/CounsellorLayout'
import AdminLayout       from './layouts/AdminLayout'

// Admin pages
import AdminDashboard      from './pages/admin/AdminDashboard'
import AdminUsersPage      from './pages/admin/AdminUsersPage'
import AdminAnalyticsPage  from './pages/admin/AdminAnalyticsPage'
import AdminSettingsPage   from './pages/admin/AdminSettingsPage'

// Public pages
import LandingPage    from './pages/public/LandingPage'
import LoginPage      from './pages/public/LoginPage'
import RegisterPage   from './pages/public/RegisterPage'
import GuestChatPage  from './pages/public/GuestChatPage'

// Citizen pages
import DashboardHome  from './pages/citizen/DashboardHome'
import ChatPage       from './pages/citizen/ChatPage'
import GoalsPage      from './pages/citizen/GoalsPage'
import DebtPage       from './pages/citizen/DebtPage'
import SpendingPage   from './pages/citizen/SpendingPage'
import BettingPage    from './pages/citizen/BettingPage'
import ProfilePage    from './pages/citizen/ProfilePage'

// Protected route wrapper
function ProtectedRoute({ children, allowedRoles }) {
  const { user, isAuthenticated } = useAuthStore()

  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/login" replace />
  }
  return children
}

export default function App() {
  return (
    <Routes>
      {/* ── Public ── */}
      <Route element={<PublicLayout />}>
        <Route path="/"         element={<LandingPage />}   />
        <Route path="/login"    element={<LoginPage />}     />
        <Route path="/register" element={<RegisterPage />}  />
        <Route path="/guest"    element={<GuestChatPage />} />
      </Route>

      {/* ── Citizen ── */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute allowedRoles={['citizen']}>
            <CitizenLayout />
          </ProtectedRoute>
        }
      >
        <Route index              element={<DashboardHome />} />
        <Route path="chat"        element={<ChatPage />}      />
        <Route path="goals"       element={<GoalsPage />}     />
        <Route path="debt"        element={<DebtPage />}      />
        <Route path="spending"    element={<SpendingPage />}  />
        <Route path="betting"     element={<BettingPage />}   />
        <Route path="profile"     element={<ProfilePage />}   />
      </Route>

      {/* ── Counsellor ── */}
      <Route
        path="/counsellor"
        element={
          <ProtectedRoute allowedRoles={['counsellor']}>
            <CounsellorLayout />
          </ProtectedRoute>
        }
      >
        <Route index              element={<div className="p-6">Counsellor Dashboard — Coming Soon</div>} />
        <Route path="citizens"    element={<div className="p-6">Citizens List — Coming Soon</div>}        />
        <Route path="alerts"      element={<div className="p-6">Alerts — Coming Soon</div>}               />
      </Route>

      {/* ── Admin ── */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index              element={<AdminDashboard />} />
        <Route path="users"       element={<AdminUsersPage />}                                        />
        <Route path="analytics"   element={<AdminAnalyticsPage />}                                   />
        <Route path="settings"    element={<AdminSettingsPage />}                                    />
      </Route>

      {/* ── Fallback ── */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}