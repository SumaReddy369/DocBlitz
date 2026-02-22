'use client';

import { useState, useRef, useEffect } from 'react';
import { queryAPI } from '@/lib/api';
import MessageBubble from './MessageBubble';

interface Source {
  content: string;
  page_number?: number;
  chunk_index: number;
  similarity_score: number;
}

interface Message {
  type: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface ChatInterfaceProps {
  selectedDocId: string | null;
}

export default function ChatInterface({ selectedDocId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'assistant',
      content: 'Hello! 👋 Upload a document and ask me anything about it. I\'ll find the relevant information and answer your questions.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { type: 'user', content: question }]);
    setLoading(true);

    try {
      const response = await queryAPI.ask(question, selectedDocId || undefined);
      const data = response.data;

      setMessages((prev) => [
        ...prev,
        {
          type: 'assistant',
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string | object | unknown[] }; status?: number }; message?: string; code?: string };
      let msg = 'Something went wrong. Please try again.';
      const detail = error.response?.data?.detail;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const isConnectionError = !error.response && (
        error.code === 'ERR_NETWORK' ||
        (error.message && /network|connection|fetch|refused|econnrefused/i.test(error.message))
      );
      if (isConnectionError) {
        msg = `Cannot reach backend at ${apiUrl}. Is Docker running? Try: docker-compose up`;
      } else if (error.response?.status === 429) {
        msg = 'API rate limit reached. Please wait 1–2 minutes and try again.';
      } else if (typeof detail === 'string') {
        msg = detail;
      } else if (Array.isArray(detail) && detail.length > 0) {
        msg = String(detail[0]);
      } else if (detail && typeof detail === 'object') {
        const errObj = detail as { error?: { message?: string }; message?: string };
        msg = errObj?.error?.message || errObj?.message || JSON.stringify(detail).slice(0, 200);
      } else if (error.message) {
        msg = error.message;
      }
      console.error('Query error:', error);
      setMessages((prev) => [
        ...prev,
        {
          type: 'assistant',
          content: `❌ Error: ${msg}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((msg, i) => (
          <MessageBubble key={i} type={msg.type} content={msg.content} sources={msg.sources} />
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <div className="animate-pulse">🤖</div>
            <span>Searching documents & generating answer...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-gray-700 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              selectedDocId
                ? 'Ask a question about the selected document...'
                : 'Ask a question about all your documents...'
            }
            className="flex-1 bg-gray-800 text-white border border-gray-600 rounded-xl px-4 py-3
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
              placeholder-gray-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed
              text-white px-6 py-3 rounded-xl font-medium transition"
          >
            {loading ? '⏳' : '🔍'}
          </button>
        </div>
      </form>
    </div>
  );
}