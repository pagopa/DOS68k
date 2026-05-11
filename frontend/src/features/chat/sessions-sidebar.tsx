import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogFooter, DialogClose,
} from '@/components/ui/dialog'

import { useSessions, useCreateSession, useDeleteSession } from './hooks'
import type { SessionDTO } from '@/lib/api'

function NewSessionDialog({ onCreated }: { onCreated: (id: string) => void }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const { mutate: createSession, isPending } = useCreateSession()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) return
    createSession(
      { title: trimmed, isTemporary: false },
      {
        onSuccess: (session) => {
          setOpen(false)
          setTitle('')
          onCreated(session.id)
        },
      }
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button size="sm" className="w-full" onClick={() => setOpen(true)}>
        <Plus className="h-4 w-4" />
        New Session
      </Button>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New Session</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            placeholder="Session title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">Cancel</Button>
            </DialogClose>
            <Button type="submit" disabled={isPending || !title.trim()}>
              {isPending ? 'Creating…' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

function DeleteConfirmDialog({
  session,
  onConfirm,
}: {
  session: SessionDTO
  onConfirm: () => void
}) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100"
        aria-label={`Delete session ${session.title}`}
        onClick={(e) => { e.stopPropagation(); setOpen(true) }}
      >
        <Trash2 className="h-3.5 w-3.5" />
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Session</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete <strong>&ldquo;{session.title}&rdquo;</strong>? This cannot be undone.
          </p>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button variant="destructive" onClick={() => { onConfirm(); setOpen(false) }}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

export function SessionsSidebar() {
  const navigate = useNavigate()
  const { sessionId: activeId } = useParams<{ sessionId?: string }>()
  const { data: sessions, isLoading, isError } = useSessions()
  const { mutate: deleteSession } = useDeleteSession()

  const sorted = sessions
    ? [...sessions].sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    : []

  if (isError) {
    toast.error('Failed to load sessions')
  }

  function handleDelete(session: SessionDTO) {
    deleteSession(session.id, {
      onSuccess: () => {
        if (activeId === session.id) navigate('/chat', { replace: true })
      },
    })
  }

  return (
    <aside className="flex w-64 flex-shrink-0 flex-col border-r bg-gray-50">
      <div className="border-b p-3">
        <NewSessionDialog onCreated={(id) => navigate(`/chat/${id}`)} />
      </div>
      <nav className="flex-1 overflow-y-auto p-2">
        {isLoading && (
          <p className="px-2 py-4 text-sm text-gray-400">Loading…</p>
        )}
        {!isLoading && sorted.length === 0 && (
          <p className="px-2 py-4 text-sm text-gray-400">No sessions yet</p>
        )}
        {sorted.map((session) => (
          <div
            key={session.id}
            role="button"
            tabIndex={0}
            aria-current={session.id === activeId ? 'page' : undefined}
            className={`group flex cursor-pointer items-center justify-between rounded-md px-2 py-2 text-sm transition-colors ${
              session.id === activeId
                ? 'bg-primary text-primary-foreground'
                : 'text-gray-700 hover:bg-gray-200'
            }`}
            onClick={() => navigate(`/chat/${session.id}`)}
            onKeyDown={(e) => e.key === 'Enter' && navigate(`/chat/${session.id}`)}
          >
            <span className="truncate">{session.title}</span>
            <DeleteConfirmDialog session={session} onConfirm={() => handleDelete(session)} />
          </div>
        ))}
      </nav>
    </aside>
  )
}
