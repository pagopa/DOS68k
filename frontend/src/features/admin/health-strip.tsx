import { useHealthQueue, useHealthStorage, useHealthVdb } from './hooks'

function HealthPill({ label, isHealthy }: { label: string; isHealthy: boolean | null }) {
  const color =
    isHealthy === null
      ? 'bg-gray-200 text-gray-500'
      : isHealthy
        ? 'bg-green-100 text-green-800'
        : 'bg-red-100 text-red-700'

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${color}`}>
      <span
        className={`mr-1.5 h-1.5 w-1.5 rounded-full ${
          isHealthy === null ? 'bg-gray-400' : isHealthy ? 'bg-green-500' : 'bg-red-500'
        }`}
      />
      {label}
    </span>
  )
}

export function HealthStrip() {
  const queue = useHealthQueue()
  const storage = useHealthStorage()
  const vdb = useHealthVdb()

  return (
    <div className="flex items-center gap-3 border-b bg-gray-50 px-4 py-2">
      <span className="text-xs font-medium text-gray-500 mr-1">Health</span>
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
