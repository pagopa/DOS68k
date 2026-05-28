import { useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useAuth } from '@/lib/auth/use-auth'
import { createApiClient, ApiError } from '@/lib/api'
import type { CreateSessionInput, CreateQueryInput } from '@/lib/api'

const SESSIONS_KEY = ['sessions'] as const
const queriesKey = (sessionId: string) => ['queries', sessionId] as const

function useApiClient() {
  const { getToken } = useAuth()
  return useMemo(
    () => createApiClient(import.meta.env.VITE_API_BASE_URL ?? '', getToken),
    // getToken is a stable useCallback ref from AuthContextProvider
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )
}

export function useSessions() {
  const client = useApiClient()
  return useQuery({
    queryKey: SESSIONS_KEY,
    queryFn: () => client.getSessions(),
  })
}

export function useCreateSession() {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: (input: CreateSessionInput) => client.createSession(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: SESSIONS_KEY }),
    onError: (err) => {
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Failed to create session'
      toast.error(message)
    },
  })
}

export function useDeleteSession() {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: (id: string) => client.deleteSession(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: SESSIONS_KEY }),
    onError: (err) => {
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Failed to delete session'
      toast.error(message)
    },
  })
}

export function useQueries(sessionId: string, enabled = true) {
  const client = useApiClient()
  return useQuery({
    queryKey: queriesKey(sessionId),
    queryFn: () => client.getQueries(sessionId),
    enabled: !!sessionId && enabled,
  })
}

export function useSubmitFeedback(sessionId: string) {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: ({ queryId, value }: { queryId: string; value: 1 | -1 }) =>
      client.submitFeedback(sessionId, queryId, value),
    onSuccess: () => qc.invalidateQueries({ queryKey: queriesKey(sessionId) }),
    onError: (err) => {
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Failed to submit feedback'
      toast.error(message)
    },
  })
}

export function useCreateQuery(sessionId: string) {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: (input: CreateQueryInput) => client.createQuery(sessionId, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: queriesKey(sessionId) }),
    onError: (err) => {
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Failed to get answer'
      toast.error(message)
    },
  })
}
