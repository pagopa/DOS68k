import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/lib/auth/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { Role } from '@/lib/auth/types'

export function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()

  if (user) {
    navigate(user.role === 'admin' ? '/admin' : '/chat', { replace: true })
    return null
  }

  function handleLogin(role: Role) {
    login(role)
    navigate(role === 'admin' ? '/admin' : '/chat', { replace: true })
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
      <div className="mb-8 w-full max-w-sm rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-center text-xs text-amber-700">
        <strong className="text-amber-800">DEV / DEMO ONLY</strong>
        {' '}— not real authentication. Will be replaced with IdP.
      </div>

      <Card className="w-full max-w-sm border-border shadow-none">
        <CardHeader className="text-center pb-4">
          <CardTitle className="text-3xl font-700 tracking-widest text-foreground">DOS68K</CardTitle>
          <CardDescription className="text-muted-foreground text-xs tracking-wide uppercase">Select a role to continue</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2.5">
          <Button className="w-full h-11 text-sm font-600 tracking-wide" onClick={() => handleLogin('user')}>
            Continue as User
          </Button>
          <Button variant="outline" className="w-full h-11 text-sm font-500 text-muted-foreground hover:text-foreground" onClick={() => handleLogin('admin')}>
            Continue as Admin
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
