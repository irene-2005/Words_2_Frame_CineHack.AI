import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import loaderGif from "./loader.gif";
import "./App.css";
import Sidebar from "./components/sidebar";

// Corrected import paths to the 'pages' directory
import Home from "./pages/Home";
import ScriptManager from "./pages/ScriptManager";
import ProductionBoard from "./pages/ProductionBoard";
import Schedule from "./pages/Schedule";
import BudgetPrediction from "./pages/BudgetPrediction";
import CrewManagement from "./pages/CrewManagement";
import ReportsAndAnalytics from "./pages/ReportsAndAnalytics";
import Settings from "./pages/Settings";

// Corrected import path for ScriptContext
import { ScriptProvider } from "./context/ScriptContext"; 

function App() {
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [isSigningUp, setIsSigningUp] = useState(false);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setTimeout(() => setLoading(false), 3000);
  }, []);

  const handleShowForm = (isSignup = false) => {
    setIsSigningUp(isSignup);
    setShowForm(true);
    setError("");
  };

  const handleGoBack = () => {
    setShowForm(false);
    setUsername("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setError("");
  };

  const handleAuth = (e) => {
    e.preventDefault();
    setError("");
    if (isSigningUp && password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }
    setTimeout(() => {
      setIsLoggedIn(true);
      setShowForm(false);
      setUsername("");
      setEmail("");
      setPassword("");
      setConfirmPassword("");
    }, 500);
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <img src={loaderGif} alt="Loading..." className="loader-gif" />
      </div>
    );
  }

  // ✅ The key change is to wrap the entire app in <Router> and then
  //    conditionally render the login page or the dashboard.
  return (
    <Router>
      {isLoggedIn ? (
        <div style={{ display: "flex", backgroundColor: "#121212", minHeight: "100vh" }}>
          <Sidebar />
          <div className="content-spacer" style={{ marginLeft: "240px", flex: 1, position: "relative" }}>
            <header
              className="header"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "15px 30px",
                backgroundColor: "rgba(26, 26, 26, 0.95)",
                borderRadius: "16px",
                margin: "20px 30px",
                boxShadow: "0 4px 25px rgba(0, 0, 0, 0.4)",
                backdropFilter: "blur(10px)",
                position: "sticky",
                top: "20px",
                zIndex: 1000,
              }}
            >
              <h1
                style={{
                  color: "#FFC759",
                  fontSize: "1.8rem",
                  fontWeight: "700",
                  letterSpacing: "1px",
                }}
              >
                WORDS2FRAME
              </h1>

              <button
                onClick={() => setIsLoggedIn(false)}
                style={{
                  backgroundColor: "#FFC759",
                  border: "none",
                  padding: "10px 18px",
                  borderRadius: "10px",
                  fontWeight: "600",
                  cursor: "pointer",
                  color: "#121212",
                  transition: "0.3s",
                }}
                onMouseOver={(e) => (e.target.style.backgroundColor = "#C8A452")}
                onMouseOut={(e) => (e.target.style.backgroundColor = "#FFC759")}
              >
                Log Out
              </button>
            </header>
            <ScriptProvider>
              <main style={{ padding: "40px", textAlign: "center", color: "white" }}>
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/script-manager" element={<ScriptManager />} />
                  <Route path="/production-board" element={<ProductionBoard />} />
                  <Route path="/schedule" element={<Schedule />} />
                  <Route path="/budget-prediction" element={<BudgetPrediction />} />
                  <Route path="/crew-management" element={<CrewManagement />} />
                  <Route path="/reports-analytics" element={<ReportsAndAnalytics />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </main>
            </ScriptProvider>
          </div>
        </div>
      ) : (
        <div className="app-container">
          <div className="clapperboard-container">
            <div className="clapperboard-top">
              {[...Array(5)].map((_, i) => (
                <div className="stripe" key={i}></div>
              ))}
            </div>
            <div className="clapperboard-main">
              {showForm ? (
                <form className="login-form" onSubmit={handleAuth}>
                  <h2 className="clapperboard-title">
                    {isSigningUp ? "SIGN UP" : "LOG IN"}
                  </h2>
                  {error && (
                    <p style={{ color: "#ff4d4d", marginBottom: "10px" }}>{error}</p>
                  )}
                  {isSigningUp && (
                    <div className="form-row">
                      <span className="label">USERNAME</span>
                      <input
                        type="text"
                        placeholder="filmmaker_nick"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                      />
                    </div>
                  )}
                  <div className="form-row">
                    <span className="label">EMAIL</span>
                    <input
                      type="email"
                      placeholder="your@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-row">
                    <span className="label">PASSWORD</span>
                    <input
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  {isSigningUp && (
                    <div className="form-row">
                      <span className="label">CONFIRM PASSWORD</span>
                      <input
                        type="password"
                        placeholder="••••••••"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                      />
                    </div>
                  )}
                  <div className="button-group">
                    <button
                      type="button"
                      className="login-button"
                      onClick={handleGoBack}
                    >
                      Back
                    </button>
                    <button type="submit" className="signup-button-alt">
                      Confirm
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <h2 className="clapperboard-title">WORDS2FRAME</h2>
                  <div className="button-group">
                    <button
                      className="login-button"
                      onClick={() => handleShowForm(false)}
                    >
                      Login
                    </button>
                    <button
                      className="signup-button-alt"
                      onClick={() => handleShowForm(true)}
                    >
                      Sign Up
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </Router>
  );
}

export default App;