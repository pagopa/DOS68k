export type Role = 'user' | 'admin'

export interface AuthProvider {
  login(role: Role): void
  logout(): void
  getToken(): string | null
  getUser(): { role: Role } | null
  isAuthenticated(): boolean
}
