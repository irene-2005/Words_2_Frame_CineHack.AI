import React, { useContext } from 'react';
import { ScriptContext } from '../context/ScriptContext';
import { FaPlus, FaCircle } from 'react-icons/fa';
import '../styles/Production.css';

const ProductionBoard = () => {
  const { scriptData } = useContext(ScriptContext);

  // Use real data if present
  const board = scriptData?.productionBoard || null;

  // 🔗 TODO: Sync tasks with backend (Flask API)
  // const updateTask = async (taskId, updates) => {
  //   await fetch('/api/production/tasks/' + taskId, { method: 'PATCH', body: JSON.stringify(updates) });
  // };

  return (
    <div className="page-container">
      <h1 className="page-title">Production Board</h1>
      <p className="page-subtitle">Track tasks across stages — Pre-Production, Production, Post-Production</p>

      {!board || Object.keys(board).length === 0 ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No tasks available</h3>
          <p>Use Script Manager to analyze scripts and populate production tasks.</p>
        </div>
      ) : (
        <div className="kanban-board">
          {Object.entries(board).map(([column, tasks]) => (
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