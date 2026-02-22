'use client';

import { useState } from 'react';
import { documentsAPI } from '@/lib/api';

interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  total_chunks: number;
  status: string;
  created_at: string;
}

interface DocumentListProps {
  documents: Document[];
  selectedDoc: string | null;
  onSelect: (id: string | null) => void;
  onRefresh: () => void;
}

export default function DocumentList({ documents, selectedDoc, onSelect, onRefresh }: DocumentListProps) {
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeleteError(null);
    if (!confirm('Delete this document?')) return;
    try {
      await documentsAPI.delete(id);
      if (selectedDoc === id) onSelect(null);
      onRefresh();
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string }; status?: number }; message?: string };
      const msg = e.response?.data?.detail || e.message || 'Failed to delete. Check connection.';
      setDeleteError(msg);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (documents.length === 0) {
    return (
      <div className="text-gray-500 text-center py-4">
        <p>No documents uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {deleteError && (
        <p className="text-red-400 text-xs p-2 bg-red-900/30 rounded mb-2">{deleteError}</p>
      )}
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-white font-semibold text-sm">📚 Your Documents</h3>
        <button
          onClick={() => onSelect(null)}
          className={`text-xs px-2 py-1 rounded ${
            !selectedDoc ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
          }`}
        >
          Search All
        </button>
      </div>
      {documents.map((doc) => (
        <div
          key={doc.id}
          onClick={() => onSelect(doc.id === selectedDoc ? null : doc.id)}
          className={`p-3 rounded-lg cursor-pointer transition-all border
            ${doc.id === selectedDoc
              ? 'bg-blue-600/20 border-blue-500'
              : 'bg-gray-800 border-gray-700 hover:border-gray-500'}`}
        >
          <div className="flex justify-between items-start">
            <div className="flex-1 min-w-0">
              <p className="text-white text-sm font-medium truncate">{doc.filename}</p>
              <p className="text-gray-400 text-xs mt-1">
                {formatSize(doc.file_size)} • {doc.total_chunks} chunks •
                <span className={doc.status === 'ready' ? ' text-green-400' : ' text-yellow-400'}>
                  {' '}{doc.status}
                </span>
              </p>
            </div>
            <button
              onClick={(e) => handleDelete(doc.id, e)}
              className="text-gray-500 hover:text-red-400 ml-2 text-sm"
            >
              🗑️
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}