'use client';

interface Source {
  content: string;
  page_number?: number;
  chunk_index: number;
  similarity_score: number;
}

interface MessageBubbleProps {
  type: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export default function MessageBubble({ type, content, sources }: MessageBubbleProps) {
  return (
    <div className={`flex ${type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className="max-w-[80%]">
        <div className={`flex items-start gap-3 ${type === 'user' ? 'flex-row-reverse' : ''}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0
            ${type === 'user' ? 'bg-blue-600' : 'bg-purple-600'}`}>
            {type === 'user' ? '👤' : '🤖'}
          </div>

          <div>
            <div className={`rounded-2xl px-4 py-3 ${
              type === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-100 border border-gray-700'
            }`}>
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{content}</p>
            </div>

            {sources && sources.length > 0 && (
              <div className="mt-2 space-y-1">
                <p className="text-gray-500 text-xs font-medium">📎 Sources:</p>
                {sources.slice(0, 3).map((source, i) => (
                  <details key={i} className="text-xs">
                    <summary className="text-gray-400 cursor-pointer hover:text-gray-300">
                      Source {i + 1}
                      {source.page_number && ` (Page ${source.page_number})`}
                      {' '}— {(source.similarity_score * 100).toFixed(0)}% match
                    </summary>
                    <p className="text-gray-500 mt-1 pl-3 border-l border-gray-700">
                      {source.content.substring(0, 200)}...
                    </p>
                  </details>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}