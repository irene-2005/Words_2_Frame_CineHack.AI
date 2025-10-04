import React from "react";
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
        <li><FaHome className="icon" /> Home</li>
        <li><FaFileAlt className="icon" /> Script Manager</li>
        <li><FaVideo className="icon" /> Production Board</li>
        <li><FaCalendarAlt className="icon" /> Schedule</li>
        <li><FaClipboardList className="icon" /> Budget Prediction</li>
        <li><FaUsers className="icon" /> Crew Management</li>
        <li><FaChartBar className="icon" /> Reports & Analytics</li>
        <li><FaCog className="icon" /> Settings</li>
      </ul>
    </div>
  );
};

export default Sidebar;
