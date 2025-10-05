import React from "react";
import { Link } from "react-router-dom";
import "../styles/sidebar.css";
import {
  FaHome,
  FaFileAlt,
  FaVideo,
  FaCalendarAlt,
  FaUsers,
  FaCog,
  FaClipboardList,
  FaChartBar,
} from "react-icons/fa";

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h3 className="menu-heading">Menu</h3>
      <ul className="nav-links">
        <Link to="/">
          <li><FaHome className="icon" /> Home</li>
        </Link>
        <Link to="/script-manager">
          <li><FaFileAlt className="icon" /> Script Manager</li>
        </Link>
        <Link to="/production-board">
          <li><FaVideo className="icon" /> Production Board</li>
        </Link>
        <Link to="/schedule">
          <li><FaCalendarAlt className="icon" /> Schedule</li>
        </Link>
        <Link to="/budget-prediction">
          <li><FaClipboardList className="icon" /> Budget Prediction</li>
        </Link>
        <Link to="/crew-management">
          <li><FaUsers className="icon" /> Crew Management</li>
        </Link>
        <Link to="/reports-analytics">
          <li><FaChartBar className="icon" /> Reports & Analytics</li>
        </Link>
        <Link to="/settings">
          <li><FaCog className="icon" /> Settings</li>
        </Link>
      </ul>
    </div>
  );
};

export default Sidebar;