import { useState } from 'react'
import type { Source } from '@/lib/api'

interface SourcesProps {
  context?: Source[]
}

export function Sources({ context }: SourcesProps) {
  const [open, setOpen] = useState(false)

  if (!context || context.length === 0) return null

  return (
    <div className="mt-1 pl-1">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={`Sources (${context.length})`}
        className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <span aria-hidden="true">{open ? '▾' : '▸'}</span>
        <span>Sources ({context.length})</span>
      </button>

      {open && (
        <div className="mt-2 space-y-2 border-l pl-3">
          {context.map((source) => (
            <details key={`${source.filename}#${source.chunkId}`} className="text-xs">
              <summary className="cursor-pointer font-medium text-muted-foreground hover:text-foreground">
                {source.filename} — {source.score !== null ? source.score.toFixed(3) : '—'}
              </summary>
              <p className="mt-1 pl-2 text-xs text-foreground/80 break-words whitespace-pre-wrap">
                {source.content}
              </p>
            </details>
          ))}
        </div>
      )}
    </div>
  )
}
