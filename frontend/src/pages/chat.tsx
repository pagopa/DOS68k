import { TopBar } from '@/components/top-bar'

export function ChatPage() {
  return (
    <div className="flex h-screen flex-col">
      <TopBar />
      <main className="flex flex-1 items-center justify-center text-gray-400">
        Chat — coming in slice #2
      </main>
    </div>
  )
}
