import { useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useAuth } from '@/lib/auth/use-auth'
import { createApiClient, ApiError } from '@/lib/api'
import type { CreateSessionInput } from '@/lib/api'

const SESSIONS_KEY = ['sessions'] as const

function useApiClient() {
  const { getToken, getUser } = useAuth()
  return useMemo(
    () => createApiClient(import.meta.env.VITE_API_BASE_URL ?? '', getToken, getUser),
    // getToken and getUser are stable useCallback refs from AuthContextProvider
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
