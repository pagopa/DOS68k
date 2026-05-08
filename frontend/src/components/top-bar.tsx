import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/lib/auth/use-auth'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export function TopBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="flex h-14 items-center justify-between border-b bg-white px-4 shadow-sm">
      <div className="flex items-center gap-4">
        <span className="font-semibold text-gray-900">DOS68K</span>
        {user?.role === 'user' && (
          <Link to="/chat" className="text-sm text-gray-600 hover:text-gray-900">Chat</Link>
        )}
        {user?.role === 'admin' && (
          <>
            <Link to="/chat" className="text-sm text-gray-600 hover:text-gray-900">Chat</Link>
            <Link to="/admin" className="text-sm text-gray-600 hover:text-gray-900">Admin</Link>
          </>
        )}
      </div>
      <div className="flex items-center gap-3">
        {user && (
          <Badge variant="secondary" className="capitalize">
            {user.role}
          </Badge>
        )}
        <Button variant="outline" size="sm" onClick={handleLogout}>
          Logout
        </Button>
      </div>
    </header>
  )
}
