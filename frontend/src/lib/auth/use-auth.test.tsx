import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthContextProvider } from './context'
import { useAuth } from './use-auth'

function TestConsumer() {
  const { user, isAuthenticated, login, logout } = useAuth()
  return (
    <div>
      <span data-testid="role">{user?.role ?? 'none'}</span>
      <span data-testid="auth">{isAuthenticated ? 'yes' : 'no'}</span>
      <button onClick={() => login('user')}>login user</button>
      <button onClick={() => login('admin')}>login admin</button>
      <button onClick={logout}>logout</button>
    </div>
  )
}

describe('useAuth', () => {
  beforeEach(() => localStorage.clear())

  it('starts unauthenticated', () => {
    render(
      <AuthContextProvider>
        <TestConsumer />
      </AuthContextProvider>
    )
    expect(screen.getByTestId('auth').textContent).toBe('no')
    expect(screen.getByTestId('role').textContent).toBe('none')
  })

  it('re-renders consumer after login', async () => {
    render(
      <AuthContextProvider>
        <TestConsumer />
      </AuthContextProvider>
    )
    await userEvent.click(screen.getByText('login user'))
    expect(screen.getByTestId('auth').textContent).toBe('yes')
    expect(screen.getByTestId('role').textContent).toBe('user')
  })

  it('re-renders consumer after login as admin', async () => {
    render(
      <AuthContextProvider>
        <TestConsumer />
      </AuthContextProvider>
    )
    await userEvent.click(screen.getByText('login admin'))
    expect(screen.getByTestId('role').textContent).toBe('admin')
  })

  it('re-renders consumer after logout', async () => {
    render(
      <AuthContextProvider>
        <TestConsumer />
      </AuthContextProvider>
    )
    await userEvent.click(screen.getByText('login user'))
    await userEvent.click(screen.getByText('logout'))
    expect(screen.getByTestId('auth').textContent).toBe('no')
    expect(screen.getByTestId('role').textContent).toBe('none')
  })
})
