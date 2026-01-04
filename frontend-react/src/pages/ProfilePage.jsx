import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiService } from "../services/api";

export default function ProfilePage({ token, setToken }) {
  const [profile, setProfile] = useState(null);
  const [attendance, setAttendance] = useState(null);
  const [fees, setFees] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileData, attendanceData, feesData] = await Promise.all([
          apiService.getProfile(),
          apiService.getAttendance(),
          apiService.getFees(),
        ]);
        setProfile(profileData);
        setAttendance(attendanceData);
        setFees(feesData);
      } catch (error) {
        console.error("Error:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Layout token={token} setToken={setToken}>
        <div className="text-center py-20">Loading...</div>
      </Layout>
    );
  }

  const avgAttendance =
    attendance?.attendance?.length > 0
      ? attendance.attendance.reduce((sum, r) => sum + r.percentage, 0) /
        attendance.attendance.length
      : 0;

  return (
    <Layout token={token} setToken={setToken}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">👤 Student Profile</h1>

        {/* Personal Info */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">📋 Personal Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Name</p>
              <p className="font-semibold">{profile?.name || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Student ID</p>
              <p className="font-semibold">{profile?.student_id || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Department</p>
              <p className="font-semibold">{profile?.department || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Year</p>
              <p className="font-semibold">{profile?.year || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="font-semibold">{profile?.email || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Phone</p>
              <p className="font-semibold">{profile?.phone || "N/A"}</p>
            </div>
          </div>
        </div>

        {/* Enrolled Courses */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">📚 Enrolled Courses</h2>
          {attendance?.attendance?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Course ID</th>
                    <th className="px-4 py-2 text-left">Course Name</th>
                    <th className="px-4 py-2 text-left">Attendance</th>
                    <th className="px-4 py-2 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {attendance.attendance.map((course, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="px-4 py-2">{course.course_id}</td>
                      <td className="px-4 py-2">{course.course_name}</td>
                      <td className="px-4 py-2">
                        {course.percentage.toFixed(1)}%
                      </td>
                      <td className="px-4 py-2">
                        {course.percentage >= 75 ? (
                          <span className="text-green-600">✅ Good</span>
                        ) : (
                          <span className="text-red-600">⚠️ Low</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500">No courses found</p>
          )}
        </div>

        {/* Overall Attendance */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">
            📊 Overall Attendance Summary
          </h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">
                {avgAttendance.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Average Attendance</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">
                {attendance?.attendance?.reduce(
                  (sum, r) => sum + r.attended,
                  0
                ) || 0}
              </p>
              <p className="text-sm text-gray-600">Classes Attended</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">
                {attendance?.attendance?.reduce(
                  (sum, r) => sum + r.total_classes,
                  0
                ) || 0}
              </p>
              <p className="text-sm text-gray-600">Total Classes</p>
            </div>
          </div>
        </div>

        {/* Fee Status */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">💰 Fee Payment Status</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Fee</p>
              <p className="text-2xl font-bold">${fees?.total || 0}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Amount Paid</p>
              <p className="text-2xl font-bold text-green-600">
                ${fees?.paid || 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Amount Due</p>
              <p className="text-2xl font-bold text-red-600">
                ${fees?.due || 0}
              </p>
            </div>
          </div>
          {fees?.due === 0 ? (
            <div className="mt-4 p-3 bg-green-50 text-green-600 rounded-lg">
              ✅ All fees paid in full!
            </div>
          ) : (
            <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-lg">
              ⚠️ Outstanding balance: ${fees?.due || 0}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
