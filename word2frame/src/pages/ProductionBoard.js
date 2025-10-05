import React, { useContext, useState } from "react";
import "../styles/Production.css";
import { CheckCircle, XCircle, Edit3, UserCog } from "lucide-react";
import { ScriptContext } from "../context/ScriptContext";

const ProductionBoard = () => {
  const { scriptData } = useContext(ScriptContext);
  const [tasks, setTasks] = useState(() => {
    const scenes = scriptData?.sceneData || [];
    const crew = (scriptData?.crewList || []).reduce((acc, cur) => ({ ...acc, [cur.role]: cur.name }), {});

    if (scenes.length > 0) {
      return scenes.map((loc, i) => ({
        id: i + 1,
        location: loc.location || 'Unknown',
        assignedTo: crew['Production'] || crew['Camera'] || 'Crew Lead',
        role: 'Production',
        status: 'pending',
      }));
    }

    // fallback generic departments (user requested departments like VFX/Editing be present)
    return [
      { id: 1, location: 'Office', assignedTo: crew['VFX'] || 'VFX Lead', role: 'VFX', status: 'pending' },
      { id: 2, location: 'Studio', assignedTo: crew['Editing'] || 'Editing Lead', role: 'Editing', status: 'pending' },
      { id: 3, location: 'Location', assignedTo: crew['Camera'] || 'Camera Lead', role: 'Camera', status: 'pending' },
    ];
  });

  const handleStatusChange = (id, newStatus) => {
    setTasks(tasks.map((t) => (t.id === id ? { ...t, status: newStatus } : t)));
  };

  const handleEdit = (id) => {
    const newAssignee = prompt("Enter new crew lead name:");
    if (newAssignee) {
      setTasks(tasks.map((t) => (t.id === id ? { ...t, assignedTo: newAssignee } : t)));
    }
  };

  return (
    <div className="production-container">
      <h1 className="page-title">🎬 Production Board</h1>
      <p className="page-subtitle">
        Manage production workflow, assign tasks, and verify completion.
      </p>

      <div className="task-section">
        {["pre-production", "in-progress", "completed"].map((stage) => (
          <div className="task-column" key={stage}>
            <h2 className="task-stage">
              {stage === "pre-production"
                ? "🛠️ Pre-Production"
                : stage === "in-progress"
                ? "🎥 In Progress"
                : "✅ Completed"}
            </h2>

            {tasks
              .filter((t) => t.status === stage || (stage === "pre-production" && t.status === "pending"))
              .map((task) => (
                <div className="task-card" key={task.id}>
                  <div className="task-header">
                    <UserCog size={20} />
                    <h3>{task.location}</h3>
                  </div>
                  <p>
                    <strong>Role:</strong> {task.role}
                  </p>
                  <p>
                    <strong>Assigned To:</strong> {task.assignedTo}
                  </p>

                  <div className="task-actions">
                    <button
                      className="action-btn check"
                      onClick={() => handleStatusChange(task.id, "completed")}
                    >
                      <CheckCircle size={18} />
                    </button>
                    <button
                      className="action-btn cross"
                      onClick={() => handleStatusChange(task.id, "pending")}
                    >
                      <XCircle size={18} />
                    </button>
                    <button className="action-btn edit" onClick={() => handleEdit(task.id)}>
                      <Edit3 size={18} />
                    </button>
                  </div>
                </div>
              ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductionBoard;
