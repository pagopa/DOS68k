import type { Scores } from '@/lib/api'

export type EvaluationStatus = 'idle' | 'pending' | 'resolved' | 'failed'

interface ScoresBadgesProps {
  status: EvaluationStatus
  scores: Scores | null
  onRetry: () => void
}

type Tier = 'green' | 'amber' | 'red'

function tierFor(value: number): Tier {
  if (value >= 0.8) return 'green'
  if (value >= 0.5) return 'amber'
  return 'red'
}

const TIER_CLASSES: Record<Tier, string> = {
  green: 'bg-green-100 text-green-800 border-green-300',
  amber: 'bg-amber-100 text-amber-800 border-amber-300',
  red: 'bg-red-100 text-red-800 border-red-300',
}

function Badge({ letter, name, value }: { letter: string; name: string; value: number }) {
  const tier = tierFor(value)
  return (
    <span
      aria-label={`${name} ${value.toFixed(2)}`}
      data-tier={tier}
      title={`${name}: ${value.toFixed(2)}`}
      className={`inline-flex h-5 w-5 items-center justify-center rounded border text-xs font-semibold ${TIER_CLASSES[tier]}`}
    >
      {letter}
    </span>
  )
}

export function ScoresBadges({ status, scores, onRetry }: ScoresBadgesProps) {
  if (status === 'idle') return null

  if (status === 'pending') {
    return <span className="text-xs text-muted-foreground italic">Evaluating…</span>
  }

  if (status === 'failed') {
    return (
      <button
        type="button"
        onClick={onRetry}
        className="text-xs text-destructive underline-offset-2 hover:underline"
      >
        Scoring failed — retry
      </button>
    )
  }

  if (!scores) return null

  return (
    <div className="flex items-center gap-1">
      <Badge letter="R" name="Relevancy" value={scores.relevancy} />
      <Badge letter="F" name="Faithfulness" value={scores.faithfulness} />
      <Badge letter="U" name="Utilization" value={scores.utilization} />
    </div>
  )
}
