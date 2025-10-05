import React, { useContext } from "react";
import { ScriptContext } from "../context/ScriptContext";
import { FaChartPie, FaFileAlt, FaUser } from "react-icons/fa";
import "../styles/other-pages.css";

const ReportsAndAnalytics = () => {
  const { scriptData } = useContext(ScriptContext);
  const hasScript = !!(scriptData && scriptData.uploadedScript);

  return (
    <div className="page-container">
      <h1 className="page-title">Reports & Analytics</h1>
      <p className="page-subtitle">Get deep insights into your script.</p>

      {!hasScript ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No Script Loaded</h3>
          <p>Please upload a script in the Script Manager to view the reports.</p>
        </div>
      ) : (
        <div className="reports-grid">
          <div className="report-card">
            <FaFileAlt className="card-icon" />
            <h3 className="section-heading">Scene Count</h3>
            <p className="report-value">{scriptData?.reports?.sceneCount}</p>
          </div>
          <div className="report-card">
            <FaChartPie className="card-icon" />
            <h3 className="section-heading">Estimated Budget</h3>
            <p className="report-value">{scriptData?.reports?.estimatedBudget}</p>
          </div>
          <div className="report-card">
            <FaUser className="card-icon" />
            <h3 className="section-heading">Most Used Character</h3>
            <p className="report-value">{scriptData?.reports?.mostUsedCharacter}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportsAndAnalytics;