import React, { useEffect, useState } from 'react'
import { MessageSquare, Plus } from 'lucide-react'
import ConversationalChat from '../components/ConversationalChat'
import { fetchConversations } from '../api/conversations'

const ChatPage = () => {
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchConversations()
        setSessions(data)
      } catch {
        setSessions([])
      }
    }
    load()
  }, [])

  const startNewChat = () => {
    setActiveSessionId(null)
  }

  const formatTime = (ts) => {
    if (!ts) return ''
    const d = new Date(ts)
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  }

  return (
    <div className="flex flex-1 min-h-0 w-full bg-background">
      {sidebarOpen && (
        <aside className="w-64 flex flex-col bg-secondary border-r border-text-muted/10 shrink-0">
          <div className="p-3 border-b border-text-muted/10">
            <button
              onClick={startNewChat}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-primary text-background text-sm font-medium hover:opacity-90 transition"
            >
              <Plus size={16} />
              New Chat
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions.length === 0 && (
              <p className="text-xs text-muted px-2 py-4 text-center">
                No past conversations
              </p>
            )}
            {sessions.map((s) => (
              <button
                key={s.session_id}
                onClick={() => setActiveSessionId(s.session_id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition group flex items-start gap-2 ${
                  activeSessionId === s.session_id
                    ? 'bg-primary/20 text-text'
                    : 'hover:bg-surface text-muted'
                }`}
              >
                <MessageSquare size={14} className="mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="truncate leading-snug">
                    {s.last_message || 'Chat session'}
                  </p>
                  <p className="text-xs opacity-60 mt-0.5">
                    {formatTime(s.last_timestamp)}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </aside>
      )}

      <div className="flex flex-col flex-1 min-h-0 min-w-0">
        <ConversationalChat
          activeSessionId={activeSessionId}
          onSessionCreated={(id) => {
            setActiveSessionId(id)
            fetchConversations()
              .then(setSessions)
              .catch(() => {})
          }}
          onToggleSidebar={() => setSidebarOpen((v) => !v)}
          sidebarOpen={sidebarOpen}
        />
      </div>
    </div>
  )
}

export default ChatPage
