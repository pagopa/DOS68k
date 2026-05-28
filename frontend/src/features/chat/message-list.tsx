import { useEffect, useMemo, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { QueryResponseDTO, Scores } from '@/lib/api'
import { Sources } from './sources'
import { FeedbackButtons } from './feedback-buttons'
import { AnswerAdminActions } from './answer-admin-actions'
import { ScoresBadges, type EvaluationStatus } from './scores-badges'
import { useEvaluationPolling } from './use-evaluation-polling'
import {
  useSubmitFeedback,
  useEvaluateQuery,
  useGetQueries,
  useInvalidateQueries,
} from './hooks'

interface PendingEntry {
  question: string
  isWaiting: boolean
}

interface MessageListProps {
  sessionId: string
  queries: QueryResponseDTO[]
  pending: PendingEntry | null
}

function QuestionBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[75%] rounded-lg rounded-tr-sm bg-primary px-4 py-2.5 text-sm font-500 text-primary-foreground leading-relaxed">
        {text}
      </div>
    </div>
  )
}

function AnswerBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[75%] rounded-lg rounded-tl-sm border border-border bg-card px-4 py-3 prose max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
      </div>
    </div>
  )
}

function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-1.5 rounded-lg rounded-tl-sm border border-border bg-card px-4 py-3.5">
        <span className="h-2 w-2 animate-bounce rounded-full bg-primary/40 [animation-delay:-0.3s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-primary/40 [animation-delay:-0.15s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-primary/40" />
      </div>
    </div>
  )
}

export function MessageList({ sessionId, queries, pending }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const submitFeedback = useSubmitFeedback(sessionId)
  const evaluateQuery = useEvaluateQuery(sessionId)
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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [queries.length, pending])

  const sorted = useMemo(
    () => [...queries].sort((a, b) => a.createdAt.localeCompare(b.createdAt)),
    [queries]
  )

  function startEvaluation(queryId: string) {
    setFailedIds((prev) => {
      if (!prev.has(queryId)) return prev
      const next = new Set(prev)
      next.delete(queryId)
      return next
    })
    setPendingIds((prev) => (prev.includes(queryId) ? prev : [...prev, queryId]))
    evaluateQuery.mutate(queryId, {
      onError: () => setPendingIds((prev) => prev.filter((p) => p !== queryId)),
    })
  }

  function statusFor(q: QueryResponseDTO): EvaluationStatus {
    if (pendingIds.includes(q.id)) return 'pending'
    if (failedIds.has(q.id)) return 'failed'
    if (q.isEvaluated && q.scores) return 'resolved'
    if (q.isEvaluated && !q.scores) return 'failed'
    return 'idle'
  }

  function scoresFor(q: QueryResponseDTO): Scores | null {
    return q.scores
  }

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
      {sorted.map((q) => (
        <div key={q.id} className="flex flex-col gap-2">
          <QuestionBubble text={q.question} />
          <AnswerBubble text={q.answer} />
          <div className="flex items-center justify-between">
            <Sources context={q.context} />
            <div className="flex items-center gap-2">
              <ScoresBadges
                status={statusFor(q)}
                scores={scoresFor(q)}
                onRetry={() => startEvaluation(q.id)}
              />
              <FeedbackButtons
                feedback={q.feedback}
                onSubmit={(value) =>
                  submitFeedback.mutateAsync({ queryId: q.id, value })
                }
              />
              <AnswerAdminActions
                isEvaluated={q.isEvaluated}
                onEvaluate={() => startEvaluation(q.id)}
              />
            </div>
          </div>
        </div>
      ))}

      {pending && (
        <div className="flex flex-col gap-2">
          <QuestionBubble text={pending.question} />
          {pending.isWaiting ? <ThinkingIndicator /> : null}
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
