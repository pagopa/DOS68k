import { useState } from 'react'
import {
  useQueries,
  useCreateQuery,
  useEvaluateQuery,
  useEvaluateRated,
  useGetQueries,
  useInvalidateQueries,
} from './hooks'
import { MessageList } from './message-list'
import { MessageComposer } from './message-composer'
import { EvaluateSessionButton } from './evaluate-session-button'
import { useEvaluationPolling } from './use-evaluation-polling'
import type { QueryResponseDTO } from '@/lib/api'

interface ChatViewProps {
  sessionId: string
}

export function ChatView({ sessionId }: ChatViewProps) {
  const [draft, setDraft] = useState('')
  const [pending, setPending] = useState<{ question: string; isWaiting: boolean } | null>(null)

  const mutation = useCreateQuery(sessionId)
  const { data: queries = [] } = useQueries(sessionId, !mutation.isPending)

  const evaluateQuery = useEvaluateQuery(sessionId)
  const evaluateRated = useEvaluateRated(sessionId)
  const getQueries = useGetQueries()
  const invalidateQueries = useInvalidateQueries(sessionId)

  const [pendingIds, setPendingIds] = useState<string[]>([])
  const [failedIds, setFailedIds] = useState<Set<string>>(new Set())

  useEvaluationPolling({
    sessionId,
    pendingQueryIds: pendingIds,
    getQueries,
    onResolved: (id) => {
      setPendingIds((prev) => prev.filter((p) => p !== id))
      setFailedIds((prev) => {
        if (!prev.has(id)) return prev
        const next = new Set(prev)
        next.delete(id)
        return next
      })
      invalidateQueries()
    },
    onFailed: (id) => {
      setPendingIds((prev) => prev.filter((p) => p !== id))
      setFailedIds((prev) => new Set(prev).add(id))
    },
  })

  function clearFailed(id: string) {
    setFailedIds((prev) => {
      if (!prev.has(id)) return prev
      const next = new Set(prev)
      next.delete(id)
      return next
    })
  }

  function startEvaluation(queryId: string) {
    clearFailed(queryId)
    setPendingIds((prev) => (prev.includes(queryId) ? prev : [...prev, queryId]))
    evaluateQuery.mutate(queryId, {
      onError: () => setPendingIds((prev) => prev.filter((p) => p !== queryId)),
    })
  }

  function evaluateRatedAnswers() {
    evaluateRated.mutate(undefined, {
      onSuccess: (response) => {
        const ids = response.evaluations.map((e) => e.queryId)
        if (ids.length === 0) return
        ids.forEach(clearFailed)
        setPendingIds((prev) => {
          const next = new Set(prev)
          ids.forEach((id) => next.add(id))
          return Array.from(next)
        })
      },
    })
  }

  function buildHistory(currentQueries: QueryResponseDTO[]) {
    return [...currentQueries]
      .sort((a, b) => a.createdAt.localeCompare(b.createdAt))
      .map((q) => ({ question: q.question, answer: q.answer }))
  }

  function handleSubmit(question: string) {
    setPending({ question, isWaiting: true })
    setDraft('')

    mutation.mutate(
      { question, sessionHistory: buildHistory(queries) },
      {
        onSuccess: () => {
          setPending(null)
        },
        onError: () => {
          setPending({ question, isWaiting: false })
          setDraft(question)
        },
      }
    )
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex items-center justify-end border-b border-border bg-background px-4 py-2">
        <EvaluateSessionButton
          onClick={evaluateRatedAnswers}
          isPending={evaluateRated.isPending}
        />
      </div>
      <MessageList
        sessionId={sessionId}
        queries={queries}
        pending={pending}
        pendingIds={pendingIds}
        failedIds={failedIds}
        onStartEvaluation={startEvaluation}
      />
      <MessageComposer
        value={draft}
        onChange={setDraft}
        onSubmit={handleSubmit}
        isDisabled={mutation.isPending}
      />
    </div>
  )
}
