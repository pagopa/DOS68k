import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthContextProvider } from '@/lib/auth/context'
import { RequireAuth } from './require-auth'
import { RequireAdmin } from './require-admin'

function wrap(initialPath: string, element: React.ReactNode) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthContextProvider>
        <Routes>
          <Route path="/login" element={<div>login page</div>} />
          <Route path="/chat" element={<div>chat page</div>} />
          <Route path="/admin" element={element} />
        </Routes>
      </AuthContextProvider>
    </MemoryRouter>
  )
}

describe('RequireAuth', () => {
  beforeEach(() => localStorage.clear())

  it('redirects unauthenticated visitor to /login', () => {
    render(
      <MemoryRouter initialEntries={['/chat']}>
        <AuthContextProvider>
          <Routes>
            <Route path="/login" element={<div>login page</div>} />
            <Route path="/chat" element={<RequireAuth><div>chat content</div></RequireAuth>} />
          </Routes>
        </AuthContextProvider>
      </MemoryRouter>
    )
    expect(screen.getByText('login page')).toBeInTheDocument()
    expect(screen.queryByText('chat content')).not.toBeInTheDocument()
  })

  it('renders children when authenticated', () => {
    localStorage.setItem('dos68k:role', 'user')
    localStorage.setItem('dos68k:token', 'local-token-user')
    render(
      <MemoryRouter initialEntries={['/chat']}>
        <AuthContextProvider>
          <Routes>
            <Route path="/login" element={<div>login page</div>} />
            <Route path="/chat" element={<RequireAuth><div>chat content</div></RequireAuth>} />
          </Routes>
        </AuthContextProvider>
      </MemoryRouter>
    )
    expect(screen.getByText('chat content')).toBeInTheDocument()
    expect(screen.queryByText('login page')).not.toBeInTheDocument()
  })
})

describe('RequireAdmin', () => {
  beforeEach(() => localStorage.clear())

  it('redirects non-admin authenticated user to /chat', () => {
    localStorage.setItem('dos68k:role', 'user')
    localStorage.setItem('dos68k:token', 'local-token-user')
    wrap(
      '/admin',
      <RequireAdmin><div>admin content</div></RequireAdmin>
    )
    expect(screen.getByText('chat page')).toBeInTheDocument()
    expect(screen.queryByText('admin content')).not.toBeInTheDocument()
  })

  it('renders children for admin user', () => {
    localStorage.setItem('dos68k:role', 'admin')
    localStorage.setItem('dos68k:token', 'local-token-admin')
    wrap(
      '/admin',
      <RequireAdmin><div>admin content</div></RequireAdmin>
    )
    expect(screen.getByText('admin content')).toBeInTheDocument()
  })

  it('redirects unauthenticated visitor to /login', () => {
    wrap(
      '/admin',
      <RequireAdmin><div>admin content</div></RequireAdmin>
    )
    expect(screen.getByText('login page')).toBeInTheDocument()
    expect(screen.queryByText('admin content')).not.toBeInTheDocument()
  })
})
