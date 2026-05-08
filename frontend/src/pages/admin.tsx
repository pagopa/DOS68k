import { useState } from 'react'
import { TopBar } from '@/components/top-bar'
import { HealthStrip } from '@/features/admin/health-strip'
import { IndexesPanel } from '@/features/admin/indexes-panel'
import { DocumentsPanel } from '@/features/admin/documents-panel'

export function AdminPage() {
  const [selectedIndex, setSelectedIndex] = useState<string | null>(null)

  return (
    <div className="flex h-screen flex-col">
      <TopBar />
      <HealthStrip />
      <div className="flex flex-1 overflow-hidden">
        <aside className="flex w-72 flex-shrink-0 flex-col border-r bg-gray-50 overflow-hidden">
          <IndexesPanel
            selectedIndex={selectedIndex}
            onSelectIndex={(id) => setSelectedIndex(id || null)}
          />
        </aside>
        <main className="flex flex-1 flex-col overflow-hidden bg-white">
          <DocumentsPanel selectedIndex={selectedIndex} />
        </main>
      </div>
    </div>
  )
}
