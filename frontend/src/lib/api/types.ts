export interface SessionDTO {
  id: string
  userId: string
  title: string
  createdAt: string
  expiresAt: string | null
}

export interface CreateSessionInput {
  title: string
  isTemporary: boolean
}

export interface HistoryEntry {
  question: string
  answer: string
}

export interface FileContext {
  chunkId: number
  content: string
  score: number | null
}

export interface QueryResponseDTO {
  id: string
  sessionId: string
  question: string
  answer: string
  badAnswer: boolean
  topic: string[]
  context: Record<string, FileContext[]>
  createdAt: string
  expiresAt: string | null
}

export interface CreateQueryInput {
  question: string
  sessionHistory: HistoryEntry[]
}

export interface CreateIndexResponse {
  indexId: string
  userId: string
  createdAt: string
}

export interface DocumentInfo {
  documentName: string
}

export interface UploadDocumentResponse {
  message: string
}

export interface HealthStatus {
  status: string
  service: string
  queue?: string
  storage?: string
  vector_db?: string
}

export class ApiError extends Error {
  readonly status: number
  readonly body?: unknown

  constructor(status: number, message: string, body?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}
