import React, { useContext, useState, useEffect, useCallback } from "react";
import { ScriptContext } from "../context/ScriptContext";
import { fetchProjectReports } from "../utils/apiClient";
import { FaChartPie, FaFileAlt, FaMoneyBillWave, FaTasks, FaUsers } from "react-icons/fa";
import "../styles/other-pages.css";

const ReportsAndAnalytics = () => {
  const { projectId, authToken, refreshSnapshot } = useContext(ScriptContext);
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReports = useCallback(async () => {
    if (!projectId) {
      setReports(null);
      return;
    }

    if (!authToken) {
      setError("Sign in to view production reports.");
      setReports(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await fetchProjectReports(projectId, authToken);
      setReports(data);
    } catch (fetchError) {
      console.error("Failed to fetch reports:", fetchError);
      if (fetchError?.status === 404) {
        try {
          await refreshSnapshot(undefined, { silent: true });
        } catch (snapshotError) {
          console.error("Snapshot refresh failed while recovering reports:", snapshotError);
        }
        return;
      }
      setError("We couldn't load the latest reports. Please try again.");
      setReports(null);
    } finally {
      setLoading(false);
    }
  }, [projectId, authToken, refreshSnapshot]);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const metrics = {
    totalScenes: Number(reports?.total_scenes ?? 0),
    totalBudget: Number(reports?.total_budget ?? 0),
    totalSpent: Number(reports?.total_spent ?? 0),
    remainingBudget: Number(reports?.remaining_budget ?? 0),
    crewCount: Number(reports?.crew_count ?? 0),
    tasksCount: Number(reports?.tasks_count ?? 0),
    completionPercentage: Number(
      reports?.completion_status?.completion_percentage ?? 0
    ),
  };

  const formatNumber = (value) => (Number.isFinite(value) ? value : 0);
  const formatCurrency = (value) =>
    Number.isFinite(value) ? value.toLocaleString("en-IN") : "0";
  const formatPercentage = (value) =>
    Number.isFinite(value) ? value.toFixed(1) : "0.0";

  return (
    <div className="page-container fade-in">
      <h1 className="page-title">Reports & Analytics</h1>
      <p className="page-subtitle">Comprehensive insights into your film production.</p>

      {loading ? (
        <p>Loading reports...</p>
      ) : error ? (
        <div className="empty-state-message">
          <h3 className="section-heading">Something went wrong</h3>
          <p>{error}</p>
        </div>
      ) : !reports ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No Data Available</h3>
          <p>Please ensure a project is selected and data is available.</p>
        </div>
      ) : (
        <div className="reports-grid">
          <div className="report-card">
            <FaFileAlt className="card-icon" />
            <h3 className="section-heading">Total Scenes</h3>
            <p className="report-value">{formatNumber(metrics.totalScenes)}</p>
          </div>
          <div className="report-card">
            <FaMoneyBillWave className="card-icon" />
            <h3 className="section-heading">Total Budget</h3>
            <p className="report-value">₹{formatCurrency(metrics.totalBudget)}</p>
          </div>
          <div className="report-card">
            <FaMoneyBillWave className="card-icon" />
            <h3 className="section-heading">Total Spent</h3>
            <p className="report-value">₹{formatCurrency(metrics.totalSpent)}</p>
          </div>
          <div className="report-card">
            <FaMoneyBillWave className="card-icon" />
            <h3 className="section-heading">Remaining Budget</h3>
            <p className="report-value">₹{formatCurrency(metrics.remainingBudget)}</p>
          </div>
          <div className="report-card">
            <FaUsers className="card-icon" />
            <h3 className="section-heading">Crew Count</h3>
            <p className="report-value">{formatNumber(metrics.crewCount)}</p>
          </div>
          <div className="report-card">
            <FaTasks className="card-icon" />
            <h3 className="section-heading">Tasks Count</h3>
            <p className="report-value">{formatNumber(metrics.tasksCount)}</p>
          </div>
          <div className="report-card">
            <FaChartPie className="card-icon" />
            <h3 className="section-heading">Completion Status</h3>
            <p className="report-value">{formatPercentage(metrics.completionPercentage)}%</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportsAndAnalytics;