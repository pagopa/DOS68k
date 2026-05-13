import { useState } from 'react'
import type { Source } from '@/lib/api'

interface SourcesProps {
  context?: Source[]
}

export function Sources({ context }: SourcesProps) {
  const [open, setOpen] = useState(false)

  if (!context || context.length === 0) return null

  return (
    <div className="mt-1.5 pl-1">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={`Sources (${context.length})`}
        className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors font-mono"
      >
        <span aria-hidden="true" className="text-primary/60">{open ? '▾' : '▸'}</span>
        <span>sources ({context.length})</span>
      </button>

      {open && (
        <div className="mt-2 space-y-2 border-l border-primary/20 pl-3">
          {context.map((source) => (
            <details key={`${source.filename}#${source.chunkId}`} className="text-xs">
              <summary className="cursor-pointer font-mono text-muted-foreground hover:text-foreground">
                {source.filename} <span className="text-primary/60">{source.score !== null ? source.score.toFixed(3) : '—'}</span>
              </summary>
              <p className="mt-1 pl-2 text-xs text-foreground/60 break-words whitespace-pre-wrap leading-relaxed">
                {source.content}
              </p>
            </details>
          ))}
        </div>
      )}
    </div>
  )
}
