import React, { useContext, useState, useEffect } from "react";
import { ScriptContext } from "../context/ScriptContext";
import { FaUserPlus, FaUser, FaTimes } from "react-icons/fa";
import "../styles/other-pages.css";

const CrewManagement = () => {
  const { scriptData, setScriptData } = useContext(ScriptContext);
  const [crewList, setCrewList] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [newCrewName, setNewCrewName] = useState("");
  const [newCrewRole, setNewCrewRole] = useState("");

  useEffect(() => {
    if (scriptData?.crew || scriptData?.actors) {
      const combined = [
        ...(scriptData.crew || []),
        ...(scriptData.actors || []),
      ];
      setCrewList(combined);
    } else {
      setCrewList([]);
    }
  }, [scriptData]);

  const handleAddCrew = () => {
    if (newCrewName && newCrewRole) {
      const newMember = { name: newCrewName, role: newCrewRole };
      const currentCrew = scriptData?.crew || [];
      const updatedCrew = [...currentCrew, newMember];
      const combinedForDisplay = [...updatedCrew, ...(scriptData?.actors || [])];
      setCrewList(combinedForDisplay);
  
      setScriptData(prev => ({
        ...prev,
        crew: updatedCrew
      }));

      setNewCrewName("");
      setNewCrewRole("");
      setShowModal(false);
    } else {
      if (typeof window !== 'undefined' && window.showSiteToast) {
        window.showSiteToast('Please enter both name and role.');
      } else {
        // eslint-disable-next-line no-console
        console.log('Please enter both name and role.');
      }
    }
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Crew Management</h1>
      <p className="page-subtitle">Manage your cast and crew assignments.</p>

  {!scriptData?.uploadedScript ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No Script Loaded</h3>
          <p>Please upload a script in the Script Manager to manage your crew.</p>
        </div>
      ) : (
        <div className="crew-section">
          <div className="crew-list">
            {crewList.map((member, index) => (
              <div key={index} className="crew-card">
                <FaUser className="card-icon" />
                <h3>{member.name}</h3>
                <p>{member.role}</p>
              </div>
            ))}
          </div>
          <div className="add-crew-card" onClick={() => setShowModal(true)}>
            <FaUserPlus className="card-icon" />
            <h3>Add New Crew Member</h3>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Add Crew Member</h2>
            <div className="modal-form">
              <div className="form-row">
                <label>Name</label>
                <input
                  type="text"
                  value={newCrewName}
                  onChange={(e) => setNewCrewName(e.target.value)}
                  placeholder="e.g., John Doe"
                />
              </div>
              <div className="form-row">
                <label>Role</label>
                <input
                  type="text"
                  value={newCrewRole}
                  onChange={(e) => setNewCrewRole(e.target.value)}
                  placeholder="e.g., Director"
                />
              </div>
              <button className="action-button add-button" onClick={handleAddCrew}>Add Crew</button>
            </div>
            <button className="close-modal-btn" onClick={() => setShowModal(false)}><FaTimes /></button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CrewManagement;