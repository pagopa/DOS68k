import { describe, it, expect, beforeEach } from 'vitest'
import { LocalAuthProvider } from './local-auth'

describe('LocalAuthProvider', () => {
  let auth: LocalAuthProvider

  beforeEach(() => {
    localStorage.clear()
    auth = new LocalAuthProvider()
  })

  it('starts unauthenticated', () => {
    expect(auth.isAuthenticated()).toBe(false)
    expect(auth.getUser()).toBeNull()
    expect(auth.getToken()).toBeNull()
  })

  it('login as user persists role and token to localStorage', () => {
    auth.login('user')
    expect(localStorage.getItem('dos68k:role')).toBe('user')
    expect(localStorage.getItem('dos68k:token')).not.toBeNull()
  })

  it('login as admin persists admin role to localStorage', () => {
    auth.login('admin')
    expect(localStorage.getItem('dos68k:role')).toBe('admin')
  })

  it('isAuthenticated returns true after login', () => {
    auth.login('user')
    expect(auth.isAuthenticated()).toBe(true)
  })

  it('getUser returns the persisted role after login', () => {
    auth.login('admin')
    expect(auth.getUser()).toEqual({ role: 'admin' })
  })

  it('getToken returns a non-empty string after login', () => {
    auth.login('user')
    expect(typeof auth.getToken()).toBe('string')
    expect(auth.getToken()!.length).toBeGreaterThan(0)
  })

  it('logout clears role and token from localStorage', () => {
    auth.login('user')
    auth.logout()
    expect(localStorage.getItem('dos68k:role')).toBeNull()
    expect(localStorage.getItem('dos68k:token')).toBeNull()
  })

  it('isAuthenticated returns false after logout', () => {
    auth.login('user')
    auth.logout()
    expect(auth.isAuthenticated()).toBe(false)
  })

  it('getUser returns null after logout', () => {
    auth.login('user')
    auth.logout()
    expect(auth.getUser()).toBeNull()
  })

  it('state is restored from localStorage on construction (survives reload)', () => {
    auth.login('admin')
    const newInstance = new LocalAuthProvider()
    expect(newInstance.isAuthenticated()).toBe(true)
    expect(newInstance.getUser()).toEqual({ role: 'admin' })
  })
})
