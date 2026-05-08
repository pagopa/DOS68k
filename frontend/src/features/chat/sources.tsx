import { useState } from 'react'
import type { FileContext } from '@/lib/api'

interface SourcesProps {
  context?: Record<string, FileContext[]>
}

export function Sources({ context }: SourcesProps) {
  const [open, setOpen] = useState(false)

  if (!context || Object.keys(context).length === 0) return null

  const totalChunks = Object.values(context).reduce((sum, chunks) => sum + chunks.length, 0)
  const sortedDocs = Object.keys(context).sort()

  return (
    <div className="mt-1 pl-1">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={`Sources (${totalChunks})`}
        className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <span aria-hidden="true">{open ? '▾' : '▸'}</span>
        <span>Sources ({totalChunks})</span>
      </button>

      {open && (
        <div className="mt-2 space-y-2 border-l pl-3">
          {sortedDocs.map((docName) => (
            <details key={docName} className="text-xs">
              <summary className="cursor-pointer font-medium text-muted-foreground hover:text-foreground">
                {docName}
              </summary>
              <ul className="mt-1 space-y-2 pl-2">
                {context[docName].map((chunk) => (
                  <li key={chunk.chunkId} className="border-l pl-2 py-0.5">
                    <p className="text-xs text-foreground/80 break-words whitespace-pre-wrap">
                      {chunk.content}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Score: {chunk.score !== null ? chunk.score.toFixed(3) : '—'}
                    </p>
                  </li>
                ))}
              </ul>
            </details>
          ))}
        </div>
      )}
    </div>
  )
}
