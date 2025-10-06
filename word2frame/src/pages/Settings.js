import React, { useState } from "react";
import { FaUser, FaEnvelope, FaLock, FaCheckCircle } from "react-icons/fa";
import "../styles/other-pages.css";

const Settings = () => {
  const [name, setName] = useState(" ");
  const [email, setEmail] = useState(" ");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleUpdateProfile = (e) => {
    e.preventDefault();
    setMessage("");
    if (name && email) {
      setTimeout(() => {
        setMessage("Profile updated successfully!");
      }, 500);
    } else {
      setMessage("Please fill out all fields.");
    }
  };

  const handleChangePassword = (e) => {
    e.preventDefault();
    setMessage("");
    if (newPassword && newPassword === confirmNewPassword) {
      setTimeout(() => {
        setMessage("Password changed successfully!");
      }, 500);
    } else {
      setMessage("Passwords do not match.");
    }
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Settings</h1>
      <p className="page-subtitle">Manage your account and preferences.</p>

      <div className="settings-grid">
        <div className="settings-card">
          <FaUser className="card-icon" />
          <h3 className="section-heading">Update Profile</h3>
          <form className="settings-form" onSubmit={handleUpdateProfile}>
            <div className="form-row">
              <label><FaUser /> Name</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="form-row">
              <label><FaEnvelope /> Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <button type="submit" className="action-button add-button">Save Changes</button>
          </form>
        </div>

        <div className="settings-card">
          <FaLock className="card-icon" />
          <h3 className="section-heading">Change Password</h3>
          <form className="settings-form" onSubmit={handleChangePassword}>
            <div className="form-row">
              <label>Current Password</label>
              <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
            </div>
            <div className="form-row">
              <label>New Password</label>
              <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
            </div>
            <div className="form-row">
              <label>Confirm Password</label>
              <input type="password" value={confirmNewPassword} onChange={(e) => setConfirmNewPassword(e.target.value)} />
            </div>
            <button type="submit" className="action-button add-button">Update Password</button>
          </form>
        </div>
      </div>
      {message && (
        <div className="success-message">
          <FaCheckCircle />
          <p>{message}</p>
        </div>
      )}
    </div>
  );
};

export default Settings;