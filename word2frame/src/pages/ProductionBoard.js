import React, { useContext } from "react";
import { ScriptContext } from "../context/ScriptContext";
import { FaPlus, FaCircle } from "react-icons/fa";
import "../styles/other-pages.css";

const ProductionBoard = () => {
  const { scriptData } = useContext(ScriptContext);

  return (
    <div className="page-container">
      <h1 className="page-title">Production Board</h1>
      <p className="page-subtitle">Track your project's progress from pre-production to post.</p>

      {!scriptData.uploadedScript ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No Script Loaded</h3>
          <p>Please upload a script in the Script Manager to view the Production Board.</p>
        </div>
      ) : (
        <div className="kanban-board">
          {Object.entries(scriptData.productionBoard).map(([column, tasks]) => (
            <div key={column} className="kanban-column">
              <h3 className="column-title">{column}</h3>
              <div className="task-list">
                {tasks.map((task) => (
                  <div key={task.id} className="task-card">
                    <div className="task-header">
                      <h4>{task.title}</h4>
                      <FaCircle className="status-icon" />
                    </div>
                    <p><strong>Scene:</strong> {task.scene}</p>
                    <p><strong>Assigned:</strong> {task.assignedTo}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductionBoard;