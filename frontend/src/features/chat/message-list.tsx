import { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { QueryResponseDTO } from '@/lib/api'
import { Sources } from './sources'

interface PendingEntry {
  question: string
  isWaiting: boolean
}

interface MessageListProps {
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

export function MessageList({ queries, pending }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [queries.length, pending])

  const sorted = [...queries].sort((a, b) => a.createdAt.localeCompare(b.createdAt))

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
      {sorted.map((q) => (
        <div key={q.id} className="flex flex-col gap-2">
          <QuestionBubble text={q.question} />
          <AnswerBubble text={q.answer} />
          <Sources context={q.context} />
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
