import { useEffect, useRef } from 'react'
import type { QueryResponseDTO, Scores } from '@/lib/api'

const POLL_INTERVAL_MS = 5_000
const TIMEOUT_MS = 120_000

interface UseEvaluationPollingArgs {
  sessionId: string
  pendingQueryIds: string[]
  getQueries: (sessionId: string) => Promise<QueryResponseDTO[]>
  onResolved: (queryId: string, scores: Scores) => void
  onFailed: (queryId: string) => void
}

export function useEvaluationPolling({
  sessionId,
  pendingQueryIds,
  getQueries,
  onResolved,
  onFailed,
}: UseEvaluationPollingArgs) {
  const startedAtRef = useRef<Map<string, number>>(new Map())
  const callbacksRef = useRef({ onResolved, onFailed, getQueries })
  callbacksRef.current = { onResolved, onFailed, getQueries }

  // Track when each pending id was first seen, so per-query deadlines survive re-renders.
  for (const id of pendingQueryIds) {
    if (!startedAtRef.current.has(id)) {
      startedAtRef.current.set(id, Date.now())
    }
  }
  for (const id of Array.from(startedAtRef.current.keys())) {
    if (!pendingQueryIds.includes(id)) startedAtRef.current.delete(id)
  }

  const pendingKey = pendingQueryIds.slice().sort().join(',')

  useEffect(() => {
    if (pendingQueryIds.length === 0) return

    let cancelled = false

    const tick = async () => {
      let queries: QueryResponseDTO[]
      try {
        queries = await callbacksRef.current.getQueries(sessionId)
      } catch {
        return
      }
      if (cancelled) return

      const byId = new Map(queries.map((q) => [q.id, q]))
      const now = Date.now()
      for (const id of pendingQueryIds) {
        const q = byId.get(id)
        if (q?.isEvaluated) {
          if (q.scores) callbacksRef.current.onResolved(id, q.scores)
          else callbacksRef.current.onFailed(id)
          continue
        }
        const startedAt = startedAtRef.current.get(id) ?? now
        if (now - startedAt >= TIMEOUT_MS) {
          callbacksRef.current.onFailed(id)
        }
      }
    }

    const timer = setInterval(tick, POLL_INTERVAL_MS)
    return () => {
      cancelled = true
      clearInterval(timer)
    }
    // pendingKey captures membership changes; sessionId triggers re-arm on session switch.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingKey, sessionId])
}
