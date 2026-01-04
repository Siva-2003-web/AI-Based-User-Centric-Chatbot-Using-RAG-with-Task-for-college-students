import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiService } from "../services/api";

export default function AttendancePage({ token, setToken }) {
  const [attendance, setAttendance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiService.getAttendance();
        setAttendance(data);
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

  return (
    <Layout token={token} setToken={setToken}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">📚 Attendance Records</h1>

        {attendance?.attendance?.length > 0 ? (
          <>
            {/* Table View */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Course
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Course ID
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Attended
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Percentage
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {attendance.attendance.map((record, idx) => (
                    <tr key={idx} className="border-t hover:bg-gray-50">
                      <td className="px-6 py-4">{record.course_name}</td>
                      <td className="px-6 py-4">{record.course_id}</td>
                      <td className="px-6 py-4">{record.attended}</td>
                      <td className="px-6 py-4">{record.total_classes}</td>
                      <td className="px-6 py-4">
                        <span
                          className={`font-semibold ${
                            record.percentage >= 75
                              ? "text-green-600"
                              : "text-red-600"
                          }`}
                        >
                          {record.percentage.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {record.percentage >= 75 ? (
                          <span className="px-3 py-1 bg-green-100 text-green-600 rounded-full text-sm">
                            ✅ Good
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-red-100 text-red-600 rounded-full text-sm">
                            ⚠️ Low
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Progress Bars */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold">Detailed View</h2>
              {attendance.attendance.map((record, idx) => (
                <div key={idx} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <h3 className="font-bold text-lg">
                        {record.course_name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {record.course_id}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold">
                        {record.percentage.toFixed(1)}%
                      </p>
                      <p className="text-sm text-gray-600">
                        {record.attended}/{record.total_classes} classes
                      </p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        record.percentage >= 75 ? "bg-green-500" : "bg-red-500"
                      }`}
                      style={{ width: `${Math.min(record.percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500">No attendance records found</p>
          </div>
        )}
      </div>
    </Layout>
  );
}
