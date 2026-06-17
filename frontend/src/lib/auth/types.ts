export type Role = 'user' | 'admin'

export interface AuthUser {
  role: Role
  id: string
}

export interface AuthProvider {
  login(role: Role): void
  logout(): void
  getToken(): string | null
  getUser(): AuthUser | null
  isAuthenticated(): boolean
}
