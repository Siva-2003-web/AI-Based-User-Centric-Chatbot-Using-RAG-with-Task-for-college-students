import { useState } from "react";
import Layout from "../components/Layout";
import { apiService } from "../services/api";

export default function AppointmentPage({ token, setToken }) {
  const [formData, setFormData] = useState({
    faculty_id: "",
    date: "",
    time_slot: "",
    purpose: "",
  });
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePreview = (e) => {
    e.preventDefault();
    setShowConfirm(true);
  };

  const handleConfirm = async () => {
    setLoading(true);
    setMessage(null);

    try {
      const result = await apiService.bookAppointment(formData);
      setMessage({ type: "success", text: "Appointment booked successfully!" });
      setFormData({ faculty_id: "", date: "", time_slot: "", purpose: "" });
      setShowConfirm(false);
    } catch (error) {
      setMessage({
        type: "error",
        text: error.response?.data?.detail || "Failed to book appointment",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setShowConfirm(false);
    setMessage({ type: "info", text: "Booking cancelled" });
  };

  return (
    <Layout token={token} setToken={setToken}>
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold">🗓️ Book Faculty Appointment</h1>

        {message && (
          <div
            className={`p-4 rounded-lg ${
              message.type === "success"
                ? "bg-green-50 text-green-600 border border-green-200"
                : message.type === "error"
                ? "bg-red-50 text-red-600 border border-red-200"
                : "bg-blue-50 text-blue-600 border border-blue-200"
            }`}
          >
            {message.text}
          </div>
        )}

        {!showConfirm ? (
          <form
            onSubmit={handlePreview}
            className="bg-white rounded-lg shadow p-6 space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Faculty ID
              </label>
              <input
                type="text"
                name="faculty_id"
                value={formData.faculty_id}
                onChange={handleChange}
                placeholder="e.g., FAC001"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Slot
              </label>
              <select
                name="time_slot"
                value={formData.time_slot}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              >
                <option value="">Select time slot</option>
                <option value="09:00-10:00">09:00 - 10:00 AM</option>
                <option value="10:00-11:00">10:00 - 11:00 AM</option>
                <option value="11:00-12:00">11:00 AM - 12:00 PM</option>
                <option value="14:00-15:00">02:00 - 03:00 PM</option>
                <option value="15:00-16:00">03:00 - 04:00 PM</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Purpose
              </label>
              <textarea
                name="purpose"
                value={formData.purpose}
                onChange={handleChange}
                placeholder="Reason for appointment"
                rows="3"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-semibold"
            >
              Preview Booking
            </button>
          </form>
        ) : (
          <div className="bg-white rounded-lg shadow p-6 space-y-6">
            <div className="p-4 bg-yellow-50 border-l-4 border-yellow-400">
              <p className="font-bold text-yellow-800">
                ⚠️ Confirm Appointment Booking
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Faculty ID:</span>
                <span className="font-semibold">{formData.faculty_id}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Date:</span>
                <span className="font-semibold">{formData.date}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Time:</span>
                <span className="font-semibold">{formData.time_slot}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span className="text-gray-600">Purpose:</span>
                <span className="font-semibold">{formData.purpose}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={handleCancel}
                className="py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition font-semibold"
              >
                ❌ Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={loading}
                className="py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition font-semibold"
              >
                {loading ? "Booking..." : "✅ Confirm"}
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
