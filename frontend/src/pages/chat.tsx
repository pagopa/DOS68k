import { useParams } from 'react-router-dom'
import { TopBar } from '@/components/top-bar'
import { SessionsSidebar } from '@/features/chat/sessions-sidebar'
import { ChatView } from '@/features/chat/chat-view'

export function ChatPage() {
  const { sessionId } = useParams<{ sessionId?: string }>()

  return (
    <div className="flex h-screen flex-col">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <SessionsSidebar />
        {sessionId ? (
          <ChatView key={sessionId} sessionId={sessionId} />
        ) : (
          <main className="flex flex-1 items-center justify-center text-gray-400">
            Select or create a session to start chatting
          </main>
        )}
      </div>
    </div>
  )
}
