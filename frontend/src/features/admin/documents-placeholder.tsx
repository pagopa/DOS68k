export function DocumentsPlaceholder({ selectedIndex }: { selectedIndex: string | null }) {
  if (!selectedIndex) {
    return (
      <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
        Select an index to manage its documents
      </div>
    )
  }

  return (
    <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
      Documents panel — coming in slice #6
    </div>
  )
}
