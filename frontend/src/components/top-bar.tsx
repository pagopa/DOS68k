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
    <header className="flex h-13 items-center justify-between border-b bg-card px-5 shadow-sm">
      <div className="flex items-center gap-5">
        <span className="text-sm font-700 tracking-wider text-foreground">DOS68K</span>
        {user?.role === 'user' && (
          <Link to="/chat" className="text-xs font-500 text-muted-foreground hover:text-foreground transition-colors">Chat</Link>
        )}
        {user?.role === 'admin' && (
          <>
            <Link to="/chat" className="text-xs font-500 text-muted-foreground hover:text-foreground transition-colors">Chat</Link>
            <Link to="/admin" className="text-xs font-500 text-muted-foreground hover:text-foreground transition-colors">Admin</Link>
          </>
        )}
      </div>
      <div className="flex items-center gap-3">
        {user && (
          <Badge variant="secondary" className="capitalize text-xs font-mono tracking-wide">
            {user.role}
          </Badge>
        )}
        <Button variant="ghost" size="sm" onClick={handleLogout} className="text-xs text-muted-foreground hover:text-foreground">
          Logout
        </Button>
      </div>
    </header>
  )
}
