import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiService } from "../services/api";

export default function FeesPage({ token, setToken }) {
  const [fees, setFees] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiService.getFees();
        setFees(data);
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

  const isPaid = fees?.due === 0 || fees?.status === "Paid";

  return (
    <Layout token={token} setToken={setToken}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">💰 Fee Status</h1>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Total Fee</p>
            <p className="text-3xl font-bold text-gray-800">
              ${fees?.total || 0}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Amount Paid</p>
            <p className="text-3xl font-bold text-green-600">
              ${fees?.paid || 0}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600 mb-2">Amount Due</p>
            <p className="text-3xl font-bold text-red-600">${fees?.due || 0}</p>
          </div>
        </div>

        {/* Status Message */}
        <div
          className={`p-6 rounded-lg ${
            isPaid
              ? "bg-green-50 border-l-4 border-green-500"
              : "bg-red-50 border-l-4 border-red-500"
          }`}
        >
          {isPaid ? (
            <>
              <h2 className="text-xl font-bold text-green-700 mb-2">
                ✅ All Fees Paid
              </h2>
              <p className="text-green-600">
                Your fee payment is up to date. Thank you!
              </p>
            </>
          ) : (
            <>
              <h2 className="text-xl font-bold text-red-700 mb-2">
                ⚠️ Outstanding Balance
              </h2>
              <p className="text-red-600">
                You have an outstanding balance of ${fees?.due || 0}.
              </p>
              {fees?.due_date && (
                <p className="text-red-600 mt-2">Due Date: {fees.due_date}</p>
              )}
            </>
          )}
        </div>

        {/* Payment Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">📋 Payment Details</h2>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Status</span>
              <span className="font-semibold">{fees?.status || "N/A"}</span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Semester</span>
              <span className="font-semibold">
                {fees?.semester || "Fall 2025"}
              </span>
            </div>
            <div className="flex justify-between py-2 border-b">
              <span className="text-gray-600">Payment Method</span>
              <span className="font-semibold">
                {fees?.payment_method || "Online"}
              </span>
            </div>
          </div>
        </div>

        {/* Payment Button */}
        {!isPaid && (
          <button className="w-full py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition font-semibold text-lg">
            💳 Pay Now
          </button>
        )}
      </div>
    </Layout>
  );
}
