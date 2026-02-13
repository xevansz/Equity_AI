import React from 'react'
import ConversationalChat from '../components/ConversationalChat'

const ChatPage = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="flex-1 flex flex-col">
        <ConversationalChat />
      </div>
    </div>
  )
}

export default ChatPage
