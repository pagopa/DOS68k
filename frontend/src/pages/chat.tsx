import { TopBar } from '@/components/top-bar'
import { SessionsSidebar } from '@/features/chat/sessions-sidebar'

export function ChatPage() {
  return (
    <div className="flex h-screen flex-col">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <SessionsSidebar />
        <main className="flex flex-1 items-center justify-center text-gray-400">
          Select or create a session to start chatting
        </main>
      </div>
    </div>
  )
}
