'use client';

interface NavbarProps {
  username?: string;
}

export default function Navbar({ username }: NavbarProps) {
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.reload();
  };

  return (
    <nav className="bg-gray-900 border-b border-gray-700 px-6 py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">🤖</span>
          <h1 className="text-xl font-bold text-white">DocQ&A</h1>
          <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full">AI</span>
        </div>
        {username && (
          <div className="flex items-center space-x-4">
            <span className="text-gray-300 text-sm">Welcome, {username}</span>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm transition"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}