import { useState, useRef, useEffect } from "react";
import { API_BASE_URL } from "../services/api";

export default function ChatInterface({ token }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const suggestedPrompts = [
    {
      icon: "📊",
      text: "Show my attendance",
      color: "from-indigo-500 to-violet-600",
      action: "attendance",
    },
    {
      icon: "📅",
      text: "Today's schedule",
      color: "from-teal-500 to-emerald-600",
      action: "chat",
    },
    {
      icon: "📝",
      text: "Upcoming exams",
      color: "from-orange-500 to-amber-600",
      action: "chat",
    },
    {
      icon: "🤝",
      text: "Book faculty meeting",
      color: "from-fuchsia-500 to-purple-600",
      action: "chat",
    },
    {
      icon: "💳",
      text: "Check fee status",
      color: "from-rose-500 to-pink-600",
      action: "chat",
    },
    {
      icon: "👨‍🏫",
      text: "Faculty contacts",
      color: "from-sky-500 to-blue-600",
      action: "chat",
    },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch attendance directly from API
  const fetchAttendance = async () => {
    const userMessage = { role: "user", content: "Show my attendance" };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/student/attendance`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (data.attendance && data.attendance.length > 0) {
        // Calculate overall attendance
        const totalClasses = data.attendance.reduce(
          (sum, r) => sum + r.total_classes,
          0
        );
        const totalAttended = data.attendance.reduce(
          (sum, r) => sum + r.attended,
          0
        );
        const overallPercentage =
          totalClasses > 0
            ? ((totalAttended / totalClasses) * 100).toFixed(1)
            : 0;

        // Format attendance data
        let formattedContent = `📊 **Your Attendance Report**\n\n`;
        formattedContent += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        formattedContent += `📈 **Overall Attendance: ${overallPercentage}%**\n`;
        formattedContent += `   Total Classes: ${totalClasses} | Attended: ${totalAttended}\n`;
        formattedContent += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
        formattedContent += `📚 **Subject-wise Breakdown:**\n\n`;

        data.attendance.forEach((record, idx) => {
          const status = record.percentage >= 75 ? "✅" : "⚠️";
          const pct = Number(record.percentage).toFixed(1);
          formattedContent += `${idx + 1}. **${record.course_name}** (${
            record.course_id
          })\n`;
          formattedContent += `   ${status} ${pct}% | ${record.attended}/${record.total_classes} classes\n`;
          if (record.percentage < 75) {
            formattedContent += `   ⚠️ Below 75% - Needs improvement!\n`;
          }
          formattedContent += `\n`;
        });

        // Add summary
        const lowAttendance = data.attendance.filter((r) => r.percentage < 75);
        if (lowAttendance.length > 0) {
          formattedContent += `\n⚠️ **Alert:** ${lowAttendance.length} subject(s) below 75% attendance threshold.`;
        } else {
          formattedContent += `\n✅ **Great job!** All subjects have attendance above 75%.`;
        }

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: formattedContent,
            attendanceData: data.attendance,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "No attendance records found for your courses.",
          },
        ]);
      }
    } catch (error) {
      console.error("Attendance error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error: Could not fetch attendance data.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply || "Sorry, I could not process your request.",
          sources: data.sources || [],
          actions: data.actions || [],
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error: Could not connect to the server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePromptClick = (prompt) => {
    if (prompt.action === "attendance") {
      fetchAttendance();
    } else {
      sendMessage(prompt.text);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  // Parse markdown-like formatting
  const formatMessage = (content) => {
    if (!content) return content;

    // Split by lines and process
    const lines = content.split("\n");
    return lines.map((line, i) => {
      // Bold text
      let formatted = line.replace(
        /\*\*(.*?)\*\*/g,
        '<strong class="font-semibold">$1</strong>'
      );
      return (
        <span
          key={i}
          dangerouslySetInnerHTML={{ __html: formatted }}
          className="block"
        />
      );
    });
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 rounded-2xl shadow-2xl border border-indigo-500/20 overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 bg-slate-800/90 backdrop-blur-sm border-b border-indigo-500/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white tracking-tight">
              AI Assistant
            </h2>
            <p className="text-xs text-indigo-300 font-medium">
              Your personal college helper
            </p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-semibold rounded-full border border-emerald-500/30">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
              Online
            </span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 scroll-smooth">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center">
            {/* Welcome Section */}
            <div className="text-center mb-8">
              <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-xl shadow-indigo-500/40">
                <span className="text-4xl">🎓</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">
                How can I help you today?
              </h3>
              <p className="text-slate-400 max-w-md font-medium">
                Ask me anything about courses, schedules, fees, or campus
                services.
              </p>
            </div>

            {/* Quick Actions Grid */}
            <div className="w-full max-w-2xl">
              <p className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-3 text-center">
                Quick Actions
              </p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {suggestedPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePromptClick(prompt)}
                    className="group relative p-4 bg-slate-800/60 hover:bg-slate-700/80 border border-slate-700 hover:border-indigo-500/50 rounded-xl transition-all duration-200 hover:shadow-lg hover:shadow-indigo-500/20 hover:-translate-y-0.5 text-left"
                  >
                    <div
                      className={`w-10 h-10 rounded-lg bg-gradient-to-br ${prompt.color} flex items-center justify-center mb-3 shadow-md group-hover:scale-110 transition-transform duration-200`}
                    >
                      <span className="text-lg">{prompt.icon}</span>
                    </div>
                    <span className="text-sm font-semibold text-slate-300 group-hover:text-white transition-colors">
                      {prompt.text}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                } animate-fade-in`}
              >
                <div
                  className={`flex items-start gap-3 max-w-[80%] ${
                    msg.role === "user" ? "flex-row-reverse" : ""
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center shadow-md ${
                      msg.role === "user"
                        ? "bg-gradient-to-br from-indigo-500 to-violet-600"
                        : "bg-gradient-to-br from-slate-600 to-slate-700"
                    }`}
                  >
                    {msg.role === "user" ? (
                      <svg
                        className="w-4 h-4 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                    ) : (
                      <svg
                        className="w-4 h-4 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                        />
                      </svg>
                    )}
                  </div>

                  {/* Message Bubble */}
                  <div
                    className={`px-4 py-3 rounded-2xl shadow-sm ${
                      msg.role === "user"
                        ? "bg-gradient-to-br from-indigo-500 to-violet-600 text-white rounded-tr-md"
                        : "bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-md"
                    }`}
                  >
                    <div className="text-sm leading-relaxed font-medium whitespace-pre-wrap">
                      {formatMessage(msg.content)}
                    </div>

                    {/* Attendance Visual Cards */}
                    {msg.attendanceData && (
                      <div className="mt-4 pt-4 border-t border-slate-600 space-y-2">
                        <div className="grid grid-cols-2 gap-2">
                          {msg.attendanceData.map((record, i) => (
                            <div
                              key={i}
                              className={`p-3 rounded-lg border ${
                                record.percentage >= 75
                                  ? "bg-emerald-900/40 border-emerald-500/40"
                                  : "bg-amber-900/40 border-amber-500/40"
                              }`}
                            >
                              <p className="text-xs font-semibold text-slate-300 truncate">
                                {record.course_name}
                              </p>
                              <p
                                className={`text-lg font-bold ${
                                  record.percentage >= 75
                                    ? "text-emerald-400"
                                    : "text-amber-400"
                                }`}
                              >
                                {Number(record.percentage).toFixed(1)}%
                              </p>
                              <p className="text-xs text-slate-400">
                                {record.attended}/{record.total_classes} classes
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {msg.actions && msg.actions.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-600">
                        <p className="text-xs font-semibold text-slate-400 mb-1">
                          Available Actions:
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.actions.map((action, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 bg-indigo-500/20 text-indigo-300 text-xs rounded-md font-medium border border-indigo-500/30"
                            >
                              {action}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start animate-fade-in">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center shadow-md">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                  <div className="px-4 py-3 bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-md shadow-sm">
                    <div className="flex items-center gap-1.5">
                      <div
                        className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 px-6 py-4 bg-slate-800/90 backdrop-blur-sm border-t border-indigo-500/30">
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="w-full px-5 py-3.5 bg-slate-700/50 border-2 border-slate-600 rounded-xl text-white placeholder-slate-400 font-medium focus:outline-none focus:bg-slate-700 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all duration-200"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex-shrink-0 px-6 py-3.5 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white font-semibold rounded-xl shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-lg transition-all duration-200 active:scale-[0.98] flex items-center gap-2"
          >
            <span>Send</span>
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
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </form>
      </div>

      {/* Animations */}
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
