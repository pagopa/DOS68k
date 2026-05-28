import { useState } from 'react'

interface FeedbackButtonsProps {
  feedback: number
  onSubmit: (value: 1 | -1) => Promise<unknown>
}

export function FeedbackButtons({ feedback, onSubmit }: FeedbackButtonsProps) {
  const [value, setValue] = useState<number>(feedback)

  async function handleClick(next: 1 | -1) {
    const previous = value
    setValue(next)
    try {
      await onSubmit(next)
    } catch {
      setValue(previous)
    }
  }

  return (
    <div className="flex items-center gap-1">
      <button
        type="button"
        aria-label="Thumbs up"
        aria-pressed={value === 1}
        onClick={() => handleClick(1)}
        className={`px-1.5 py-0.5 text-sm rounded transition-colors ${
          value === 1 ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
        }`}
      >
        👍
      </button>
      <button
        type="button"
        aria-label="Thumbs down"
        aria-pressed={value === -1}
        onClick={() => handleClick(-1)}
        className={`px-1.5 py-0.5 text-sm rounded transition-colors ${
          value === -1 ? 'text-destructive' : 'text-muted-foreground hover:text-foreground'
        }`}
      >
        👎
      </button>
    </div>
  )
}
