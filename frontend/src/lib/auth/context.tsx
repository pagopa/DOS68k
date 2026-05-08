import { createContext, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import { LocalAuthProvider } from './local-auth'
import type { AuthUser, Role } from './types'

const provider = new LocalAuthProvider()

interface AuthContextValue {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (role: Role) => void
  logout: () => void
  getToken: () => string | null
  getUser: () => AuthUser | null
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthContextProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => provider.getUser())
  const [isAuthenticated, setIsAuthenticated] = useState(() => provider.isAuthenticated())

  const login = useCallback((role: Role) => {
    provider.login(role)
    setUser(provider.getUser())
    setIsAuthenticated(true)
  }, [])

  const logout = useCallback(() => {
    provider.logout()
    setUser(null)
    setIsAuthenticated(false)
  }, [])

  const getToken = useCallback(() => provider.getToken(), [])
  const getUser = useCallback(() => provider.getUser(), [])

  return (
    <AuthContext value={{ user, isAuthenticated, login, logout, getToken, getUser }}>
      {children}
    </AuthContext>
  )
}
