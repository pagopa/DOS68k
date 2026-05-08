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
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4">
      <div className="mb-6 w-full max-w-md rounded-md border border-yellow-300 bg-yellow-50 px-4 py-3 text-center text-sm text-yellow-800">
        <strong>DEV / DEMO ONLY — not real authentication.</strong>
        {' '}This login screen will be replaced when an IdP provider is configured.
      </div>

      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">DOS68K</CardTitle>
          <CardDescription>Choose a role to continue</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Button className="w-full h-14 text-base" onClick={() => handleLogin('user')}>
            Continue as User
          </Button>
          <Button variant="outline" className="w-full h-14 text-base" onClick={() => handleLogin('admin')}>
            Continue as Admin
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
