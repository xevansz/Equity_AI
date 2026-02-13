import React from 'react'
import ConversationalChat from '../components/ConversationalChat'

const ChatPage = () => {
  return (
    <div className="bg-background flex flex-col flex-1 min-h-0 w-full">
      <div className="flex-1 flex flex-col min-h-0">
        <ConversationalChat />
      </div>
    </div>
  )
}

export default ChatPage
