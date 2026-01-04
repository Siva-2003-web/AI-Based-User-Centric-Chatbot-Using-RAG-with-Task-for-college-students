import { Link, useNavigate, useLocation } from "react-router-dom";

export default function Layout({ children, token, setToken }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950/50 to-slate-900">
      {/* Top Navigation */}
      <nav className="bg-slate-900/95 backdrop-blur-xl border-b border-indigo-500/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/40">
                <span className="text-xl">🎓</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-white tracking-tight">
                  College Assistant
                </h1>
                <p className="text-xs text-indigo-400 font-semibold -mt-0.5">
                  AI-Powered Help Desk
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-red-900/50 text-slate-300 hover:text-red-400 font-medium rounded-xl border border-slate-700 hover:border-red-500/50 transition-all duration-200"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content - Full width for chat */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>
    </div>
  );
}
