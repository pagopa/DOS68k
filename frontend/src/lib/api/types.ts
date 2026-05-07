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
