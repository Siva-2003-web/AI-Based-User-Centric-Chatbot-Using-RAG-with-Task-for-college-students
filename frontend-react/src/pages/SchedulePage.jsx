import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiService } from "../services/api";

export default function SchedulePage({ token, setToken }) {
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiService.getSchedule();
        setSchedule(data);
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
        <div>
          <h1 className="text-3xl font-bold">📅 Today's Schedule</h1>
          <p className="text-gray-600 mt-1">Date: {schedule?.date || "N/A"}</p>
        </div>

        {schedule?.classes?.length > 0 ? (
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
                      Time
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Faculty
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-600">
                      Department
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {schedule.classes.map((cls, idx) => (
                    <tr key={idx} className="border-t hover:bg-gray-50">
                      <td className="px-6 py-4 font-semibold">
                        {cls.course_name}
                      </td>
                      <td className="px-6 py-4">{cls.course_id}</td>
                      <td className="px-6 py-4">
                        {cls.meeting_times || "TBD"}
                      </td>
                      <td className="px-6 py-4">{cls.faculty_name || "TBD"}</td>
                      <td className="px-6 py-4">{cls.department}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Card View */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold">Detailed View</h2>
              {schedule.classes.map((cls, idx) => (
                <div key={idx} className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-xl font-bold mb-4">{cls.course_name}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Course ID</p>
                      <p className="font-semibold">{cls.course_id}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Department</p>
                      <p className="font-semibold">{cls.department}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Time</p>
                      <p className="font-semibold">
                        {cls.meeting_times || "TBD"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Faculty</p>
                      <p className="font-semibold">
                        {cls.faculty_name || "TBD"}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-6xl mb-4">🎉</p>
            <p className="text-xl text-gray-600">
              No classes scheduled for today!
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
}
