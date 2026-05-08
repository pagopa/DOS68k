import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { createApiClient, ApiError } from './index'
import type { SessionDTO, QueryResponseDTO } from './types'

const BASE = 'http://test-gateway'

const mockSession: SessionDTO = {
  id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  userId: 'user-uuid',
  title: 'Test Session',
  createdAt: '2024-01-15T10:00:00Z',
  expiresAt: null,
}

const mockQuery: QueryResponseDTO = {
  id: 'a1b2c3d4-0000-0000-0000-000000000001',
  sessionId: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
  question: 'What is DOS68K?',
  answer: 'DOS68K is a RAG chatbot platform.',
  badAnswer: false,
  topic: ['platform'],
  context: {
    'readme.md': [{ chunkId: 1, content: 'DOS68K is...', score: 0.92 }],
  },
  createdAt: '2024-01-15T10:05:00Z',
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

// ------- getQueries -------

describe('getQueries', () => {
  const SESSION_ID = 'f47ac10b-58cc-4372-a567-0e02b2c3d479'

  it('sends GET to /queries/{sessionId}', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json([mockQuery])
      })
    )
    await createApiClient(BASE, () => null, () => null).getQueries(SESSION_ID)
    expect(capturedMethod).toBe('GET')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => 'q-token', () => null).getQueries(SESSION_ID)
    expect(authHeader).toBe('Bearer q-token')
  })

  it('omits Authorization header when token is null', async () => {
    let authHeader: string | null = 'present'
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => null, () => null).getQueries(SESSION_ID)
    expect(authHeader).toBeNull()
  })

  it('parses response JSON into QueryResponseDTO[]', async () => {
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, () => HttpResponse.json([mockQuery]))
    )
    const queries = await createApiClient(BASE, () => null, () => null).getQueries(SESSION_ID)
    expect(queries).toEqual([mockQuery])
  })

  it('throws ApiError with correct status on 4xx', async () => {
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, () =>
        HttpResponse.json({ detail: 'Session not found' }, { status: 404 })
      )
    )
    const err = await createApiClient(BASE, () => null, () => null).getQueries(SESSION_ID).catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })

  it('throws ApiError with status 500 on 5xx', async () => {
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, () =>
        HttpResponse.json({ detail: 'Internal error' }, { status: 500 })
      )
    )
    const err = await createApiClient(BASE, () => null, () => null).getQueries(SESSION_ID).catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(500)
  })
})

// ------- createQuery -------

describe('createQuery', () => {
  const SESSION_ID = 'f47ac10b-58cc-4372-a567-0e02b2c3d479'

  it('sends POST to /queries/{sessionId}', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.post(`${BASE}/queries/${SESSION_ID}`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json(mockQuery, { status: 201 })
      })
    )
    await createApiClient(BASE, () => null, () => null).createQuery(SESSION_ID, {
      question: 'What is DOS68K?',
      sessionHistory: [],
    })
    expect(capturedMethod).toBe('POST')
  })

  it('sends body with camelCase alias field sessionHistory (not session_history)', async () => {
    let body: unknown
    server.use(
      http.post(`${BASE}/queries/${SESSION_ID}`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(mockQuery, { status: 201 })
      })
    )
    await createApiClient(BASE, () => null, () => null).createQuery(SESSION_ID, {
      question: 'Follow-up?',
      sessionHistory: [{ question: 'What is DOS68K?', answer: 'A RAG platform.' }],
    })
    expect(body).toMatchObject({ question: 'Follow-up?', sessionHistory: expect.any(Array) })
    expect(body).not.toHaveProperty('session_history')
  })

  it('sends sessionHistory entries with question and answer fields', async () => {
    let body: unknown
    server.use(
      http.post(`${BASE}/queries/${SESSION_ID}`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(mockQuery, { status: 201 })
      })
    )
    const history = [{ question: 'q1', answer: 'a1' }, { question: 'q2', answer: 'a2' }]
    await createApiClient(BASE, () => null, () => null).createQuery(SESSION_ID, {
      question: 'q3',
      sessionHistory: history,
    })
    expect((body as { sessionHistory: unknown[] }).sessionHistory).toEqual(history)
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.post(`${BASE}/queries/${SESSION_ID}`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json(mockQuery, { status: 201 })
      })
    )
    await createApiClient(BASE, () => 'q-tok', () => null).createQuery(SESSION_ID, {
      question: 'Q?',
      sessionHistory: [],
    })
    expect(authHeader).toBe('Bearer q-tok')
  })

  it('parses response JSON into QueryResponseDTO', async () => {
    server.use(
      http.post(`${BASE}/queries/${SESSION_ID}`, () => HttpResponse.json(mockQuery, { status: 201 }))
    )
    const result = await createApiClient(BASE, () => null, () => null).createQuery(SESSION_ID, {
      question: 'What is DOS68K?',
      sessionHistory: [],
    })
    expect(result).toEqual(mockQuery)
  })

  it('throws ApiError on non-2xx response', async () => {
    server.use(
      http.post(`${BASE}/queries/${SESSION_ID}`, () =>
        HttpResponse.json({ detail: 'Session not found' }, { status: 404 })
      )
    )
    const err = await createApiClient(BASE, () => null, () => null)
      .createQuery(SESSION_ID, { question: 'Q?', sessionHistory: [] })
      .catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })
})
