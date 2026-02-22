'use client';

import { useState, useRef } from 'react';
import { documentsAPI } from '@/lib/api';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError('');

    try {
      await documentsAPI.upload(file);
      onUploadSuccess();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string | string[] }; status?: number }; message?: string };
      let msg = 'Upload failed';
      const d = axiosError.response?.data?.detail;
      if (typeof d === 'string') msg = d;
      else if (Array.isArray(d) && d.length > 0) msg = String(d[0]);
      else if (axiosError.message?.includes('Network') || !axiosError.response) msg = 'Cannot reach backend. Is it running on port 8000?';
      setError(msg);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  return (
    <div className="mb-6">
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
          ${dragActive ? 'border-blue-500 bg-blue-500/10' : 'border-gray-600 hover:border-gray-400'}
          ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />
        {uploading ? (
          <div>
            <div className="animate-spin text-4xl mb-2">⚙️</div>
            <p className="text-gray-300">Processing document...</p>
            <p className="text-gray-500 text-sm">Extracting text, chunking & generating embeddings</p>
          </div>
        ) : (
          <div>
            <div className="text-4xl mb-2">📄</div>
            <p className="text-gray-300 font-medium">Drop a PDF or TXT file here</p>
            <p className="text-gray-500 text-sm mt-1">or click to browse (max 10MB)</p>
          </div>
        )}
      </div>
      {error && <p className="text-red-400 text-sm mt-2">❌ {error}</p>}
    </div>
  );
}