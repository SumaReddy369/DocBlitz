'use client';

import { useState, useEffect } from 'react';
import { authAPI, documentsAPI } from '@/lib/api';
import Navbar from '@/components/Navbar';
import FileUpload from '@/components/FileUpload';
import DocumentList from '@/components/DocumentList';
import ChatInterface from '@/components/ChatInterface';

interface DocumentType {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  total_chunks: number;
  status: string;
  created_at: string;
}

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [documents, setDocuments] = useState<DocumentType[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);

  const [isRegistering, setIsRegistering] = useState(false);
  const [authForm, setAuthForm] = useState({ email: '', username: '', password: '' });
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [backendReachable, setBackendReachable] = useState<boolean | null>(null);

  useEffect(() => {
    fetch((process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/health')
      .then(() => setBackendReachable(true))
      .catch(() => setBackendReachable(false));
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUsername = localStorage.getItem('username');
    if (token && savedUsername) {
      setIsLoggedIn(true);
      setUsername(savedUsername);
      loadDocuments();
    }
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await documentsAPI.list();
      setDocuments(response.data.documents);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    try {
      if (isRegistering) {
        await authAPI.register({
          email: authForm.email,
          username: authForm.username,
          password: authForm.password,
        });
      }

      const response = await authAPI.login(authForm.username, authForm.password);
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      localStorage.setItem('username', authForm.username);
      setIsLoggedIn(true);
      setUsername(authForm.username);
      loadDocuments();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string | unknown[] }; status?: number }; message?: string };
      console.error('Auth error:', error);
      let msg = 'Authentication failed';
      if (error.response?.status === 401) {
        msg = 'Incorrect username or password';
      } else if (error.response?.data?.detail) {
        const d = error.response.data.detail;
        const errType = (error.response.data as { type?: string }).type;
        msg = Array.isArray(d) ? d.map((e: { msg?: string }) => e.msg).join(', ') : String(d);
        if (errType) msg += ` (${errType})`;
      } else if (error.response?.status && error.response.status >= 500) {
        msg = `Server error (${error.response.status}). Check backend logs.`;
      } else if (error.message) {
        msg = error.message.includes('Network') || error.message.includes('fetch')
          ? 'Cannot reach backend at ' + (process.env.NEXT_PUBLIC_API_URL || 'localhost:8000') + '. Is Docker running?'
          : error.message;
      }
      setAuthError(msg);
    } finally {
      setAuthLoading(false);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="bg-gray-900 border border-gray-700 rounded-2xl p-8 w-full max-w-md">
          <div className="text-center mb-6">
            <span className="text-5xl">🤖</span>
            <h1 className="text-2xl font-bold text-white mt-3">DocQ&A Platform</h1>
            <p className="text-gray-400 text-sm mt-1">AI-Powered Document Intelligence</p>
          </div>

          {backendReachable === false && (
            <p className="text-amber-400 text-sm mb-4 p-2 bg-amber-900/30 rounded">
              ⚠ Backend not reachable. Ensure docker-compose is running (backend on port 8000).
            </p>
          )}
          <form onSubmit={handleAuth} className="space-y-4">
            {isRegistering && (
              <input
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg px-4 py-3
                  focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
                required
              />
            )}
            <input
              type="text"
              placeholder="Username"
              value={authForm.username}
              onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })}
              className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg px-4 py-3
                focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={authForm.password}
              onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
              className="w-full bg-gray-800 text-white border border-gray-600 rounded-lg px-4 py-3
                focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-500"
              required
            />

            {authError && <p className="text-red-400 text-sm">❌ {authError}</p>}

            <button
              type="submit"
              disabled={authLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700
                text-white py-3 rounded-lg font-medium transition"
            >
              {authLoading ? '⏳ Please wait...' : isRegistering ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-gray-400 text-sm mt-4">
            {isRegistering ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => { setIsRegistering(!isRegistering); setAuthError(''); }}
              className="text-blue-400 hover:text-blue-300"
            >
              {isRegistering ? 'Sign In' : 'Register'}
            </button>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <Navbar username={username} />

      <div className="flex-1 flex max-w-7xl mx-auto w-full">
        <div className="w-80 border-r border-gray-700 p-4 flex flex-col">
          <FileUpload onUploadSuccess={loadDocuments} />
          <DocumentList
            documents={documents}
            selectedDoc={selectedDoc}
            onSelect={setSelectedDoc}
            onRefresh={loadDocuments}
          />
        </div>

        <div className="flex-1 flex flex-col">
          <ChatInterface selectedDocId={selectedDoc} />
        </div>
      </div>
    </div>
  );
}