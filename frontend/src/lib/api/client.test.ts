import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { createApiClient, ApiError } from './index'
import type { SessionDTO } from './types'

const BASE = 'http://test-gateway'

const mockSession: SessionDTO = {
  id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  userId: 'user-uuid',
  title: 'Test Session',
  createdAt: '2024-01-15T10:00:00Z',
  expiresAt: null,
}

const server = setupServer()

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// ------- getSessions -------

describe('getSessions', () => {
  it('sends GET to /sessions', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.get(`${BASE}/sessions`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json([mockSession])
      })
    )
    await createApiClient(BASE, () => null, () => null).getSessions()
    expect(capturedMethod).toBe('GET')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.get(`${BASE}/sessions`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => 'my-token', () => null).getSessions()
    expect(authHeader).toBe('Bearer my-token')
  })

  it('omits Authorization header when token is null', async () => {
    let authHeader: string | null = 'present'
    server.use(
      http.get(`${BASE}/sessions`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => null, () => null).getSessions()
    expect(authHeader).toBeNull()
  })

  it('parses response JSON into SessionDTO[]', async () => {
    server.use(
      http.get(`${BASE}/sessions`, () => HttpResponse.json([mockSession]))
    )
    const sessions = await createApiClient(BASE, () => null, () => null).getSessions()
    expect(sessions).toEqual([mockSession])
  })

  it('throws ApiError with correct status on 4xx', async () => {
    server.use(
      http.get(`${BASE}/sessions`, () => HttpResponse.json({ detail: 'Not found' }, { status: 404 }))
    )
    const err = await createApiClient(BASE, () => null, () => null).getSessions().catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })

  it('throws ApiError with status 500 on 5xx (distinguishable from 4xx)', async () => {
    server.use(
      http.get(`${BASE}/sessions`, () => HttpResponse.json({ detail: 'Internal error' }, { status: 500 }))
    )
    const err = await createApiClient(BASE, () => null, () => null).getSessions().catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(500)
    expect(err.status >= 500).toBe(true)
  })
})

// ------- createSession -------

describe('createSession', () => {
  it('sends POST to /sessions', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.post(`${BASE}/sessions`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json(mockSession, { status: 201 })
      })
    )
    await createApiClient(BASE, () => null, () => null).createSession({ title: 'T', isTemporary: false })
    expect(capturedMethod).toBe('POST')
  })

  it('sends body with camelCase alias fields (isTemporary, not is_temporary)', async () => {
    let body: unknown
    server.use(
      http.post(`${BASE}/sessions`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(mockSession, { status: 201 })
      })
    )
    await createApiClient(BASE, () => null, () => null).createSession({ title: 'New', isTemporary: false })
    expect(body).toEqual({ title: 'New', isTemporary: false })
    expect(body).not.toHaveProperty('is_temporary')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.post(`${BASE}/sessions`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json(mockSession, { status: 201 })
      })
    )
    await createApiClient(BASE, () => 'tok', () => null).createSession({ title: 'T', isTemporary: false })
    expect(authHeader).toBe('Bearer tok')
  })

  it('parses response JSON into SessionDTO', async () => {
    server.use(
      http.post(`${BASE}/sessions`, () => HttpResponse.json(mockSession, { status: 201 }))
    )
    const session = await createApiClient(BASE, () => null, () => null).createSession({ title: 'T', isTemporary: false })
    expect(session).toEqual(mockSession)
  })

  it('throws ApiError on non-2xx response', async () => {
    server.use(
      http.post(`${BASE}/sessions`, () => HttpResponse.json({ detail: 'Bad request' }, { status: 400 }))
    )
    const err = await createApiClient(BASE, () => null, () => null)
      .createSession({ title: 'T', isTemporary: false })
      .catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(400)
  })
})

// ------- deleteSession -------

describe('deleteSession', () => {
  it('sends DELETE to /sessions/{id}', async () => {
    let capturedMethod: string | undefined
    let capturedUrl: string | undefined
    server.use(
      http.delete(`${BASE}/sessions/abc-uuid`, ({ request }) => {
        capturedMethod = request.method
        capturedUrl = request.url
        return new HttpResponse(null, { status: 204 })
      })
    )
    await createApiClient(BASE, () => null, () => null).deleteSession('abc-uuid')
    expect(capturedMethod).toBe('DELETE')
    expect(capturedUrl).toContain('/sessions/abc-uuid')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.delete(`${BASE}/sessions/abc-uuid`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return new HttpResponse(null, { status: 204 })
      })
    )
    await createApiClient(BASE, () => 'del-tok', () => null).deleteSession('abc-uuid')
    expect(authHeader).toBe('Bearer del-tok')
  })

  it('resolves to undefined on 204 No Content', async () => {
    server.use(
      http.delete(`${BASE}/sessions/abc-uuid`, () => new HttpResponse(null, { status: 204 }))
    )
    const result = await createApiClient(BASE, () => null, () => null).deleteSession('abc-uuid')
    expect(result).toBeUndefined()
  })

  it('throws ApiError with correct status on non-2xx', async () => {
    server.use(
      http.delete(`${BASE}/sessions/abc-uuid`, () => HttpResponse.json({ detail: 'Not found' }, { status: 404 }))
    )
    const err = await createApiClient(BASE, () => null, () => null).deleteSession('abc-uuid').catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })
})
