import React, { useState } from "react";
import "../styles/home.css";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";

const Home = () => {
  const budgetData = [
    { category: "Editing", Planned: 20000, Spent: 18000 },
    { category: "VFX", Planned: 15000, Spent: 12000 },
    { category: "Sound Mixing", Planned: 10000, Spent: 9000 },
    { category: "Marketing", Planned: 15000, Spent: 7000 },
  ];

  const overallProgress = 82;
  const [expandedCard, setExpandedCard] = useState(null);

  const toggleCard = (index) => {
    setExpandedCard(expandedCard === index ? null : index);
  };

  return (
    <div className="home-container">
      <div className="dashboard-grid">
        {/* LEFT SIDE */}
        <div className="left-column">
          {/* 🎬 Summary */}
          <div
            className={`card summary-card ${
              expandedCard === 1 ? "expanded" : ""
            }`}
            onClick={() => toggleCard(1)}
          >
            <h2>🎬 Project Summary</h2>
            <div className="progress-section">
              <p><strong>Overall Progress:</strong> {overallProgress}%</p>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${overallProgress}%` }}
                ></div>
              </div>
            </div>

            <div className="summary-details">
              <p><strong>Movie Name:</strong> Dream Chasers</p>
              <p><strong>Phase:</strong> Post-Production</p>
              <p><strong>Budget Used:</strong> ₹46,000 / ₹65,000</p>
              <p><strong>Deadline:</strong> 25 Oct 2025</p>
            </div>

            {expandedCard === 1 && (
              <div className="extra-content">
                <p>
                  The movie is currently in post-production. Editing and VFX
                  are nearing completion, with sound design in progress. Final
                  trailer cut is expected within the next two weeks.
                </p>
              </div>
            )}
          </div>

          {/* 💰 Budget */}
          <div
            className={`card chart-card ${expandedCard === 2 ? "expanded" : ""}`}
            onClick={() => toggleCard(2)}
          >
            <h2>💰 Budget Overview</h2>
            <ResponsiveContainer width="100%" height={230}>
              <BarChart data={budgetData}>
                <XAxis dataKey="category" stroke="#f5e6b3" />
                <YAxis stroke="#f5e6b3" />
                <Tooltip />
                <Legend />
                <Bar dataKey="Planned" fill="#FFC759" barSize={30} radius={[6, 6, 0, 0]} />
                <Bar dataKey="Spent" fill="#F5E6B3" barSize={30} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            {expandedCard === 2 && (
              <div className="extra-content">
                <p>
                  Spending is stable and on track. The VFX and marketing
                  departments are optimizing their costs effectively.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="right-column">
          {/* 🎥 In Progress */}
          <div
            className={`card progress-card ${
              expandedCard === 3 ? "expanded" : ""
            }`}
            onClick={() => toggleCard(3)}
          >
            <h2>🎥 Current Tasks</h2>
            <ul>
              <li>Editing final cut</li>
              <li>Composing background score</li>
              <li>VFX rendering – scene 14</li>
              <li>Trailer preview assembly</li>
            </ul>
            {expandedCard === 3 && (
              <div className="extra-content">
                <p>
                  The editing and sound teams are finalizing assets for review.
                  Trailer and poster drafts are due next week.
                </p>
              </div>
            )}
          </div>

          {/* 🗓️ Calendar */}
          <div
            className={`card calendar-card ${
              expandedCard === 4 ? "expanded" : ""
            }`}
            onClick={() => toggleCard(4)}
          >
            <h2>🗓️ Schedule</h2>
            <div className="modern-calendar">
              <Calendar className="custom-calendar" />
            </div>
            {expandedCard === 4 && (
              <div className="extra-content">
                <p>
                  Upcoming: Trailer cut review (Oct 10) and final mastering
                  (Oct 20).
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
