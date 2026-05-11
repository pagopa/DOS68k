import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Trash2, RefreshCw, UploadCloud } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogFooter, DialogClose,
} from '@/components/ui/dialog'
import { useDocuments, useUploadDocument, useDeleteDocument } from './hooks'

const ACCEPTED_EXTENSIONS = ['.pdf', '.md', '.txt']
const ACCEPTED_MIME = ['application/pdf', 'text/markdown', 'text/plain', 'text/x-markdown']

function isAccepted(file: File): boolean {
  const name = file.name.toLowerCase()
  return ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext))
}

function DeleteDocumentDialog({
  documentName,
  onConfirm,
}: {
  documentName: string
  onConfirm: () => void
}) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100"
        aria-label={`Delete document ${documentName}`}
        onClick={(e) => { e.stopPropagation(); setOpen(true) }}
      >
        <Trash2 className="h-3.5 w-3.5" />
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete <strong>&ldquo;{documentName}&rdquo;</strong>? This cannot be undone.
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

interface UploadingRow {
  name: string
  id: number
}

export function DocumentsPanel({ selectedIndex }: { selectedIndex: string | null }) {
  const [uploadingRows, setUploadingRows] = useState<UploadingRow[]>([])
  const [rejectedNames, setRejectedNames] = useState<string[]>([])
  const [idCounter, setIdCounter] = useState(0)

  const { data: documents, isLoading, refetch } = useDocuments(selectedIndex ?? '')
  const { mutate: uploadDocument } = useUploadDocument(selectedIndex ?? '')
  const { mutate: deleteDocument } = useDeleteDocument(selectedIndex ?? '')

  const handleDrop = useCallback(
    (accepted: File[], rejected: File[]) => {
      setRejectedNames(rejected.map((f) => f.name))

      for (const file of accepted) {
        const rowId = idCounter + accepted.indexOf(file)
        setIdCounter((c) => c + 1)
        setUploadingRows((rows) => [...rows, { name: file.name, id: rowId }])
        uploadDocument(file, {
          onSettled: () => {
            setUploadingRows((rows) => rows.filter((r) => r.id !== rowId))
          },
        })
      }
    },
    [idCounter, uploadDocument]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (accepted, fileRejections) => {
      const clientRejected = accepted.filter((f) => !isAccepted(f))
      const clientAccepted = accepted.filter((f) => isAccepted(f))
      const allRejected = [
        ...fileRejections.map((fr) => fr.file),
        ...clientRejected,
      ]
      handleDrop(clientAccepted, allRejected)
    },
    accept: Object.fromEntries(ACCEPTED_MIME.map((m) => [m, []])),
    noClick: false,
    noKeyboard: false,
  })

  if (!selectedIndex) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-gray-400">
        Select an index to manage its documents
      </div>
    )
  }

  const allDocs = documents ?? []

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Documents
          </p>
          <p className="font-mono text-sm text-gray-700">{selectedIndex}</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          aria-label="Refresh documents"
        >
          <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
          Refresh
        </Button>
      </div>

      {/* Async note */}
      <div className="border-b bg-amber-50 px-4 py-2 text-xs text-amber-700">
        Indexing happens asynchronously. Documents may take a moment to be ready for retrieval.
        Use refresh to see updated state.
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <p className="px-4 py-6 text-sm text-gray-400">Loading…</p>
        )}

        {!isLoading && allDocs.length === 0 && uploadingRows.length === 0 && (
          <p className="px-4 py-6 text-sm text-gray-400">No documents yet — upload one below.</p>
        )}

        {allDocs.map((doc) => (
          <div
            key={doc.documentName}
            className="group flex items-center justify-between border-b px-4 py-2.5 text-sm last:border-b-0"
          >
            <span className="truncate font-mono text-xs text-gray-700">{doc.documentName}</span>
            <DeleteDocumentDialog
              documentName={doc.documentName}
              onConfirm={() => deleteDocument(doc.documentName)}
            />
          </div>
        ))}

        {uploadingRows.map((row) => (
          <div
            key={row.id}
            className="flex items-center gap-2 border-b px-4 py-2.5 text-sm last:border-b-0"
          >
            <span className="truncate font-mono text-xs text-gray-400">{row.name}</span>
            <span className="ml-auto shrink-0 text-xs text-gray-400 italic">uploading…</span>
          </div>
        ))}
      </div>

      {/* Dropzone */}
      <div className="border-t p-4">
        {rejectedNames.length > 0 && (
          <p role="alert" className="mb-2 text-xs text-red-600">
            Unsupported file type. Allowed: {ACCEPTED_EXTENSIONS.join(', ')}.{' '}
            Rejected: {rejectedNames.join(', ')}.
          </p>
        )}
        <div
          {...getRootProps()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-4 py-8 text-sm transition-colors ${
            isDragActive
              ? 'border-primary bg-primary/5 text-primary'
              : 'border-gray-200 text-gray-400 hover:border-gray-300 hover:text-gray-500'
          }`}
        >
          <input {...getInputProps()} />
          <UploadCloud className="mb-2 h-6 w-6" />
          {isDragActive ? (
            <p>Drop to upload</p>
          ) : (
            <p>
              Drag &amp; drop or{' '}
              <span className="underline">click to pick</span> a file
            </p>
          )}
          <p className="mt-1 text-xs opacity-70">Accepted: {ACCEPTED_EXTENSIONS.join(', ')}</p>
        </div>
      </div>
    </div>
  )
}
