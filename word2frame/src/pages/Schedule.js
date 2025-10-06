import React, { useContext } from 'react';
import '../styles/other-pages.css';
import { ScriptContext } from '../context/ScriptContext';
import { FaCalendarAlt, FaMapMarkerAlt, FaUser } from 'react-icons/fa';

const Schedule = () => {
  const { scriptData } = useContext(ScriptContext);
  const source = scriptData?.scheduleData || [];

  // 🔗 TODO: Integrate schedule CRUD with backend (Firebase / Flask)
  // Example: await fetch('/api/schedule', { method: 'POST', body: JSON.stringify(newEntry) })

  return (
    <div className="page-container">
      <h1 className="page-title">Schedule</h1>
      <p className="page-subtitle">Shooting schedule and call sheets</p>

      {!source || source.length === 0 ? (
        <div className="empty-state-message">
          <h3 className="section-heading">No scheduled days</h3>
          <p>Use Script Manager to create a shooting schedule for your project.</p>
        </div>
      ) : (
        <div className="schedule-list">
          {source.map((s) => (
            <div key={s.id} className="schedule-item card">
              <div className="schedule-date">
                <FaCalendarAlt className="date-icon" />
                <strong style={{ marginLeft: 8 }}>{s.date}</strong>
              </div>
              <div className="schedule-details">
                <h3>{s.scene}</h3>
                <p><FaMapMarkerAlt /> <strong>Location:</strong> {s.location}</p>
                <p><FaUser /> <strong>Cast:</strong> {s.cast.join(', ')}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Schedule;