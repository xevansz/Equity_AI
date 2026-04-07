import React, { useState, useRef, useEffect } from 'react'
import { Send, PanelLeftOpen, PanelLeftClose } from 'lucide-react'
import { sendChat } from '../api/chat'
import { fetchConversationHistory } from '../api/conversations'
import { ChatMessageSkeleton } from './Skeleton'

function cleanMarkdown(text = '') {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/#+\s?/g, '')
    .replace(/-\s/g, '• ')
    .trim()
}

const WELCOME_MESSAGE = {
  id: 'welcome',
  text: "Hello! I'm your AI equity research assistant. Ask me about any stock or company.",
  sender: 'bot',
}

const ConversationalChat = ({
  activeSessionId,
  onSessionCreated,
  onToggleSidebar,
  sidebarOpen,
}) => {
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [sessionId, setSessionId] = useState(activeSessionId || null)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (activeSessionId === null) {
      setSessionId(null)
      setMessages([WELCOME_MESSAGE])
      return
    }

    if (activeSessionId && activeSessionId !== sessionId) {
      setSessionId(activeSessionId)
      setMessages([])
      fetchConversationHistory(activeSessionId)
        .then((history) => {
          const mapped = history.map((m) => ({
            id: m._id || m.timestamp,
            text: m.content,
            sender: m.role === 'user' ? 'user' : 'bot',
          }))
          setMessages(mapped.length > 0 ? mapped : [WELCOME_MESSAGE])
        })
        .catch(() => setMessages([WELCOME_MESSAGE]))
    }
  }, [activeSessionId])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = input
    let currentSessionId = sessionId

    if (!currentSessionId) {
      currentSessionId = `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
      setSessionId(currentSessionId)
      onSessionCreated?.(currentSessionId)
    }

    setInput('')

    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: userMessage, sender: 'user' },
    ])

    setLoading(true)

    try {
      const result = await sendChat(userMessage, currentSessionId)

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: result?.answer || 'No response available',
          sender: 'bot',
        },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text:
            err.response?.data?.detail ||
            err.message ||
            'Something went wrong. Please try again.',
          sender: 'bot',
          isError: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col bg-background flex-1 min-h-0">
      <div className="bg-secondary border-b border-text-muted/10 p-4 flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="text-muted hover:text-text transition"
          title={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
        >
          {sidebarOpen ? (
            <PanelLeftClose size={18} />
          ) : (
            <PanelLeftOpen size={18} />
          )}
        </button>
        <div>
          <h1 className="text-xl font-bold">Equity Research Assistant</h1>
          <p className="text-sm text-muted">
            Ask me anything about stocks and companies
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-lg px-4 py-2 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-primary text-background'
                  : msg.isError
                    ? 'bg-error/10 border border-error/20 text-error'
                    : 'bg-surface text-text'
              }`}
            >
              <p className="text-sm whitespace-pre-line">
                {cleanMarkdown(msg.text)}
              </p>
            </div>
          </div>
        ))}

        {loading && <ChatMessageSkeleton />}
        <div ref={messagesEndRef} />
      </div>

      <div className="bg-secondary border-t border-text-muted/10 p-4 flex gap-2 mt-auto">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && handleSend()}
          className="flex-1 px-4 py-2 rounded-lg bg-surface"
          placeholder="Ask about a stock..."
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-primary px-4 py-2 rounded-lg disabled:opacity-50 transition"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}

export default ConversationalChat
