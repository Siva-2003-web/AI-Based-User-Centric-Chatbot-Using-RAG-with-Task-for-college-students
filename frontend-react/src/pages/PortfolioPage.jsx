import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

export default function PortfolioPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTimeout(() => setMounted(true), 100);
  }, []);

  const features = [
    {
      icon: "💬",
      title: "AI-Powered Chat",
      description:
        "Get instant answers to all your college-related queries with our intelligent chatbot powered by advanced AI.",
      color: "from-indigo-500 to-violet-600",
    },
    {
      icon: "📊",
      title: "Attendance Tracking",
      description:
        "Monitor your attendance in real-time with detailed subject-wise breakdown and alerts for low attendance.",
      color: "from-emerald-500 to-teal-600",
    },
    {
      icon: "📅",
      title: "Schedule Management",
      description:
        "View your daily class schedule, exam timetables, and never miss an important academic event.",
      color: "from-orange-500 to-amber-600",
    },
    {
      icon: "💳",
      title: "Fee Status",
      description:
        "Check your fee payment status, due dates, and get reminders for pending payments instantly.",
      color: "from-rose-500 to-pink-600",
    },
    {
      icon: "👨‍🏫",
      title: "Faculty Connect",
      description:
        "Book appointments with faculty members and get their contact information when you need guidance.",
      color: "from-cyan-500 to-blue-600",
    },
    {
      icon: "📚",
      title: "Course Information",
      description:
        "Access detailed information about your courses, syllabi, and academic resources anytime.",
      color: "from-purple-500 to-fuchsia-600",
    },
  ];

  const stats = [
    { number: "10K+", label: "Students Helped" },
    { number: "50+", label: "Courses Covered" },
    { number: "24/7", label: "Available" },
    { number: "99%", label: "Accuracy Rate" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Grid pattern */}
        <div className="absolute inset-0 grid-bg opacity-20" />

        {/* 3D Rotating Cube - Left Side */}
        <div className="absolute top-[20%] left-[8%] perspective-1000">
          <div className="cube-container animate-spin-3d">
            <div className="cube">
              <div className="cube-face cube-front"></div>
              <div className="cube-face cube-back"></div>
              <div className="cube-face cube-right"></div>
              <div className="cube-face cube-left"></div>
              <div className="cube-face cube-top"></div>
              <div className="cube-face cube-bottom"></div>
            </div>
          </div>
        </div>

        {/* 3D Rotating Cube - Right Side */}
        <div
          className="absolute top-[60%] right-[10%] perspective-1000"
          style={{ animationDelay: "-3s" }}
        >
          <div className="cube-container animate-spin-3d-reverse">
            <div className="cube cube-small">
              <div className="cube-face cube-front bg-violet-500/30"></div>
              <div className="cube-face cube-back bg-violet-500/30"></div>
              <div className="cube-face cube-right bg-violet-500/30"></div>
              <div className="cube-face cube-left bg-violet-500/30"></div>
              <div className="cube-face cube-top bg-violet-500/30"></div>
              <div className="cube-face cube-bottom bg-violet-500/30"></div>
            </div>
          </div>
        </div>

        {/* 3D Rotating Octahedron */}
        <div className="absolute top-[40%] left-[85%] perspective-1000">
          <div className="octahedron-container animate-spin-3d-slow">
            <div className="octahedron">
              <div className="octa-face octa-1"></div>
              <div className="octa-face octa-2"></div>
              <div className="octa-face octa-3"></div>
              <div className="octa-face octa-4"></div>
              <div className="octa-face octa-5"></div>
              <div className="octa-face octa-6"></div>
              <div className="octa-face octa-7"></div>
              <div className="octa-face octa-8"></div>
            </div>
          </div>
        </div>

        {/* 3D Rotating Ring */}
        <div className="absolute bottom-[25%] left-[15%] perspective-1000">
          <div className="ring-3d animate-spin-ring">
            {[...Array(12)].map((_, i) => (
              <div
                key={i}
                className="ring-segment"
                style={{ transform: `rotateY(${i * 30}deg) translateZ(40px)` }}
              ></div>
            ))}
          </div>
        </div>

        {/* 3D Floating Sphere */}
        <div className="absolute top-[15%] right-[20%]">
          <div className="sphere animate-float-sphere">
            <div className="sphere-inner"></div>
          </div>
        </div>

        {/* 3D Pyramid */}
        <div className="absolute bottom-[40%] right-[5%] perspective-1000">
          <div
            className="pyramid-container animate-spin-3d-slow"
            style={{ animationDelay: "-5s" }}
          >
            <div className="pyramid">
              <div className="pyramid-face pyramid-front"></div>
              <div className="pyramid-face pyramid-right"></div>
              <div className="pyramid-face pyramid-back"></div>
              <div className="pyramid-face pyramid-left"></div>
              <div className="pyramid-base"></div>
            </div>
          </div>
        </div>

        {/* 3D DNA Helix */}
        <div className="absolute top-[50%] left-[3%]">
          <div className="dna-helix">
            {[...Array(10)].map((_, i) => (
              <div
                key={i}
                className="dna-pair animate-dna-rotate"
                style={{
                  animationDelay: `${i * 0.2}s`,
                  top: `${i * 25}px`,
                }}
              >
                <div className="dna-dot dna-dot-left"></div>
                <div className="dna-line"></div>
                <div className="dna-dot dna-dot-right"></div>
              </div>
            ))}
          </div>
        </div>

        {/* Rotating icons */}
        <div className="absolute top-20 left-[10%] text-4xl animate-float-rotate opacity-20">
          🎓
        </div>
        <div
          className="absolute top-40 right-[15%] text-5xl animate-float-rotate-reverse opacity-15"
          style={{ animationDelay: "-2s" }}
        >
          📚
        </div>
        <div
          className="absolute top-[60%] left-[5%] text-3xl animate-float-rotate opacity-20"
          style={{ animationDelay: "-4s" }}
        >
          💡
        </div>
        <div
          className="absolute top-[30%] right-[8%] text-4xl animate-float-rotate-reverse opacity-15"
          style={{ animationDelay: "-1s" }}
        >
          🏆
        </div>
        <div
          className="absolute bottom-[20%] left-[20%] text-5xl animate-float-rotate opacity-20"
          style={{ animationDelay: "-3s" }}
        >
          ✨
        </div>
        <div
          className="absolute bottom-[30%] right-[25%] text-3xl animate-float-rotate-reverse opacity-15"
          style={{ animationDelay: "-5s" }}
        >
          🎯
        </div>
        <div
          className="absolute top-[50%] left-[40%] text-4xl animate-float-rotate opacity-10"
          style={{ animationDelay: "-2.5s" }}
        >
          📖
        </div>
        <div
          className="absolute bottom-[10%] right-[10%] text-5xl animate-float-rotate-reverse opacity-15"
          style={{ animationDelay: "-4.5s" }}
        >
          🌟
        </div>

        {/* Gradient orbs */}
        <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[150px] animate-pulse-slow" />
        <div
          className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-violet-500/10 rounded-full blur-[120px] animate-pulse-slow"
          style={{ animationDelay: "-4s" }}
        />
        <div
          className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-indigo-600/5 rounded-full blur-[100px] animate-pulse-slow"
          style={{ animationDelay: "-2s" }}
        />

        {/* Floating geometric shapes */}
        <div className="absolute top-32 left-32 w-24 h-24 border border-indigo-500/20 rounded-2xl animate-float-slow rotate-12" />
        <div className="absolute top-60 right-40 w-20 h-20 border border-violet-500/20 rounded-full animate-float-medium" />
        <div className="absolute bottom-40 left-60 w-16 h-16 border border-indigo-400/15 rotate-45 animate-float-fast" />
        <div
          className="absolute bottom-60 right-32 w-28 h-28 border border-violet-400/15 rounded-3xl animate-float-slow"
          style={{ animationDelay: "-3s" }}
        />
      </div>

      {/* Navbar */}
      <nav className="relative z-50 bg-slate-900/80 backdrop-blur-xl border-b border-indigo-500/20 sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/40 animate-float-gentle">
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
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="group relative px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white font-semibold rounded-xl shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 transition-all duration-300 active:scale-[0.98] overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-2">
                  <span>Login</span>
                  <svg
                    className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300"
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
                </span>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12" />
                </div>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div
            className={`transform transition-all duration-1000 ${
              mounted ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
            }`}
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/30 rounded-full mb-8">
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              <span className="text-indigo-300 text-sm font-medium">
                Powered by Advanced AI
              </span>
            </div>

            {/* Main heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              Your Smart
              <span className="block bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
                College Companion
              </span>
            </h1>

            <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-12 leading-relaxed">
              Experience the future of campus assistance. Get instant answers
              about attendance, schedules, fees, and more with our AI-powered
              chatbot designed exclusively for students.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/login"
                className="group relative px-8 py-4 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white font-semibold rounded-2xl shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:shadow-indigo-500/40 transition-all duration-300 active:scale-[0.98] overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-2 text-lg">
                  <span>Get Started</span>
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
                </span>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12" />
                </div>
              </Link>
              <a
                href="#features"
                className="px-8 py-4 text-slate-300 hover:text-white font-semibold rounded-2xl border border-slate-700 hover:border-indigo-500/50 hover:bg-slate-800/50 transition-all duration-300 flex items-center gap-2"
              >
                <span>Learn More</span>
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </a>
            </div>
          </div>

          {/* Stats */}
          <div
            className={`mt-20 grid grid-cols-2 md:grid-cols-4 gap-6 transform transition-all duration-1000 delay-300 ${
              mounted ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
            }`}
          >
            {stats.map((stat, idx) => (
              <div
                key={idx}
                className="p-6 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl hover:border-indigo-500/30 transition-all duration-300 hover:-translate-y-1"
              >
                <p className="text-3xl font-bold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                  {stat.number}
                </p>
                <p className="text-slate-400 text-sm font-medium mt-1">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section
        id="features"
        className="relative z-10 py-24 px-4 sm:px-6 lg:px-8"
      >
        <div className="max-w-7xl mx-auto">
          <div
            className={`text-center mb-16 transform transition-all duration-1000 ${
              mounted ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
            }`}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Everything You Need,{" "}
              <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                One Chat Away
              </span>
            </h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Our AI assistant understands your queries and provides accurate
              information instantly. No more waiting in queues or searching
              through portals.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <div
                key={idx}
                className={`group p-6 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl hover:border-indigo-500/40 transition-all duration-500 hover:-translate-y-2 hover:shadow-xl hover:shadow-indigo-500/10 transform ${
                  mounted
                    ? "translate-y-0 opacity-100"
                    : "translate-y-10 opacity-0"
                }`}
                style={{ transitionDelay: `${400 + idx * 100}ms` }}
              >
                <div
                  className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}
                >
                  <span className="text-2xl">{feature.icon}</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              How It{" "}
              <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
                Works
              </span>
            </h2>
            <p className="text-slate-400 text-lg">
              Getting started is simple and takes just seconds
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Login",
                description:
                  "Sign in with your student credentials to access your personalized dashboard.",
                icon: "🔐",
              },
              {
                step: "02",
                title: "Ask Anything",
                description:
                  "Type your question in natural language - our AI understands context and intent.",
                icon: "💭",
              },
              {
                step: "03",
                title: "Get Answers",
                description:
                  "Receive accurate, personalized responses based on your academic records.",
                icon: "✅",
              },
            ].map((item, idx) => (
              <div
                key={idx}
                className="relative text-center p-8 bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-2xl"
              >
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-sm font-bold rounded-full">
                  Step {item.step}
                </div>
                <div className="w-16 h-16 mx-auto mt-4 mb-4 rounded-2xl bg-slate-700/50 flex items-center justify-center">
                  <span className="text-3xl">{item.icon}</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-slate-400">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="relative p-12 bg-gradient-to-br from-indigo-600/20 via-violet-600/20 to-purple-600/20 backdrop-blur-xl border border-indigo-500/30 rounded-3xl overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-violet-500/20 rounded-full blur-3xl" />

            <div className="relative z-10 text-center">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Ready to Get Started?
              </h2>
              <p className="text-indigo-200 text-lg mb-8 max-w-xl mx-auto">
                Join thousands of students who are already using our AI
                assistant to make their college life easier.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 font-bold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 active:scale-[0.98]"
              >
                <span className="text-lg">Start Chatting Now</span>
                <svg
                  className="w-5 h-5"
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
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-8 px-4 border-t border-slate-800">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-slate-500 text-sm">
            © 2026 College Assistant. Built with ❤️ for students.
          </p>
        </div>
      </footer>

      {/* Styles */}
      <style>{`
        .grid-bg {
          background-image: 
            linear-gradient(rgba(99, 102, 241, 0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.08) 1px, transparent 1px);
          background-size: 60px 60px;
        }

        /* 3D Perspective */
        .perspective-1000 {
          perspective: 1000px;
        }

        /* 3D Cube Styles */
        .cube-container {
          width: 80px;
          height: 80px;
          transform-style: preserve-3d;
        }

        .cube {
          width: 100%;
          height: 100%;
          position: relative;
          transform-style: preserve-3d;
        }

        .cube-small {
          width: 50px;
          height: 50px;
        }

        .cube-face {
          position: absolute;
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.2) 100%);
          border: 1px solid rgba(139, 92, 246, 0.4);
          backdrop-filter: blur(5px);
        }

        .cube-small .cube-face {
          width: 50px;
          height: 50px;
        }

        .cube-front  { transform: rotateY(0deg) translateZ(40px); }
        .cube-back   { transform: rotateY(180deg) translateZ(40px); }
        .cube-right  { transform: rotateY(90deg) translateZ(40px); }
        .cube-left   { transform: rotateY(-90deg) translateZ(40px); }
        .cube-top    { transform: rotateX(90deg) translateZ(40px); }
        .cube-bottom { transform: rotateX(-90deg) translateZ(40px); }

        .cube-small .cube-front  { transform: rotateY(0deg) translateZ(25px); }
        .cube-small .cube-back   { transform: rotateY(180deg) translateZ(25px); }
        .cube-small .cube-right  { transform: rotateY(90deg) translateZ(25px); }
        .cube-small .cube-left   { transform: rotateY(-90deg) translateZ(25px); }
        .cube-small .cube-top    { transform: rotateX(90deg) translateZ(25px); }
        .cube-small .cube-bottom { transform: rotateX(-90deg) translateZ(25px); }

        /* 3D Sphere */
        .sphere {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.6), rgba(99, 102, 241, 0.2) 50%, rgba(30, 27, 75, 0.8));
          box-shadow: 
            inset -10px -10px 20px rgba(0, 0, 0, 0.5),
            inset 5px 5px 10px rgba(139, 92, 246, 0.3),
            0 0 40px rgba(139, 92, 246, 0.3);
        }

        .sphere-inner {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          background: radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.3) 0%, transparent 50%);
        }

        /* 3D Ring */
        .ring-3d {
          width: 80px;
          height: 80px;
          transform-style: preserve-3d;
          position: relative;
        }

        .ring-segment {
          position: absolute;
          width: 8px;
          height: 30px;
          background: linear-gradient(180deg, rgba(99, 102, 241, 0.6) 0%, rgba(139, 92, 246, 0.3) 100%);
          border-radius: 4px;
          left: 50%;
          top: 50%;
          margin-left: -4px;
          margin-top: -15px;
          box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
        }

        /* 3D Pyramid */
        .pyramid-container {
          width: 60px;
          height: 60px;
          transform-style: preserve-3d;
        }

        .pyramid {
          width: 100%;
          height: 100%;
          position: relative;
          transform-style: preserve-3d;
          transform: rotateX(-10deg);
        }

        .pyramid-face {
          position: absolute;
          width: 0;
          height: 0;
          border-left: 30px solid transparent;
          border-right: 30px solid transparent;
          border-bottom: 50px solid rgba(99, 102, 241, 0.4);
          transform-origin: bottom center;
        }

        .pyramid-front { transform: rotateX(30deg) translateZ(0) translateY(-25px); }
        .pyramid-right { transform: rotateY(90deg) rotateX(30deg) translateZ(0) translateY(-25px); }
        .pyramid-back { transform: rotateY(180deg) rotateX(30deg) translateZ(0) translateY(-25px); }
        .pyramid-left { transform: rotateY(-90deg) rotateX(30deg) translateZ(0) translateY(-25px); }

        .pyramid-base {
          position: absolute;
          width: 60px;
          height: 60px;
          background: rgba(139, 92, 246, 0.3);
          transform: rotateX(90deg) translateZ(-25px);
        }

        /* DNA Helix */
        .dna-helix {
          position: relative;
          height: 250px;
          width: 60px;
        }

        .dna-pair {
          position: absolute;
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .dna-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: linear-gradient(135deg, rgba(99, 102, 241, 0.8), rgba(139, 92, 246, 0.6));
          box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
        }

        .dna-line {
          flex: 1;
          height: 2px;
          background: linear-gradient(90deg, rgba(99, 102, 241, 0.6), rgba(139, 92, 246, 0.4));
          margin: 0 5px;
        }

        /* Octahedron */
        .octahedron-container {
          width: 50px;
          height: 50px;
          transform-style: preserve-3d;
        }

        .octahedron {
          width: 100%;
          height: 100%;
          position: relative;
          transform-style: preserve-3d;
        }

        .octa-face {
          position: absolute;
          width: 0;
          height: 0;
          border-left: 25px solid transparent;
          border-right: 25px solid transparent;
          border-bottom: 35px solid rgba(139, 92, 246, 0.4);
          transform-origin: center bottom;
        }

        .octa-1 { transform: rotateY(0deg) rotateX(35deg) translateZ(0); }
        .octa-2 { transform: rotateY(90deg) rotateX(35deg) translateZ(0); }
        .octa-3 { transform: rotateY(180deg) rotateX(35deg) translateZ(0); }
        .octa-4 { transform: rotateY(270deg) rotateX(35deg) translateZ(0); }
        .octa-5 { transform: rotateY(0deg) rotateX(-35deg) rotateZ(180deg) translateZ(0); }
        .octa-6 { transform: rotateY(90deg) rotateX(-35deg) rotateZ(180deg) translateZ(0); }
        .octa-7 { transform: rotateY(180deg) rotateX(-35deg) rotateZ(180deg) translateZ(0); }
        .octa-8 { transform: rotateY(270deg) rotateX(-35deg) rotateZ(180deg) translateZ(0); }

        /* Animations */
        @keyframes spin-3d {
          0% { transform: rotateX(0deg) rotateY(0deg); }
          100% { transform: rotateX(360deg) rotateY(360deg); }
        }

        @keyframes spin-3d-reverse {
          0% { transform: rotateX(360deg) rotateY(0deg); }
          100% { transform: rotateX(0deg) rotateY(360deg); }
        }

        @keyframes spin-3d-slow {
          0% { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
          100% { transform: rotateX(360deg) rotateY(360deg) rotateZ(360deg); }
        }

        @keyframes spin-ring {
          0% { transform: rotateX(70deg) rotateZ(0deg); }
          100% { transform: rotateX(70deg) rotateZ(360deg); }
        }

        @keyframes float-sphere {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-20px) scale(1.1); }
        }

        @keyframes dna-rotate {
          0%, 100% { 
            transform: rotateY(0deg) scaleX(1);
            opacity: 0.8;
          }
          25% {
            transform: rotateY(90deg) scaleX(0.3);
            opacity: 0.4;
          }
          50% { 
            transform: rotateY(180deg) scaleX(1);
            opacity: 0.8;
          }
          75% {
            transform: rotateY(270deg) scaleX(0.3);
            opacity: 0.4;
          }
        }
        
        @keyframes float-rotate {
          0%, 100% { 
            transform: translateY(0) rotate(0deg); 
          }
          50% { 
            transform: translateY(-30px) rotate(180deg); 
          }
        }
        
        @keyframes float-rotate-reverse {
          0%, 100% { 
            transform: translateY(0) rotate(360deg); 
          }
          50% { 
            transform: translateY(-25px) rotate(180deg); 
          }
        }
        
        @keyframes float-slow {
          0%, 100% { transform: translateY(0) rotate(12deg); }
          50% { transform: translateY(-20px) rotate(15deg); }
        }
        
        @keyframes float-medium {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-30px); }
        }
        
        @keyframes float-fast {
          0%, 100% { transform: translateY(0) rotate(45deg); }
          50% { transform: translateY(-25px) rotate(50deg); }
        }
        
        @keyframes float-gentle {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-5px); }
        }
        
        @keyframes pulse-slow {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.1); }
        }

        .animate-spin-3d { animation: spin-3d 15s linear infinite; }
        .animate-spin-3d-reverse { animation: spin-3d-reverse 12s linear infinite; }
        .animate-spin-3d-slow { animation: spin-3d-slow 20s linear infinite; }
        .animate-spin-ring { animation: spin-ring 8s linear infinite; }
        .animate-float-sphere { animation: float-sphere 4s ease-in-out infinite; }
        .animate-dna-rotate { animation: dna-rotate 3s ease-in-out infinite; }
        .animate-float-rotate { animation: float-rotate 12s ease-in-out infinite; }
        .animate-float-rotate-reverse { animation: float-rotate-reverse 15s ease-in-out infinite; }
        .animate-float-slow { animation: float-slow 8s ease-in-out infinite; }
        .animate-float-medium { animation: float-medium 6s ease-in-out infinite; }
        .animate-float-fast { animation: float-fast 5s ease-in-out infinite; }
        .animate-float-gentle { animation: float-gentle 3s ease-in-out infinite; }
        .animate-pulse-slow { animation: pulse-slow 8s ease-in-out infinite; }
      `}</style>
    </div>
  );
}
