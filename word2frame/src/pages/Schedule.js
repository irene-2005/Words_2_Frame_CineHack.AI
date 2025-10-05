import React, { useContext } from "react";
import { ScriptContext } from "../context/ScriptContext";
import { FaCalendarAlt, FaMapMarkerAlt, FaUser } from "react-icons/fa";
import "../styles/other-pages.css";

const Schedule = () => {
  const { scriptData } = useContext(ScriptContext);

  return (
    <div className="page-container">
      <h1 className="page-title">Schedule</h1>
      <p className="page-subtitle">Your automatically generated shooting schedule.</p>

      {!scriptData.uploadedScript ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No Script Loaded</h3>
          <p>Please upload a script in the Script Manager to view the schedule.</p>
        </div>
      ) : (
        <div className="schedule-list">
          {scriptData.scheduleData.map((item) => (
            <div key={item.id} className="schedule-item">
              <div className="schedule-date">
                <FaCalendarAlt className="date-icon" />
                <span>{item.date}</span>
              </div>
              <div className="schedule-details">
                <h3>{item.scene}</h3>
                <p><FaMapMarkerAlt /> <strong>Location:</strong> {item.location}</p>
                <p><FaUser /> <strong>Cast:</strong> {item.cast.join(', ')}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Schedule;