import React, { useState, useContext, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Calendar from 'react-calendar';
import '../styles/home.css';
import 'react-calendar/dist/Calendar.css';
import { ScriptContext } from '../context/ScriptContext';

const Home = () => {
  const { scriptData } = useContext(ScriptContext);
  const [date, setDate] = useState(new Date());
  // Only show real script data (no demo fallback)
  const hasScript = !!(scriptData && scriptData.uploadedScript);

  // 🔗 TODO: Connect to Firebase to fetch project data
  // useEffect(() => {
  //   (async () => {
  //     // const project = await firebase.getProject(projectId);
  //     // setProject(project);
  //   })();
  // }, []);

  return (
    <div className="page-container">
      <h1 className="page-title">Dashboard Overview 📊</h1>
      <p className="page-subtitle">A quick look at your projects and tasks.</p>

      {hasScript ? (
        <div className="dashboard-grid">
          <div className="card projects-card">
            <h3>Budget Breakdown (per Scene)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={scriptData?.budget?.perScene || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="scene" stroke="#e0e0e0" />
                <YAxis stroke="#e0e0e0" />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="total" stroke="var(--accent)" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="card calendar-card">
            <h3>Upcoming Schedule</h3>
            <Calendar
              onChange={setDate}
              value={date}
              className="react-calendar-dark"
            />
            <ul className="schedule-list">
              {scriptData?.scheduleData?.map((item) => (
                <li key={item.id}>
                  <strong>{item.date}</strong>: {item.scene} at {item.location}
                </li>
              ))}
            </ul>
          </div>

          <div className="card recent-activity-card">
            <h3>Project Summary</h3>
            <ul>
              <li>Total Scenes: {scriptData?.reports?.sceneCount}</li>
              <li>Locations: {scriptData?.reports?.locations}</li>
              <li>Characters: {scriptData?.reports?.characters}</li>
              <li>Most Featured Character: {scriptData?.reports?.mostUsedCharacter}</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="empty-state-message">
          <h3 className="section-heading">No Script Loaded</h3>
          <p>Please upload a script in the Script Manager to view the dashboard.</p>
          <button className="action-button view-script-btn" disabled style={{ marginTop: 12 }}>
            Start New Project
          </button>
        </div>
      )}
    </div>
  );
};

export default Home;