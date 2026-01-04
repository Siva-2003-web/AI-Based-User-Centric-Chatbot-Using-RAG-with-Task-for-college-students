import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import StatCard from "../components/StatCard";
import ChatInterface from "../components/ChatInterface";
import { apiService } from "../services/api";

export default function DashboardPage({ token, setToken }) {
  const [profile, setProfile] = useState(null);
  const [attendance, setAttendance] = useState(null);
  const [schedule, setSchedule] = useState(null);
  const [fees, setFees] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileData, attendanceData, scheduleData, feesData] =
          await Promise.all([
            apiService.getProfile(),
            apiService.getAttendance(),
            apiService.getSchedule(),
            apiService.getFees(),
          ]);

        setProfile(profileData);
        setAttendance(attendanceData);
        setSchedule(scheduleData);
        setFees(feesData);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token]);

  if (loading) {
    return (
      <Layout token={token} setToken={setToken}>
        <div className="text-center py-20">
          <div className="text-6xl mb-4">⏳</div>
          <p className="text-xl text-gray-600">Loading dashboard...</p>
        </div>
      </Layout>
    );
  }

  // Calculate average attendance
  const avgAttendance =
    attendance?.attendance?.length > 0
      ? attendance.attendance.reduce((sum, r) => sum + r.percentage, 0) /
        attendance.attendance.length
      : 0;

  return (
    <Layout token={token} setToken={setToken}>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            Welcome back, {profile?.name || "Student"}! 👋
          </h1>
          <p className="text-gray-600 mt-1">Here's your academic overview</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Average Attendance"
            value={`${avgAttendance.toFixed(1)}%`}
            subtitle={avgAttendance >= 75 ? "✅ Above 75%" : "⚠️ Below 75%"}
            icon="📚"
            color={avgAttendance >= 75 ? "green" : "red"}
          />

          <StatCard
            title="Fee Status"
            value={fees?.status || "N/A"}
            subtitle={fees?.due ? `Due: $${fees.due}` : "Paid in Full"}
            icon="💰"
            color={fees?.due > 0 ? "yellow" : "green"}
          />

          <StatCard
            title="Today's Classes"
            value={schedule?.count || 0}
            subtitle={
              schedule?.classes?.[0]?.course_name?.substring(0, 20) ||
              "No classes"
            }
            icon="📅"
            color="blue"
          />
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-2xl font-bold mb-4">🚀 Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <a
              href="/profile"
              className="p-4 bg-white rounded-lg shadow hover:shadow-md transition text-center"
            >
              <div className="text-3xl mb-2">👤</div>
              <div className="font-semibold">My Profile</div>
            </a>
            <a
              href="/attendance"
              className="p-4 bg-white rounded-lg shadow hover:shadow-md transition text-center"
            >
              <div className="text-3xl mb-2">📚</div>
              <div className="font-semibold">Attendance</div>
            </a>
            <a
              href="/schedule"
              className="p-4 bg-white rounded-lg shadow hover:shadow-md transition text-center"
            >
              <div className="text-3xl mb-2">📅</div>
              <div className="font-semibold">Schedule</div>
            </a>
            <a
              href="/appointment"
              className="p-4 bg-white rounded-lg shadow hover:shadow-md transition text-center"
            >
              <div className="text-3xl mb-2">🗓️</div>
              <div className="font-semibold">Appointments</div>
            </a>
          </div>
        </div>

        {/* Chat Interface */}
        <ChatInterface token={token} />
      </div>
    </Layout>
  );
}
