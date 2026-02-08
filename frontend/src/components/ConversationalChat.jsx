import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader } from 'lucide-react';
import useSearch from '../hooks/useSearch';

function cleanMarkdown(text = '') {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/#+\s?/g, '')
    .replace(/-\s/g, '• ')
    .trim();
}

const ConversationalChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI equity research assistant. Ask me about any stock or company.",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { runSearch } = useSearch();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = {
      id: messages.length + 1,
      text: input,
      sender: 'user'
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const result = await runSearch(input);

      const botMsg = {
        id: messages.length + 2,
        text: result?.chat?.answer || 'No response available',
        sender: 'bot',
        data: result
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: messages.length + 2,
          text: 'Something went wrong. Please try again.',
          sender: 'bot',
          isError: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      <div className="bg-secondary border-b border-textMuted/10 p-4">
        <h1 className="text-xl font-bold">Equity Research Assistant</h1>
        <p className="text-sm text-textMuted">Ask me anything about stocks and companies</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-lg px-4 py-2 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-primary text-background'
                  : 'bg-surface text-text'
              }`}
            >
              <p className="text-sm whitespace-pre-line">
                {cleanMarkdown(msg.text)}
              </p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <Loader className="animate-spin w-4 h-4" />
            <span className="ml-2 text-sm">Processing...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="bg-secondary border-t border-textMuted/10 p-4 flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          className="flex-1 px-4 py-2 rounded-lg bg-surface"
          placeholder="Ask about a stock..."
        />
        <button onClick={handleSend} className="bg-primary px-4 py-2 rounded-lg">
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};

export default ConversationalChat;
