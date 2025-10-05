import React, { useContext } from "react";
import { ScriptContext } from "../context/ScriptContext";
import { FaMoneyBillAlt } from "react-icons/fa";
import "../styles/other-pages.css";

const BudgetPrediction = () => {
  const { scriptData } = useContext(ScriptContext);

  return (
    <div className="page-container">
      <h1 className="page-title">Budget Prediction</h1>
      <p className="page-subtitle">An estimate of your production budget.</p>

      {!scriptData.uploadedScript ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No Script Loaded</h3>
          <p>Please upload a script in the Script Manager to view the budget prediction.</p>
        </div>
      ) : (
        <div className="budget-section">
          <div className="total-budget-card">
            <FaMoneyBillAlt className="card-icon" />
            <h3 className="section-heading">Total Estimated Budget</h3>
            <p className="total-amount">₹{scriptData.budget?.total?.toLocaleString('en-IN')}</p>
          </div>
          <div className="budget-breakdown">
            <h3 className="section-heading">Budget per Scene</h3>
            <ul>
              {scriptData.budget?.perScene.map((item, index) => (
                <li key={index}>
                  <strong>{item.scene}:</strong> ₹{item.total.toLocaleString('en-IN')}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default BudgetPrediction;