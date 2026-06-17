import { useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogFooter, DialogClose,
} from '@/components/ui/dialog'
import { ApiError } from '@/lib/api'
import { useIndexes, useCreateIndex, useDeleteIndex } from './hooks'

function NewIndexDialog({ onCreated }: { onCreated: (id: string) => void }) {
  const [open, setOpen] = useState(false)
  const [indexId, setIndexId] = useState('')
  const { mutate: createIndex, isPending } = useCreateIndex()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const id = indexId.trim()
    if (!id) return
    createIndex(id, {
      onSuccess: () => {
        setOpen(false)
        setIndexId('')
        onCreated(id)
      },
      onError: (err) => {
        if (err instanceof ApiError && err.status === 409) {
          toast.error(`Index "${id}" already exists.`)
        } else {
          toast.error('Failed to create index.')
        }
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button size="sm" className="w-full" onClick={() => setOpen(true)}>
        <Plus className="h-4 w-4" />New Index
      </Button>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New Index</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            placeholder="index-id"
            value={indexId}
            onChange={(e) => setIndexId(e.target.value)}
            autoFocus
            disabled={isPending}
          />
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">Cancel</Button>
            </DialogClose>
            <Button type="submit" disabled={isPending || !indexId.trim()}>
              {isPending ? 'Creating…' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

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
  const { data: indexes, isLoading, isError } = useIndexes()
  const { mutate: deleteIndex } = useDeleteIndex()

  if (isError) {
    toast.error('Failed to load indexes')
  }

  const sorted = indexes ? [...indexes].sort() : []

  return (
    <div className="flex flex-col h-full">
      <div className="border-b p-3">
        <p className="mb-2 text-xs font-mono font-600 uppercase text-muted-foreground tracking-widest">Indexes</p>
        <NewIndexDialog onCreated={onSelectIndex} />
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        {isLoading && (
          <p className="px-2 py-4 text-xs text-muted-foreground">Loading…</p>
        )}
        {!isLoading && sorted.length === 0 && (
          <p className="px-2 py-4 text-xs text-muted-foreground">No indexes yet</p>
        )}
        {sorted.map((id) => (
          <div
            key={id}
            role="button"
            tabIndex={0}
            aria-current={id === selectedIndex ? 'true' : undefined}
            className={`group flex cursor-pointer items-center justify-between rounded-md px-2 py-2 text-xs transition-colors ${
              id === selectedIndex
                ? 'bg-primary text-primary-foreground'
                : 'text-foreground/70 hover:bg-accent hover:text-foreground'
            }`}
            onClick={() => onSelectIndex(id)}
            onKeyDown={(e) => e.key === 'Enter' && onSelectIndex(id)}
          >
            <span className="truncate font-mono">{id}</span>
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
