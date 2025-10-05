import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { supabase } from "./supabaseClient"; // Add this line
import loaderGif from "./loader.gif";
import "./styles/App.css";
import Sidebar from "./components/sidebar";

// Pages
import Home from "./pages/Home";
import ScriptManager from "./pages/ScriptManager";
import ProductionBoard from "./pages/ProductionBoard";
import Schedule from "./pages/Schedule";
import BudgetPrediction from "./pages/BudgetPrediction";
import CrewManagement from "./pages/CrewManagement";
import ReportsAndAnalytics from "./pages/ReportsAndAnalytics";
import Settings from "./pages/Settings";

import { ScriptProvider } from "./context/ScriptContext";

function App() {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null); // Supabase session state
  const [toast, setToast] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [isSigningUp, setIsSigningUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    // Initial loading screen timeout
    setTimeout(() => setLoading(false), 3000);

    // Supabase session listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    // Apply saved accessibility mode if present
    try {
      const saved = localStorage.getItem('accessibilityMode');
      if (saved === 'high-contrast') document.documentElement.classList.add('ac-high-contrast');
      if (saved === 'colorblind') document.documentElement.classList.add('ac-colorblind');
    } catch (e) {}

    // Expose a toast helper so other components/pages can show the site toast
    try {
      window.showSiteToast = (msg) => {
        setToast(msg);
        setTimeout(() => setToast(null), 3000);
      };
    } catch (e) {}

    // Cleanup the subscription and window helper on unmount
    return () => {
      try {
        subscription.unsubscribe();
      } catch (e) {}
      try {
        if (window.showSiteToast) delete window.showSiteToast;
      } catch (e) {}
    };
  }, []);

  // Accessibility mode toggles
  const toggleHighContrast = () => {
    const root = document.documentElement;
    if (root.classList.contains('ac-high-contrast')) {
      root.classList.remove('ac-high-contrast');
      if (window.showSiteToast) window.showSiteToast('High contrast turned off');
      try { localStorage.removeItem('accessibilityMode'); } catch (e) {}
    } else {
      root.classList.remove('ac-colorblind');
      root.classList.add('ac-high-contrast');
      if (window.showSiteToast) window.showSiteToast('High contrast enabled');
      try { localStorage.setItem('accessibilityMode', 'high-contrast'); } catch (e) {}
    }
  };

  const toggleColorBlind = () => {
    const root = document.documentElement;
    if (root.classList.contains('ac-colorblind')) {
      root.classList.remove('ac-colorblind');
      if (window.showSiteToast) window.showSiteToast('Color-blind mode turned off');
      try { localStorage.removeItem('accessibilityMode'); } catch (e) {}
    } else {
      root.classList.remove('ac-high-contrast');
      root.classList.add('ac-colorblind');
      if (window.showSiteToast) window.showSiteToast('Color-blind mode enabled');
      try { localStorage.setItem('accessibilityMode', 'colorblind'); } catch (e) {}
    }
  };

  const handleShowForm = (isSignup = false) => {
    setIsSigningUp(isSignup);
    setShowForm(true);
    setError("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
  };

  const handleGoBack = () => {
    setShowForm(false);
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setError("");
  };

  const handleSupabaseLogin = async (e) => {
    e.preventDefault();
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
      // Session state will be updated by the listener, no need to manually set it.
    } catch (error) {
      setError(error.message);
    }
  };

  const handleSupabaseSignup = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }
    try {
      const { error } = await supabase.auth.signUp({ email, password });
      if (error) throw error;
  setToast("Success! Please check your email for a confirmation link.");
      // Session state will be updated by the listener
    } catch (error) {
      setError(error.message);
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <img src={loaderGif} alt="Loading..." className="loader-gif" />
      </div>
    );
  }

  return (
    <>
    <Router>
      {session ? (
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
              <h1 style={{ color: 'var(--accent)', fontSize: "1.8rem", fontWeight: "700", letterSpacing: "1px" }}>
                WORDS2FRAME
              </h1>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                {/* Accessibility icons: high contrast & color-blind-friendly */}
                <button
                  aria-label="Toggle high contrast"
                  title="High contrast"
                  onClick={toggleHighContrast}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 6,
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  {/* Sun/Moon style high contrast icon */}
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="4" stroke="var(--accent)" strokeWidth="1.4" fill="none" />
                    <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" stroke="var(--accent)" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>

                <button
                  aria-label="Toggle color blind mode"
                  title="Color-blind friendly mode"
                  onClick={toggleColorBlind}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 6,
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  {/* Two-tone palette icon */}
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2a10 10 0 100 20 10 10 0 000-20z" stroke="#0072b2" strokeWidth="1.2" fill="#0072b2" opacity="0.9" />
                    <path d="M12 2a10 10 0 0110 10H12V2z" stroke="var(--accent)" strokeWidth="1.2" fill="var(--accent)" opacity="0.9" />
                  </svg>
                </button>

                <button
                  onClick={() => supabase.auth.signOut()}
                  style={{
                    backgroundColor: 'var(--accent)',
                    border: "none",
                    padding: "10px 18px",
                    borderRadius: "10px",
                    fontWeight: "600",
                    cursor: "pointer",
                    color: 'var(--accent-contrast)',
                    transition: "0.3s",
                  }}
                >
                  Log Out
                </button>
              </div>
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
              <div className="stripe black" />
              <div className="stripe golden" />
              <div className="stripe black" />
            </div>
            <div className="clapperboard-main">
              <h2 className="clapperboard-title">WORDS2FRAME</h2>
              <p style={{ color: '#ddd', textAlign: 'center', marginBottom: 18 }}>Sign in to continue</p>
              {showForm ? (
                <form className="login-form" onSubmit={isSigningUp ? handleSupabaseSignup : handleSupabaseLogin}>
                  {error && <p style={{ color: '#ff4d4d' }}>{error}</p>}
                  <div className="form-row">
                    <span className="label">EMAIL</span>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                  </div>
                  <div className="form-row">
                    <span className="label">PASSWORD</span>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                  </div>
                  {isSigningUp && (
                    <div className="form-row">
                      <span className="label">CONFIRM PASSWORD</span>
                      <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
                    </div>
                  )}
                  <div className="button-group">
                    <button type="button" className="login-button" onClick={handleGoBack}>Back</button>
                    <button type="submit" className="signup-button-alt">Confirm</button>
                  </div>
                </form>
              ) : (
                <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                  <button className="login-button" onClick={() => { setIsSigningUp(false); setShowForm(true); }}>Login</button>
                  <button className="signup-button-alt" onClick={() => { setIsSigningUp(true); setShowForm(true); }}>Sign Up</button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </Router>
    {toast && (
      <div className="site-toast" role="status" aria-live="polite">
        <div style={{ fontSize: 14 }}>{toast}</div>
        <button className="toast-close" aria-label="Close notification" onClick={() => setToast(null)}>✕</button>
      </div>
    )}
    </>
  );
}

export default App;