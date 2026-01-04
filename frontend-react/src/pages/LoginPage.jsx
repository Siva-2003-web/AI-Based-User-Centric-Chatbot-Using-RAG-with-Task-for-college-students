import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiService } from "../services/api";

export default function LoginPage({ setToken, setUser }) {
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [focusedField, setFocusedField] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    setTimeout(() => setMounted(true), 100);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await apiService.login(studentId, password);
      setToken(data.token);
      setUser(data);
      navigate("/chat");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex">
      {/* Left side - Branding section */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-slate-950 via-indigo-950 to-violet-950 items-center justify-center p-12">
        {/* Animated grid background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute inset-0 grid-bg opacity-20" />

          {/* Floating geometric shapes */}
          <div className="absolute top-20 left-20 w-32 h-32 border border-indigo-400/20 rounded-2xl animate-float-slow" />
          <div className="absolute top-40 right-32 w-24 h-24 border border-violet-400/20 rounded-full animate-float-medium" />
          <div className="absolute bottom-32 left-40 w-20 h-20 border border-indigo-300/20 rotate-45 animate-float-fast" />
          <div
            className="absolute bottom-20 right-20 w-28 h-28 border border-violet-300/20 rounded-2xl animate-float-slow"
            style={{ animationDelay: "-5s" }}
          />
          <div
            className="absolute top-1/2 left-16 w-16 h-16 border border-indigo-400/15 rounded-full animate-float-medium"
            style={{ animationDelay: "-3s" }}
          />

          {/* Gradient orbs */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/15 rounded-full blur-[120px] animate-pulse-slow" />
          <div
            className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-violet-500/15 rounded-full blur-[100px] animate-pulse-slow"
            style={{ animationDelay: "-4s" }}
          />

          {/* Animated lines */}
          <svg
            className="absolute inset-0 w-full h-full"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient
                id="line-gradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="0%"
              >
                <stop offset="0%" stopColor="rgba(99, 102, 241, 0)" />
                <stop offset="50%" stopColor="rgba(139, 92, 246, 0.3)" />
                <stop offset="100%" stopColor="rgba(99, 102, 241, 0)" />
              </linearGradient>
            </defs>
            <line
              x1="0"
              y1="30%"
              x2="100%"
              y2="30%"
              stroke="url(#line-gradient)"
              strokeWidth="1"
              className="animate-slide-right"
            />
            <line
              x1="0"
              y1="70%"
              x2="100%"
              y2="70%"
              stroke="url(#line-gradient)"
              strokeWidth="1"
              className="animate-slide-left"
            />
          </svg>
        </div>

        {/* Content */}
        <div
          className={`relative z-10 text-center transform transition-all duration-1000 ${
            mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-3xl shadow-2xl shadow-indigo-500/40 mb-8 animate-float-gentle">
            <span className="text-5xl">🎓</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">
            College Assistant
          </h1>
          <p className="text-indigo-200/80 text-lg max-w-md mx-auto leading-relaxed">
            Your intelligent companion for academic success. Get instant answers
            to all your college-related queries.
          </p>

          {/* Feature highlights */}
          <div
            className={`mt-12 space-y-4 transform transition-all duration-1000 delay-300 ${
              mounted ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
            }`}
          >
            {[
              { icon: "💬", text: "AI-Powered Chat Support" },
              { icon: "📚", text: "Course Information" },
              { icon: "📅", text: "Schedule Management" },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="flex items-center justify-center gap-3 text-indigo-200/70"
                style={{ transitionDelay: `${400 + idx * 100}ms` }}
              >
                <span className="text-xl">{feature.icon}</span>
                <span className="text-sm font-medium">{feature.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950">
        {/* Background pattern */}
        <div className="absolute inset-0 lg:left-1/2 overflow-hidden">
          <div className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-to-br from-indigo-500/10 to-transparent rounded-full blur-3xl animate-rotate-slow" />
          <div className="absolute -bottom-1/2 -left-1/2 w-full h-full bg-gradient-to-tr from-violet-500/10 to-transparent rounded-full blur-3xl animate-rotate-slow-reverse" />
        </div>

        <div
          className={`relative z-10 w-full max-w-md transform transition-all duration-700 ease-out ${
            mounted
              ? "translate-y-0 opacity-100 scale-100"
              : "translate-y-8 opacity-0 scale-95"
          }`}
        >
          {/* Mobile header */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-2xl shadow-lg shadow-indigo-500/40 mb-4">
              <span className="text-3xl">🎓</span>
            </div>
            <h1 className="text-2xl font-bold text-white">College Assistant</h1>
          </div>

          {/* Login card */}
          <div className="bg-slate-800/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-indigo-500/10 overflow-hidden border border-slate-700/50">
            <div className="p-8 sm:p-10">
              {/* Header */}
              <div
                className={`mb-8 transform transition-all duration-500 ${
                  mounted
                    ? "translate-y-0 opacity-100"
                    : "translate-y-4 opacity-0"
                }`}
                style={{ transitionDelay: "200ms" }}
              >
                <h2 className="text-2xl font-bold text-white mb-1">
                  Welcome back
                </h2>
                <p className="text-slate-400">
                  Sign in to continue to your dashboard
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Student ID field */}
                <div
                  className={`transform transition-all duration-500 ${
                    mounted
                      ? "translate-y-0 opacity-100"
                      : "translate-y-4 opacity-0"
                  }`}
                  style={{ transitionDelay: "300ms" }}
                >
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Student ID
                  </label>
                  <div className="relative group">
                    <div
                      className={`absolute inset-0 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm ${
                        focusedField === "studentId" ? "opacity-100" : ""
                      }`}
                      style={{ padding: "2px" }}
                    />
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <svg
                          className={`w-5 h-5 transition-all duration-300 ${
                            focusedField === "studentId"
                              ? "text-indigo-400 scale-110"
                              : "text-slate-500"
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1.5}
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                          />
                        </svg>
                      </div>
                      <input
                        type="text"
                        value={studentId}
                        onChange={(e) => setStudentId(e.target.value)}
                        onFocus={() => setFocusedField("studentId")}
                        onBlur={() => setFocusedField(null)}
                        placeholder="Enter your student ID"
                        className={`w-full pl-12 pr-4 py-3.5 bg-slate-700/50 border-2 rounded-xl text-white placeholder-slate-500 transition-all duration-300 focus:outline-none focus:bg-slate-700 ${
                          focusedField === "studentId"
                            ? "border-indigo-500 shadow-lg shadow-indigo-500/20"
                            : "border-slate-600 hover:border-slate-500"
                        }`}
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Password field */}
                <div
                  className={`transform transition-all duration-500 ${
                    mounted
                      ? "translate-y-0 opacity-100"
                      : "translate-y-4 opacity-0"
                  }`}
                  style={{ transitionDelay: "400ms" }}
                >
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Password
                  </label>
                  <div className="relative group">
                    <div
                      className={`absolute inset-0 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-sm ${
                        focusedField === "password" ? "opacity-100" : ""
                      }`}
                      style={{ padding: "2px" }}
                    />
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <svg
                          className={`w-5 h-5 transition-all duration-300 ${
                            focusedField === "password"
                              ? "text-blue-600 scale-110"
                              : "text-slate-400"
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={1.5}
                            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                          />
                        </svg>
                      </div>
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        onFocus={() => setFocusedField("password")}
                        onBlur={() => setFocusedField(null)}
                        placeholder="Enter your password"
                        className={`w-full pl-12 pr-4 py-3.5 bg-slate-50 border-2 rounded-xl text-slate-800 placeholder-slate-400 transition-all duration-300 focus:outline-none focus:bg-white ${
                          focusedField === "password"
                            ? "border-blue-500 shadow-lg shadow-blue-500/10"
                            : "border-slate-200 hover:border-slate-300"
                        }`}
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Error message */}
                {error && (
                  <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-sm animate-shake">
                    <div className="flex-shrink-0 w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center">
                      <svg
                        className="w-4 h-4 text-red-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </div>
                    <span className="font-medium">{error}</span>
                  </div>
                )}

                {/* Submit button */}
                <div
                  className={`pt-2 transform transition-all duration-500 ${
                    mounted
                      ? "translate-y-0 opacity-100"
                      : "translate-y-4 opacity-0"
                  }`}
                  style={{ transitionDelay: "500ms" }}
                >
                  <button
                    type="submit"
                    disabled={loading}
                    className="relative w-full py-4 rounded-xl font-semibold text-white overflow-hidden group disabled:cursor-not-allowed transition-all duration-300 active:scale-[0.98]"
                  >
                    {/* Button background */}
                    <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-500 transition-all duration-500" />
                    <div className="absolute inset-0 bg-gradient-to-r from-indigo-700 via-indigo-600 to-violet-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                    {/* Shine effect */}
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                      <div className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12" />
                    </div>

                    {/* Shadow */}
                    <div className="absolute inset-0 rounded-xl shadow-lg shadow-indigo-500/40 group-hover:shadow-xl group-hover:shadow-indigo-500/50 transition-shadow duration-300" />

                    {/* Content */}
                    <span className="relative flex items-center justify-center gap-2">
                      {loading ? (
                        <>
                          <svg
                            className="animate-spin h-5 w-5"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                              fill="none"
                            />
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                          </svg>
                          <span>Signing in...</span>
                        </>
                      ) : (
                        <>
                          <span>Sign In</span>
                          <svg
                            className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M13 7l5 5m0 0l-5 5m5-5H6"
                            />
                          </svg>
                        </>
                      )}
                    </span>
                  </button>
                </div>
              </form>

              {/* Demo credentials */}
              <div
                className={`mt-8 pt-6 border-t border-slate-700 transform transition-all duration-500 ${
                  mounted
                    ? "translate-y-0 opacity-100"
                    : "translate-y-4 opacity-0"
                }`}
                style={{ transitionDelay: "600ms" }}
              >
                <div className="flex items-center justify-center gap-2 mb-3">
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent to-slate-600" />
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Demo Access
                  </span>
                  <div className="h-px flex-1 bg-gradient-to-l from-transparent to-slate-600" />
                </div>
                <div className="flex items-center justify-center gap-6 p-4 bg-gradient-to-br from-slate-700/50 to-slate-800/50 rounded-xl border border-slate-600/50">
                  <div className="text-center">
                    <span className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                      Student ID
                    </span>
                    <code className="text-sm font-mono font-bold text-indigo-300 bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-600 shadow-sm">
                      STU00001
                    </code>
                  </div>
                  <div className="w-px h-10 bg-slate-600" />
                  <div className="text-center">
                    <span className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                      Password
                    </span>
                    <code className="text-sm font-mono font-bold text-indigo-300 bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-600 shadow-sm">
                      password123
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <p
            className={`text-center text-slate-400 text-sm mt-8 transform transition-all duration-500 ${
              mounted ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
            }`}
            style={{ transitionDelay: "700ms" }}
          >
            © 2026 College Assistant. Secure & Private.
          </p>
        </div>
      </div>

      {/* Styles */}
      <style>{`
        .grid-bg {
          background-image: 
            linear-gradient(rgba(99, 102, 241, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.1) 1px, transparent 1px);
          background-size: 50px 50px;
          animation: grid-move 20s linear infinite;
        }
        
        @keyframes grid-move {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes float-slow {
          0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.3; }
          50% { transform: translateY(-20px) rotate(5deg); opacity: 0.5; }
        }
        
        @keyframes float-medium {
          0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.2; }
          50% { transform: translateY(-30px) rotate(-5deg); opacity: 0.4; }
        }
        
        @keyframes float-fast {
          0%, 100% { transform: translateY(0) rotate(45deg); opacity: 0.2; }
          50% { transform: translateY(-25px) rotate(50deg); opacity: 0.35; }
        }
        
        @keyframes float-gentle {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        
        @keyframes pulse-slow {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.05); }
        }
        
        @keyframes rotate-slow {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes rotate-slow-reverse {
          0% { transform: rotate(360deg); }
          100% { transform: rotate(0deg); }
        }
        
        @keyframes slide-right {
          0% { transform: translateX(-100%); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateX(100%); opacity: 0; }
        }
        
        @keyframes slide-left {
          0% { transform: translateX(100%); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateX(-100%); opacity: 0; }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          20%, 60% { transform: translateX(-4px); }
          40%, 80% { transform: translateX(4px); }
        }
        
        .animate-float-slow { animation: float-slow 8s ease-in-out infinite; }
        .animate-float-medium { animation: float-medium 6s ease-in-out infinite; }
        .animate-float-fast { animation: float-fast 5s ease-in-out infinite; }
        .animate-float-gentle { animation: float-gentle 4s ease-in-out infinite; }
        .animate-pulse-slow { animation: pulse-slow 8s ease-in-out infinite; }
        .animate-rotate-slow { animation: rotate-slow 60s linear infinite; }
        .animate-rotate-slow-reverse { animation: rotate-slow-reverse 50s linear infinite; }
        .animate-slide-right { animation: slide-right 8s ease-in-out infinite; }
        .animate-slide-left { animation: slide-left 10s ease-in-out infinite; }
        .animate-shake { animation: shake 0.4s ease-in-out; }
      `}</style>
    </div>
  );
}
