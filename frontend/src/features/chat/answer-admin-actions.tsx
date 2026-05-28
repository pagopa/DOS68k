import { MoreHorizontal } from 'lucide-react'
import { useAuth } from '@/lib/auth/use-auth'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

interface AnswerAdminActionsProps {
  isEvaluated: boolean
  onEvaluate: () => void
}

export function AnswerAdminActions({ isEvaluated, onEvaluate }: AnswerAdminActionsProps) {
  const { user } = useAuth()
  if (user?.role !== 'admin') return null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        aria-label="More actions"
        className="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
      >
        <MoreHorizontal className="h-4 w-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem
          disabled={isEvaluated}
          onSelect={() => onEvaluate()}
        >
          Evaluate this answer
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
