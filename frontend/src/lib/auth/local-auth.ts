import type { AuthProvider, Role } from './types'

const ROLE_KEY = 'dos68k:role'
const TOKEN_KEY = 'dos68k:token'

export class LocalAuthProvider implements AuthProvider {
  login(role: Role): void {
    localStorage.setItem(ROLE_KEY, role)
    // Placeholder bearer — real IdP will replace this token via AuthProvider.login()
    localStorage.setItem(TOKEN_KEY, `local-token-${role}`)
  }

  logout(): void {
    localStorage.removeItem(ROLE_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  }

  getUser(): { role: Role } | null {
    const role = localStorage.getItem(ROLE_KEY) as Role | null
    if (!role) return null
    return { role }
  }

  isAuthenticated(): boolean {
    return localStorage.getItem(TOKEN_KEY) !== null
  }
}
