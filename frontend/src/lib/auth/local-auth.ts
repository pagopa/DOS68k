import type { AuthProvider, AuthUser, Role } from './types'

const ROLE_KEY = 'dos68k:role'
const TOKEN_KEY = 'dos68k:token'

const LOCAL_USER_IDS: Record<Role, string> = {
  user: '00000000-0000-0000-0000-000000000001',
  admin: '00000000-0000-0000-0000-000000000002',
}

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

  getUser(): AuthUser | null {
    const role = localStorage.getItem(ROLE_KEY) as Role | null
    if (!role) return null
    return { role, id: LOCAL_USER_IDS[role] }
  }

  isAuthenticated(): boolean {
    return localStorage.getItem(TOKEN_KEY) !== null
  }
}
