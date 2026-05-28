import { ApiError } from './types'
import type {
  SessionDTO, CreateSessionInput, QueryResponseDTO, CreateQueryInput,
  CreateIndexResponse, HealthStatus, DocumentInfo, UploadDocumentResponse,
} from './types'

export type GetToken = () => string | null

async function doRequest<T>(
  baseUrl: string,
  path: string,
  getToken: GetToken,
  init: RequestInit & { json?: unknown; form?: Record<string, string | number>; timeoutMs?: number } = {}
): Promise<T> {
  const { json, form, timeoutMs, ...rest } = init
  if (timeoutMs) rest.signal = AbortSignal.timeout(timeoutMs)
  const headers: Record<string, string> = {}

  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    rest.body = JSON.stringify(json)
  } else if (form !== undefined) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    rest.body = Object.entries(form)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join('&')
  }

  const res = await fetch(`${baseUrl}${path}`, {
    ...rest,
    headers: { ...headers, ...(rest.headers as Record<string, string> | undefined ?? {}) },
  })

  if (!res.ok) {
    let body: unknown
    try { body = await res.json() } catch { /* ignore */ }
    throw new ApiError(res.status, res.statusText, body)
  }

  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export function createApiClient(baseUrl: string, getToken: GetToken) {
  const req = <T>(
    path: string,
    init?: RequestInit & { json?: unknown; form?: Record<string, string | number> }
  ) => doRequest<T>(baseUrl, path, getToken, init)

  return {
    getSessions(): Promise<SessionDTO[]> {
      return req('/sessions/all')
    },
    createSession(input: CreateSessionInput): Promise<SessionDTO> {
      return req('/sessions', { method: 'POST', json: input })
    },
    deleteSession(id: string): Promise<void> {
      return req(`/sessions/${id}`, { method: 'DELETE' })
    },
    getQueries(sessionId: string): Promise<QueryResponseDTO[]> {
      return req(`/queries/${sessionId}`)
    },
    createQuery(sessionId: string, input: CreateQueryInput): Promise<QueryResponseDTO> {
      return req(`/queries/${sessionId}`, { method: 'POST', json: input })
    },
    submitFeedback(sessionId: string, queryId: string, value: 1 | -1): Promise<unknown> {
      return req(`/evaluate/simple-feedback/${sessionId}/${queryId}`, {
        method: 'POST',
        form: { feedback: value },
      })
    },
    evaluateQuery(sessionId: string, queryId: string): Promise<unknown> {
      return req(`/evaluate/${sessionId}/${queryId}`, { method: 'POST' })
    },
    getIndexes(): Promise<string[]> {
      return req('/index/all')
    },
    createIndex(indexId: string): Promise<CreateIndexResponse> {
      return req(`/index/${indexId}`, { method: 'POST' })
    },
    deleteIndex(indexId: string): Promise<void> {
      return req(`/index/${indexId}`, { method: 'DELETE' })
    },
    getDocuments(indexId: string): Promise<DocumentInfo[]> {
      return req(`/index/${indexId}/documents`)
    },
    uploadDocument(indexId: string, file: File): Promise<UploadDocumentResponse> {
      const formData = new FormData()
      formData.append('file', file)
      return req(`/index/${indexId}/documents`, { method: 'POST', body: formData })
    },
    deleteDocument(indexId: string, documentName: string): Promise<void> {
      return req(`/index/${indexId}/documents/${encodeURIComponent(documentName)}`, { method: 'DELETE' })
    },
    getHealthQueue(): Promise<HealthStatus> {
      return req('/health/queue')
    },
    getHealthStorage(): Promise<HealthStatus> {
      return req('/health/storage')
    },
    getHealthVdb(): Promise<HealthStatus> {
      return req('/health/vdb')
    },
  }
}

export type ApiClient = ReturnType<typeof createApiClient>
