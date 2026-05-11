import { useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useAuth } from '@/lib/auth/use-auth'
import { createApiClient, ApiError } from '@/lib/api'

const INDEXES_KEY = ['indexes'] as const
const documentsKey = (indexId: string) => ['documents', indexId] as const

function useApiClient() {
  const { getToken, getUser } = useAuth()
  return useMemo(
    () => createApiClient(import.meta.env.VITE_API_BASE_URL ?? '', getToken, getUser),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )
}

export function useIndexes() {
  const client = useApiClient()
  return useQuery({
    queryKey: INDEXES_KEY,
    queryFn: () => client.getIndexes(),
  })
}

export function useCreateIndex() {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: (indexId: string) => client.createIndex(indexId),
    onSuccess: () => qc.invalidateQueries({ queryKey: INDEXES_KEY }),
    onError: (err) => {
      if (err instanceof ApiError && err.status === 409) return
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Failed to create index'
      toast.error(message)
    },
  })
}

export function useDeleteIndex() {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: (indexId: string) => client.deleteIndex(indexId),
    onSuccess: () => qc.invalidateQueries({ queryKey: INDEXES_KEY }),
    onError: (err) => {
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Failed to delete index'
      toast.error(message)
    },
  })
}

export function useDocuments(indexId: string) {
  const client = useApiClient()
  return useQuery({
    queryKey: documentsKey(indexId),
    queryFn: () => client.getDocuments(indexId),
    enabled: !!indexId,
  })
}

export function useUploadDocument(indexId: string) {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: (file: File) => client.uploadDocument(indexId, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: documentsKey(indexId) }),
    onError: (err) => {
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Upload failed'
      toast.error(message)
    },
  })
}

export function useDeleteDocument(indexId: string) {
  const qc = useQueryClient()
  const client = useApiClient()
  return useMutation({
    mutationFn: (documentName: string) => client.deleteDocument(indexId, documentName),
    onSuccess: () => qc.invalidateQueries({ queryKey: documentsKey(indexId) }),
    onError: (err) => {
      const message = err instanceof ApiError ? `${err.status}: ${err.message}` : 'Failed to delete document'
      toast.error(message)
    },
  })
}

export function useHealthQueue() {
  const client = useApiClient()
  return useQuery({
    queryKey: ['health', 'queue'] as const,
    queryFn: () => client.getHealthQueue(),
    refetchInterval: 10_000,
    retry: false,
  })
}

export function useHealthStorage() {
  const client = useApiClient()
  return useQuery({
    queryKey: ['health', 'storage'] as const,
    queryFn: () => client.getHealthStorage(),
    refetchInterval: 10_000,
    retry: false,
  })
}

export function useHealthVdb() {
  const client = useApiClient()
  return useQuery({
    queryKey: ['health', 'vdb'] as const,
    queryFn: () => client.getHealthVdb(),
    refetchInterval: 10_000,
    retry: false,
  })
}
