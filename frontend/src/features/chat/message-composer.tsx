import { useRef } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface MessageComposerProps {
  value: string
  onChange: (value: string) => void
  onSubmit: (question: string) => void
  isDisabled: boolean
}

export function MessageComposer({ value, onChange, onSubmit, isDisabled }: MessageComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  function submit() {
    const trimmed = value.trim()
    if (!trimmed || isDisabled) return
    onSubmit(trimmed)
  }

  return (
    <div className="border-t bg-card px-4 py-3 shadow-sm">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question… (Enter to send, Shift+Enter for newline)"
          disabled={isDisabled}
          rows={1}
          className="flex-1 resize-none rounded-md border border-border bg-secondary px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
          style={{ minHeight: '2.5rem', maxHeight: '8rem', overflowY: 'auto' }}
        />
        <Button
          onClick={submit}
          disabled={isDisabled || !value.trim()}
          size="icon"
          aria-label="Send message"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
