import { useHealthQueue, useHealthStorage, useHealthVdb } from './hooks'

function HealthPill({ label, isHealthy }: { label: string; isHealthy: boolean | null }) {
  const color =
    isHealthy === null
      ? 'bg-secondary text-muted-foreground border border-border'
      : isHealthy
        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
        : 'bg-red-50 text-red-700 border border-red-200'

  const dotColor =
    isHealthy === null ? 'bg-zinc-400' : isHealthy ? 'bg-emerald-500' : 'bg-red-500'

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${color}`}>
      <span className={`mr-1.5 h-1.5 w-1.5 rounded-full ${dotColor}`} />
      {label}
    </span>
  )
}

export function HealthStrip() {
  const queue = useHealthQueue()
  const storage = useHealthStorage()
  const vdb = useHealthVdb()

  return (
    <div className="flex items-center gap-2 border-b bg-secondary px-4 py-2">
      <span className="text-xs font-medium text-muted-foreground mr-1">Health</span>
      <HealthPill
        label="Queue"
        isHealthy={queue.isSuccess ? true : queue.isError ? false : null}
      />
      <HealthPill
        label="Storage"
        isHealthy={storage.isSuccess ? true : storage.isError ? false : null}
      />
      <HealthPill
        label="Vector DB"
        isHealthy={vdb.isSuccess ? true : vdb.isError ? false : null}
      />
    </div>
  )
}
