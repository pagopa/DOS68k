import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { createApiClient, ApiError } from './index'
import type { SessionDTO, QueryResponseDTO, CreateIndexResponse, HealthStatus, DocumentInfo, UploadDocumentResponse } from './types'

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
  context: [{ chunkId: '1', content: 'DOS68K is...', score: 0.92, filename: 'readme.md' }],
  createdAt: '2024-01-15T10:05:00Z',
  expiresAt: null,
}

const server = setupServer()

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// ------- getSessions -------

describe('getSessions', () => {
  it('sends GET to /sessions/all', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.get(`${BASE}/sessions/all`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json([mockSession])
      })
    )
    await createApiClient(BASE, () => null).getSessions()
    expect(capturedMethod).toBe('GET')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.get(`${BASE}/sessions/all`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => 'my-token').getSessions()
    expect(authHeader).toBe('Bearer my-token')
  })

  it('omits Authorization header when token is null', async () => {
    let authHeader: string | null = 'present'
    server.use(
      http.get(`${BASE}/sessions/all`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => null).getSessions()
    expect(authHeader).toBeNull()
  })

  it('parses response JSON into SessionDTO[]', async () => {
    server.use(
      http.get(`${BASE}/sessions/all`, () => HttpResponse.json([mockSession]))
    )
    const sessions = await createApiClient(BASE, () => null).getSessions()
    expect(sessions).toEqual([mockSession])
  })

  it('throws ApiError with correct status on 4xx', async () => {
    server.use(
      http.get(`${BASE}/sessions/all`, () => HttpResponse.json({ detail: 'Not found' }, { status: 404 }))
    )
    const err = await createApiClient(BASE, () => null).getSessions().catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })

  it('throws ApiError with status 500 on 5xx (distinguishable from 4xx)', async () => {
    server.use(
      http.get(`${BASE}/sessions/all`, () => HttpResponse.json({ detail: 'Internal error' }, { status: 500 }))
    )
    const err = await createApiClient(BASE, () => null).getSessions().catch(e => e)
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
    await createApiClient(BASE, () => null).createSession({ title: 'T', isTemporary: false })
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
    await createApiClient(BASE, () => null).createSession({ title: 'New', isTemporary: false })
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
    await createApiClient(BASE, () => 'tok').createSession({ title: 'T', isTemporary: false })
    expect(authHeader).toBe('Bearer tok')
  })

  it('parses response JSON into SessionDTO', async () => {
    server.use(
      http.post(`${BASE}/sessions`, () => HttpResponse.json(mockSession, { status: 201 }))
    )
    const session = await createApiClient(BASE, () => null).createSession({ title: 'T', isTemporary: false })
    expect(session).toEqual(mockSession)
  })

  it('throws ApiError on non-2xx response', async () => {
    server.use(
      http.post(`${BASE}/sessions`, () => HttpResponse.json({ detail: 'Bad request' }, { status: 400 }))
    )
    const err = await createApiClient(BASE, () => null)
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
    await createApiClient(BASE, () => null).deleteSession('abc-uuid')
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
    await createApiClient(BASE, () => 'del-tok').deleteSession('abc-uuid')
    expect(authHeader).toBe('Bearer del-tok')
  })

  it('resolves to undefined on 204 No Content', async () => {
    server.use(
      http.delete(`${BASE}/sessions/abc-uuid`, () => new HttpResponse(null, { status: 204 }))
    )
    const result = await createApiClient(BASE, () => null).deleteSession('abc-uuid')
    expect(result).toBeUndefined()
  })

  it('throws ApiError with correct status on non-2xx', async () => {
    server.use(
      http.delete(`${BASE}/sessions/abc-uuid`, () => HttpResponse.json({ detail: 'Not found' }, { status: 404 }))
    )
    const err = await createApiClient(BASE, () => null).deleteSession('abc-uuid').catch(e => e)
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
    await createApiClient(BASE, () => null).getQueries(SESSION_ID)
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
    await createApiClient(BASE, () => 'q-token').getQueries(SESSION_ID)
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
    await createApiClient(BASE, () => null).getQueries(SESSION_ID)
    expect(authHeader).toBeNull()
  })

  it('parses response JSON into QueryResponseDTO[]', async () => {
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, () => HttpResponse.json([mockQuery]))
    )
    const queries = await createApiClient(BASE, () => null).getQueries(SESSION_ID)
    expect(queries).toEqual([mockQuery])
  })

  it('throws ApiError with correct status on 4xx', async () => {
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, () =>
        HttpResponse.json({ detail: 'Session not found' }, { status: 404 })
      )
    )
    const err = await createApiClient(BASE, () => null).getQueries(SESSION_ID).catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })

  it('throws ApiError with status 500 on 5xx', async () => {
    server.use(
      http.get(`${BASE}/queries/${SESSION_ID}`, () =>
        HttpResponse.json({ detail: 'Internal error' }, { status: 500 })
      )
    )
    const err = await createApiClient(BASE, () => null).getQueries(SESSION_ID).catch(e => e)
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
    await createApiClient(BASE, () => null).createQuery(SESSION_ID, {
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
    await createApiClient(BASE, () => null).createQuery(SESSION_ID, {
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
    await createApiClient(BASE, () => null).createQuery(SESSION_ID, {
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
    await createApiClient(BASE, () => 'q-tok').createQuery(SESSION_ID, {
      question: 'Q?',
      sessionHistory: [],
    })
    expect(authHeader).toBe('Bearer q-tok')
  })

  it('parses response JSON into QueryResponseDTO', async () => {
    server.use(
      http.post(`${BASE}/queries/${SESSION_ID}`, () => HttpResponse.json(mockQuery, { status: 201 }))
    )
    const result = await createApiClient(BASE, () => null).createQuery(SESSION_ID, {
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
    const err = await createApiClient(BASE, () => null)
      .createQuery(SESSION_ID, { question: 'Q?', sessionHistory: [] })
      .catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })
})

// ------- getIndexes -------

describe('getIndexes', () => {
  it('sends GET to /index/all', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.get(`${BASE}/index/all`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json(['idx-1', 'idx-2'])
      })
    )
    await createApiClient(BASE, () => null).getIndexes()
    expect(capturedMethod).toBe('GET')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.get(`${BASE}/index/all`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => 'idx-token').getIndexes()
    expect(authHeader).toBe('Bearer idx-token')
  })

  it('parses response JSON into string[]', async () => {
    server.use(
      http.get(`${BASE}/index/all`, () => HttpResponse.json(['idx-1', 'idx-2']))
    )
    const result = await createApiClient(BASE, () => null).getIndexes()
    expect(result).toEqual(['idx-1', 'idx-2'])
  })

  it('throws ApiError on non-2xx', async () => {
    server.use(
      http.get(`${BASE}/index/all`, () => HttpResponse.json({ detail: 'Forbidden' }, { status: 403 }))
    )
    const err = await createApiClient(BASE, () => null).getIndexes().catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(403)
  })
})

// ------- createIndex -------

const mockCreateIndexResponse: CreateIndexResponse = {
  indexId: 'my-index',
  userId: '00000000-0000-0000-0000-000000000002',
  createdAt: '2024-01-15T10:00:00Z',
}

describe('createIndex', () => {
  it('sends POST to /index/{indexId}', async () => {
    let capturedMethod: string | undefined
    let capturedUrl: string | undefined
    server.use(
      http.post(`${BASE}/index/my-index`, ({ request }) => {
        capturedMethod = request.method
        capturedUrl = request.url
        return HttpResponse.json(mockCreateIndexResponse, { status: 201 })
      })
    )
    await createApiClient(BASE, () => null).createIndex('my-index')
    expect(capturedMethod).toBe('POST')
    expect(capturedUrl).toContain('/index/my-index')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.post(`${BASE}/index/my-index`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json(mockCreateIndexResponse, { status: 201 })
      })
    )
    await createApiClient(BASE, () => 'admin-tok').createIndex('my-index')
    expect(authHeader).toBe('Bearer admin-tok')
  })

  it('parses response into CreateIndexResponse with camelCase aliases', async () => {
    server.use(
      http.post(`${BASE}/index/my-index`, () => HttpResponse.json(mockCreateIndexResponse, { status: 201 }))
    )
    const result = await createApiClient(BASE, () => null).createIndex('my-index')
    expect(result).toEqual(mockCreateIndexResponse)
    expect(result).toHaveProperty('indexId', 'my-index')
    expect(result).toHaveProperty('userId')
    expect(result).not.toHaveProperty('index_id')
  })

  it('throws ApiError with status 409 on duplicate index', async () => {
    server.use(
      http.post(`${BASE}/index/dup`, () => HttpResponse.json({ detail: 'Index already exists' }, { status: 409 }))
    )
    const err = await createApiClient(BASE, () => null).createIndex('dup').catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(409)
  })

  it('throws ApiError on other non-2xx', async () => {
    server.use(
      http.post(`${BASE}/index/fail`, () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    )
    const err = await createApiClient(BASE, () => null).createIndex('fail').catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(500)
  })
})

// ------- deleteIndex -------

describe('deleteIndex', () => {
  it('sends DELETE to /index/{indexId}', async () => {
    let capturedMethod: string | undefined
    let capturedUrl: string | undefined
    server.use(
      http.delete(`${BASE}/index/my-index`, ({ request }) => {
        capturedMethod = request.method
        capturedUrl = request.url
        return HttpResponse.json({ message: "Index 'my-index' deleted successfully" })
      })
    )
    await createApiClient(BASE, () => null).deleteIndex('my-index')
    expect(capturedMethod).toBe('DELETE')
    expect(capturedUrl).toContain('/index/my-index')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.delete(`${BASE}/index/my-index`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json({ message: 'deleted' })
      })
    )
    await createApiClient(BASE, () => 'del-tok').deleteIndex('my-index')
    expect(authHeader).toBe('Bearer del-tok')
  })

  it('throws ApiError with status 404 when index not found', async () => {
    server.use(
      http.delete(`${BASE}/index/ghost`, () => HttpResponse.json({ detail: 'Not found' }, { status: 404 }))
    )
    const err = await createApiClient(BASE, () => null).deleteIndex('ghost').catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })
})

// ------- health endpoints -------

const mockHealth: HealthStatus = { status: 'ok', service: 'Chatbot Index API' }

describe('getHealthQueue', () => {
  it('sends GET to /health/queue', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.get(`${BASE}/health/queue`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json({ ...mockHealth, queue: 'connected' })
      })
    )
    await createApiClient(BASE, () => null).getHealthQueue()
    expect(capturedMethod).toBe('GET')
  })

  it('parses response into HealthStatus', async () => {
    server.use(
      http.get(`${BASE}/health/queue`, () => HttpResponse.json({ ...mockHealth, queue: 'connected' }))
    )
    const result = await createApiClient(BASE, () => null).getHealthQueue()
    expect(result).toMatchObject({ status: 'ok', queue: 'connected' })
  })

  it('throws ApiError on non-2xx', async () => {
    server.use(
      http.get(`${BASE}/health/queue`, () => HttpResponse.json({ detail: 'error' }, { status: 503 }))
    )
    const err = await createApiClient(BASE, () => null).getHealthQueue().catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(503)
  })
})

describe('getHealthStorage', () => {
  it('sends GET to /health/storage', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.get(`${BASE}/health/storage`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json({ ...mockHealth, storage: 'connected' })
      })
    )
    await createApiClient(BASE, () => null).getHealthStorage()
    expect(capturedMethod).toBe('GET')
  })

  it('parses response into HealthStatus', async () => {
    server.use(
      http.get(`${BASE}/health/storage`, () => HttpResponse.json({ ...mockHealth, storage: 'connected' }))
    )
    const result = await createApiClient(BASE, () => null).getHealthStorage()
    expect(result).toMatchObject({ status: 'ok', storage: 'connected' })
  })

  it('throws ApiError on non-2xx', async () => {
    server.use(
      http.get(`${BASE}/health/storage`, () => HttpResponse.json({ detail: 'error' }, { status: 503 }))
    )
    const err = await createApiClient(BASE, () => null).getHealthStorage().catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(503)
  })
})

describe('getHealthVdb', () => {
  it('sends GET to /health/vdb', async () => {
    let capturedMethod: string | undefined
    server.use(
      http.get(`${BASE}/health/vdb`, ({ request }) => {
        capturedMethod = request.method
        return HttpResponse.json({ ...mockHealth, vector_db: 'connected' })
      })
    )
    await createApiClient(BASE, () => null).getHealthVdb()
    expect(capturedMethod).toBe('GET')
  })

  it('parses response into HealthStatus', async () => {
    server.use(
      http.get(`${BASE}/health/vdb`, () => HttpResponse.json({ ...mockHealth, vector_db: 'connected' }))
    )
    const result = await createApiClient(BASE, () => null).getHealthVdb()
    expect(result).toMatchObject({ status: 'ok', vector_db: 'connected' })
  })

  it('throws ApiError on non-2xx', async () => {
    server.use(
      http.get(`${BASE}/health/vdb`, () => HttpResponse.json({ detail: 'error' }, { status: 503 }))
    )
    const err = await createApiClient(BASE, () => null).getHealthVdb().catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(503)
  })
})

// ------- getDocuments -------

const mockDocuments: DocumentInfo[] = [
  { documentName: 'readme.pdf' },
  { documentName: 'guide.md' },
]

describe('getDocuments', () => {
  it('sends GET to /index/{indexId}/documents', async () => {
    let capturedMethod: string | undefined
    let capturedUrl: string | undefined
    server.use(
      http.get(`${BASE}/index/my-index/documents`, ({ request }) => {
        capturedMethod = request.method
        capturedUrl = request.url
        return HttpResponse.json(mockDocuments)
      })
    )
    await createApiClient(BASE, () => null).getDocuments('my-index')
    expect(capturedMethod).toBe('GET')
    expect(capturedUrl).toContain('/index/my-index/documents')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.get(`${BASE}/index/my-index/documents`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json([])
      })
    )
    await createApiClient(BASE, () => 'doc-token').getDocuments('my-index')
    expect(authHeader).toBe('Bearer doc-token')
  })

  it('parses response JSON into DocumentInfo[]', async () => {
    server.use(
      http.get(`${BASE}/index/my-index/documents`, () => HttpResponse.json(mockDocuments))
    )
    const result = await createApiClient(BASE, () => null).getDocuments('my-index')
    expect(result).toEqual(mockDocuments)
    expect(result[0]).toHaveProperty('documentName', 'readme.pdf')
  })

  it('throws ApiError on non-2xx', async () => {
    server.use(
      http.get(`${BASE}/index/no-such/documents`, () =>
        HttpResponse.json({ detail: 'Not found' }, { status: 404 })
      )
    )
    const err = await createApiClient(BASE, () => null).getDocuments('no-such').catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })
})

// ------- uploadDocument -------

const mockUploadResponse: UploadDocumentResponse = { message: 'Upload accepted' }

describe('uploadDocument', () => {
  it('sends POST to /index/{indexId}/documents', async () => {
    let capturedMethod: string | undefined
    let capturedUrl: string | undefined
    server.use(
      http.post(`${BASE}/index/my-index/documents`, ({ request }) => {
        capturedMethod = request.method
        capturedUrl = request.url
        return HttpResponse.json(mockUploadResponse, { status: 202 })
      })
    )
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    await createApiClient(BASE, () => null).uploadDocument('my-index', file)
    expect(capturedMethod).toBe('POST')
    expect(capturedUrl).toContain('/index/my-index/documents')
  })

  it('sends multipart FormData with a file field', async () => {
    let capturedFileField: FormDataEntryValue | null = null
    server.use(
      http.post(`${BASE}/index/my-index/documents`, async ({ request }) => {
        const fd = await request.formData()
        capturedFileField = fd.get('file')
        return HttpResponse.json(mockUploadResponse, { status: 202 })
      })
    )
    const file = new File(['pdf bytes'], 'report.pdf', { type: 'application/pdf' })
    await createApiClient(BASE, () => null).uploadDocument('my-index', file)
    expect(capturedFileField).not.toBeNull()
    expect((capturedFileField as unknown as File).size).toBeGreaterThan(0)
  })

  it('does not set Content-Type: application/json (lets browser set multipart boundary)', async () => {
    let contentType: string | null = null
    server.use(
      http.post(`${BASE}/index/my-index/documents`, ({ request }) => {
        contentType = request.headers.get('Content-Type')
        return HttpResponse.json(mockUploadResponse, { status: 202 })
      })
    )
    const file = new File(['data'], 'file.md', { type: 'text/markdown' })
    await createApiClient(BASE, () => null).uploadDocument('my-index', file)
    expect(contentType).not.toBe('application/json')
    expect(contentType).toContain('multipart/form-data')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.post(`${BASE}/index/my-index/documents`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return HttpResponse.json(mockUploadResponse, { status: 202 })
      })
    )
    const file = new File(['x'], 'x.txt', { type: 'text/plain' })
    await createApiClient(BASE, () => 'upload-tok').uploadDocument('my-index', file)
    expect(authHeader).toBe('Bearer upload-tok')
  })

  it('parses 202 response into UploadDocumentResponse', async () => {
    server.use(
      http.post(`${BASE}/index/my-index/documents`, () =>
        HttpResponse.json(mockUploadResponse, { status: 202 })
      )
    )
    const file = new File(['x'], 'x.pdf', { type: 'application/pdf' })
    const result = await createApiClient(BASE, () => null).uploadDocument('my-index', file)
    expect(result).toEqual(mockUploadResponse)
  })

  it('throws ApiError with status 415 on unsupported media type', async () => {
    server.use(
      http.post(`${BASE}/index/my-index/documents`, () =>
        HttpResponse.json({ detail: 'Unsupported media type' }, { status: 415 })
      )
    )
    const file = new File(['x'], 'x.zip', { type: 'application/zip' })
    const err = await createApiClient(BASE, () => null)
      .uploadDocument('my-index', file)
      .catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(415)
  })

  it('throws ApiError on other non-2xx', async () => {
    server.use(
      http.post(`${BASE}/index/my-index/documents`, () =>
        HttpResponse.json({ detail: 'Server error' }, { status: 500 })
      )
    )
    const file = new File(['x'], 'x.pdf', { type: 'application/pdf' })
    const err = await createApiClient(BASE, () => null)
      .uploadDocument('my-index', file)
      .catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(500)
  })
})

// ------- deleteDocument -------

describe('deleteDocument', () => {
  it('sends DELETE to /index/{indexId}/documents/{documentName}', async () => {
    let capturedMethod: string | undefined
    let capturedUrl: string | undefined
    server.use(
      http.delete(`${BASE}/index/my-index/documents/readme.pdf`, ({ request }) => {
        capturedMethod = request.method
        capturedUrl = request.url
        return new HttpResponse(null, { status: 204 })
      })
    )
    await createApiClient(BASE, () => null).deleteDocument('my-index', 'readme.pdf')
    expect(capturedMethod).toBe('DELETE')
    expect(capturedUrl).toContain('/index/my-index/documents/readme.pdf')
  })

  it('sends Authorization header when token is present', async () => {
    let authHeader: string | null = null
    server.use(
      http.delete(`${BASE}/index/my-index/documents/readme.pdf`, ({ request }) => {
        authHeader = request.headers.get('Authorization')
        return new HttpResponse(null, { status: 204 })
      })
    )
    await createApiClient(BASE, () => 'del-doc-tok').deleteDocument('my-index', 'readme.pdf')
    expect(authHeader).toBe('Bearer del-doc-tok')
  })

  it('resolves to undefined on 204 No Content', async () => {
    server.use(
      http.delete(`${BASE}/index/my-index/documents/readme.pdf`, () =>
        new HttpResponse(null, { status: 204 })
      )
    )
    const result = await createApiClient(BASE, () => null).deleteDocument('my-index', 'readme.pdf')
    expect(result).toBeUndefined()
  })

  it('throws ApiError with status 404 when document not found', async () => {
    server.use(
      http.delete(`${BASE}/index/my-index/documents/ghost.pdf`, () =>
        HttpResponse.json({ detail: 'Not found' }, { status: 404 })
      )
    )
    const err = await createApiClient(BASE, () => null)
      .deleteDocument('my-index', 'ghost.pdf')
      .catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(404)
  })

  it('throws ApiError on other non-2xx', async () => {
    server.use(
      http.delete(`${BASE}/index/my-index/documents/readme.pdf`, () =>
        HttpResponse.json({ detail: 'Error' }, { status: 500 })
      )
    )
    const err = await createApiClient(BASE, () => null)
      .deleteDocument('my-index', 'readme.pdf')
      .catch(e => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(500)
  })
})
