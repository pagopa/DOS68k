import { useState } from 'react'
import { useQueries, useCreateQuery } from './hooks'
import { MessageList } from './message-list'
import { MessageComposer } from './message-composer'
import type { QueryResponseDTO } from '@/lib/api'

interface ChatViewProps {
  sessionId: string
}

export function ChatView({ sessionId }: ChatViewProps) {
  const [draft, setDraft] = useState('')
  const [pending, setPending] = useState<{ question: string; isWaiting: boolean } | null>(null)

  const { data: queries = [] } = useQueries(sessionId)
  const mutation = useCreateQuery(sessionId)

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
      <MessageList queries={queries} pending={pending} />
      <MessageComposer
        value={draft}
        onChange={setDraft}
        onSubmit={handleSubmit}
        isDisabled={mutation.isPending}
      />
    </div>
  )
}
