import { ApiError } from './types'
import type {
  SessionDTO, CreateSessionInput, QueryResponseDTO, CreateQueryInput,
  CreateIndexResponse, HealthStatus,
} from './types'

export type GetToken = () => string | null
export type GetUser = () => { id: string; role: string } | null

async function doRequest<T>(
  baseUrl: string,
  path: string,
  getToken: GetToken,
  getUser: GetUser,
  init: RequestInit & { json?: unknown } = {}
): Promise<T> {
  const { json, ...rest } = init
  const headers: Record<string, string> = {}

  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const user = getUser()
  if (user) {
    headers['X-User-Id'] = user.id
    headers['X-User-Role'] = user.role
  }

  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    rest.body = JSON.stringify(json)
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

export function createApiClient(baseUrl: string, getToken: GetToken, getUser: GetUser) {
  const req = <T>(path: string, init?: RequestInit & { json?: unknown }) =>
    doRequest<T>(baseUrl, path, getToken, getUser, init)

  return {
    getSessions(): Promise<SessionDTO[]> {
      return req('/sessions')
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
    getIndexes(): Promise<string[]> {
      return req('/index/all')
    },
    createIndex(indexId: string): Promise<CreateIndexResponse> {
      return req(`/index/${indexId}`, { method: 'POST' })
    },
    deleteIndex(indexId: string): Promise<void> {
      return req(`/index/${indexId}`, { method: 'DELETE' })
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
