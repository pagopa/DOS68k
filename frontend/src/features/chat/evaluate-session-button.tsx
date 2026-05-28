import { Sparkles } from 'lucide-react'
import { useAuth } from '@/lib/auth/use-auth'

interface EvaluateSessionButtonProps {
  onClick: () => void
  isPending?: boolean
}

const TOOLTIP =
  'Scores answers with user feedback that have not yet been scored (capped per session).'

export function EvaluateSessionButton({ onClick, isPending = false }: EvaluateSessionButtonProps) {
  const { user } = useAuth()
  if (user?.role !== 'admin') return null

  return (
    <button
      type="button"
      title={TOOLTIP}
      disabled={isPending}
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-md border border-border bg-card px-2.5 py-1.5 text-xs font-medium text-foreground hover:bg-accent disabled:cursor-not-allowed disabled:opacity-60"
    >
      <Sparkles className="h-3.5 w-3.5" aria-hidden />
      Evaluate rated answers
    </button>
  )
}
