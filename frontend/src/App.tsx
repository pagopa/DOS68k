import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthContextProvider } from '@/lib/auth/context'
import { useAuth } from '@/lib/auth/use-auth'
import { RequireAuth } from '@/routes/require-auth'
import { RequireAdmin } from '@/routes/require-admin'
import { LoginPage } from '@/pages/login'
import { ChatPage } from '@/pages/chat'
import { AdminPage } from '@/pages/admin'
import { Toaster } from '@/components/ui/sonner'

function RootRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'admin' ? '/admin' : '/chat'} replace />
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<RootRedirect />} />
      <Route
        path="/chat"
        element={<RequireAuth><ChatPage /></RequireAuth>}
      />
      <Route
        path="/chat/:sessionId"
        element={<RequireAuth><ChatPage /></RequireAuth>}
      />
      <Route
        path="/admin"
        element={<RequireAuth><RequireAdmin><AdminPage /></RequireAdmin></RequireAuth>}
      />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthContextProvider>
        <AppRoutes />
        <Toaster />
      </AuthContextProvider>
    </BrowserRouter>
  )
}
