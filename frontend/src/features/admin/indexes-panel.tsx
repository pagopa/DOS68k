import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogFooter, DialogClose,
} from '@/components/ui/dialog'
import { ApiError } from '@/lib/api'
import { useIndexes, useCreateIndex, useDeleteIndex } from './hooks'

function DeleteIndexDialog({
  indexId,
  onConfirm,
}: {
  indexId: string
  onConfirm: () => void
}) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100"
        aria-label={`Delete index ${indexId}`}
        onClick={(e) => { e.stopPropagation(); setOpen(true) }}
      >
        <Trash2 className="h-3.5 w-3.5" />
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Index</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete index <strong>&ldquo;{indexId}&rdquo;</strong>? This cannot be undone.
          </p>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button
              variant="destructive"
              onClick={() => { onConfirm(); setOpen(false) }}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

export function IndexesPanel({
  selectedIndex,
  onSelectIndex,
}: {
  selectedIndex: string | null
  onSelectIndex: (id: string) => void
}) {
  const [newIndexId, setNewIndexId] = useState('')
  const [inlineError, setInlineError] = useState<string | null>(null)

  const { data: indexes, isLoading, isError } = useIndexes()
  const { mutate: createIndex, isPending: isCreating } = useCreateIndex()
  const { mutate: deleteIndex } = useDeleteIndex()

  if (isError) {
    toast.error('Failed to load indexes')
  }

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    const id = newIndexId.trim()
    if (!id) return
    setInlineError(null)
    createIndex(id, {
      onSuccess: () => {
        setNewIndexId('')
        onSelectIndex(id)
      },
      onError: (err) => {
        if (err instanceof ApiError && err.status === 409) {
          setInlineError(`Index "${id}" already exists.`)
        }
      },
    })
  }

  const sorted = indexes ? [...indexes].sort() : []

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-3">
        <p className="mb-2 text-xs font-semibold uppercase text-gray-500 tracking-wide">Indexes</p>
        <form onSubmit={handleCreate} className="flex gap-2">
          <Input
            placeholder="index-id"
            value={newIndexId}
            onChange={(e) => { setNewIndexId(e.target.value); setInlineError(null) }}
            className="flex-1 text-sm"
            disabled={isCreating}
          />
          <Button type="submit" size="sm" disabled={isCreating || !newIndexId.trim()}>
            {isCreating ? 'Creating…' : 'New'}
          </Button>
        </form>
        {inlineError && (
          <p role="alert" className="mt-1.5 text-xs text-red-600">{inlineError}</p>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        {isLoading && (
          <p className="px-2 py-4 text-sm text-gray-400">Loading…</p>
        )}
        {!isLoading && sorted.length === 0 && (
          <p className="px-2 py-4 text-sm text-gray-400">No indexes yet</p>
        )}
        {sorted.map((id) => (
          <div
            key={id}
            role="button"
            tabIndex={0}
            aria-current={id === selectedIndex ? 'true' : undefined}
            className={`group flex cursor-pointer items-center justify-between rounded-md px-2 py-2 text-sm transition-colors ${
              id === selectedIndex
                ? 'bg-primary text-primary-foreground'
                : 'text-gray-700 hover:bg-gray-200'
            }`}
            onClick={() => onSelectIndex(id)}
            onKeyDown={(e) => e.key === 'Enter' && onSelectIndex(id)}
          >
            <span className="truncate font-mono text-xs">{id}</span>
            <DeleteIndexDialog
              indexId={id}
              onConfirm={() => {
                deleteIndex(id, {
                  onSuccess: () => {
                    if (selectedIndex === id) onSelectIndex('')
                  },
                })
              }}
            />
          </div>
        ))}
      </nav>
    </div>
  )
}
