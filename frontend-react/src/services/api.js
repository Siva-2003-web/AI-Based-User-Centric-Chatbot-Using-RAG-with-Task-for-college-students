import axios from "axios";

// Use environment variable for production, fallback to localhost for development
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

console.log("🔗 API_BASE_URL:", API_BASE_URL);
console.log("🔧 VITE_API_URL:", import.meta.env.VITE_API_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API methods
export const apiService = {
  // Authentication
  login: async (studentId, password) => {
    const response = await api.post("/auth/login", {
      student_id: studentId,
      password: password,
    });
    return response.data;
  },

  // Student data
  getProfile: async () => {
    const response = await api.get("/student/profile");
    return response.data;
  },

  getAttendance: async () => {
    const response = await api.get("/student/attendance");
    return response.data;
  },

  getSchedule: async () => {
    const response = await api.get("/student/schedule");
    return response.data;
  },

  getFees: async () => {
    const response = await api.get("/student/fees");
    return response.data;
  },

  // Actions
  bookAppointment: async (data) => {
    const response = await api.post("/student/appointment", data);
    return response.data;
  },

  applyLeave: async (data) => {
    const response = await api.post("/student/apply-leave", data);
    return response.data;
  },

  // Chat
  sendChatMessage: async (messages) => {
    const response = await api.post("/chat", { messages });
    return response.data;
  },

  getChatHistory: async (limit = 10) => {
    const response = await api.get(`/chat/history?limit=${limit}`);
    return response.data;
  },

  // File upload
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },
};

export default api;
