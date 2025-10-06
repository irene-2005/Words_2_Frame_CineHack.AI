import React, { useState, useContext, useEffect } from "react";
import "../styles/ScriptManager.css";
import { FaFileUpload, FaTimes, FaMapMarkerAlt, FaUser, FaTag } from "react-icons/fa";
import { supabase } from "../supabaseClient";
import { ScriptContext } from "../context/ScriptContext";

const ScriptManager = () => {
  const {
    scriptData,
    setScriptData,
    project,
    runScriptBreakdown,
    uploadAndAnalyze,
    analysisStatus,
    statusMessage,
    isLoadingSnapshot,
  } = useContext(ScriptContext);
  const [authToken, setAuthToken] = useState(null);
  const [breakdownData, setBreakdownData] = useState([]);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [filteredScenes, setFilteredScenes] = useState(scriptData?.sceneData || []);
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedCharacter, setSelectedCharacter] = useState("");
  const [selectedProp, setSelectedProp] = useState("");

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file || !authToken) return;
    try {
      await uploadAndAnalyze(file);
      if (typeof window !== "undefined" && window.showSiteToast) {
        window.showSiteToast("Script uploaded and analyzed successfully.");
      }
    } catch (error) {
      if (typeof window !== "undefined" && window.showSiteToast) {
        window.showSiteToast(error.message || "Script upload failed");
      }
    } finally {
      event.target.value = "";
    }
  };

  const handleAnalyzeScript = async () => {
    if (!scriptData.uploadedScript?.name) return;
    try {
      await runScriptBreakdown();
    } catch (error) {
      // Error is handled in context
    }
  };

  const handleRemoveScript = () => {
    setScriptData({
      uploadedScript: null,
      sceneData: [],
      budget: { total: 0, perScene: [] },
      scheduleData: [],
      crew: [],
      actors: [],
      reports: null,
      productionBoard: {},
    });
    setBreakdownData([]);
    setFilteredScenes([]);
    setSelectedLocation("");
    setSelectedCharacter("");
    setSelectedProp("");
  };

  const toggleExpand = (i) => setExpandedIndex(expandedIndex === i ? null : i);

  useEffect(() => {
    const getSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setAuthToken(session?.access_token || null);
    };
    getSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setAuthToken(session?.access_token || null);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (scriptData?.sceneData && scriptData.sceneData.length > 0) {
      setBreakdownData(scriptData.sceneData);
      setFilteredScenes(scriptData.sceneData);
    } else {
      setBreakdownData([]);
      setFilteredScenes([]);
    }
  }, [scriptData]);

  useEffect(() => {
    let tempScenes = breakdownData || [];
    
    if (selectedLocation) {
      tempScenes = tempScenes.filter((s) => s.location === selectedLocation);
    }
    if (selectedCharacter) {
      tempScenes = tempScenes.filter((s) => [...s.characters].includes(selectedCharacter));
    }
    if (selectedProp) {
      tempScenes = tempScenes.filter((s) => [...(s.props || [])].includes(selectedProp));
    }
    setFilteredScenes(tempScenes);
  }, [selectedLocation, selectedCharacter, selectedProp, breakdownData]);
  
  const locations = [...new Set(breakdownData.map((s) => s.location))];
  const characters = [
    ...new Set(
      breakdownData.flatMap((s) => (s.characters ? [...s.characters] : []))
    ),
  ];
  const props = [
    ...new Set(breakdownData.flatMap((s) => (s.props ? [...s.props] : []))),
  ];

  const isBusy = analysisStatus === "uploading" || analysisStatus === "analyzing" || isLoadingSnapshot;

  return (
    <div className="page-container">
      <h1 className="page-title">🎬 Script Manager</h1>
      <p className="page-subtitle">Instantly analyze your screenplay for production readiness.</p>

      {analysisStatus !== "idle" && statusMessage && (
        <div className={`analysis-status analysis-${analysisStatus}`}>
          {statusMessage}
        </div>
      )}

  {!scriptData?.uploadedScript ? (
        <div className="upload-section">
          <label
            htmlFor="script-upload"
            className={`upload-box${isBusy ? " is-disabled" : ""}`}
          >
            <FaFileUpload className="upload-icon" />
            <span>Click to Upload Script</span>
            <p className="upload-info">.txt, .pdf, .docx</p>
          </label>
          <input
            type="file"
            id="script-upload"
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            style={{ display: "none" }}
            disabled={isBusy || !authToken}
          />
        </div>
      ) : (
        <div className="script-view-section">
          <div className="action-row">
            <div className="uploaded-file-info">
              <strong>{scriptData?.uploadedScript?.name}</strong> uploaded
              {project?.name ? <span style={{ marginLeft: 12, color: '#b3b3b3' }}>({project.name})</span> : null}.
            </div>
            <div style={{ display: 'flex', gap: 12 }}>
              {scriptData?.uploadedScript && analysisStatus !== "analyzing" && (
                <button
                  onClick={handleAnalyzeScript}
                  className="action-button view-script-btn"
                  disabled={isBusy}
                >
                  Re-Analyze Script
                </button>
              )}
              <button onClick={handleRemoveScript} className="action-button remove-script-btn" disabled={isBusy}>
                <FaTimes /> Remove Script
              </button>
            </div>
          </div>
          
          <div className="breakdown-section">
            <div className="filter-panel">
              <h2>Filter Breakdown</h2>
              <div className="filter-dropdowns">
                <div className="dropdown-wrapper">
                  <FaMapMarkerAlt className="dropdown-icon" />
                  <select className="breakdown-dropdown" onChange={(e) => setSelectedLocation(e.target.value)} value={selectedLocation}>
                    <option value="">All Locations</option>
                    {locations.map((loc, index) => <option key={index} value={loc}>{loc}</option>)}
                  </select>
                </div>
                <div className="dropdown-wrapper">
                  <FaUser className="dropdown-icon" />
                  <select className="breakdown-dropdown" onChange={(e) => setSelectedCharacter(e.target.value)} value={selectedCharacter}>
                    <option value="">All Cast</option>
                    {characters.map((char, index) => (
                      <option key={index} value={char}>{char}</option>
                    ))}
                  </select>
                </div>
                <div className="dropdown-wrapper">
                  <FaTag className="dropdown-icon" />
                  <select className="breakdown-dropdown" onChange={(e) => setSelectedProp(e.target.value)} value={selectedProp}>
                    <option value="">All Props</option>
                    {props.map((prop, index) => (
                      <option key={index} value={prop}>{prop}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="breakdown-grid">
              {filteredScenes.length === 0 ? (
                <p className="no-scenes-message">No scenes found. This might be a synopsis or non-script document.</p>
              ) : filteredScenes.length === 1 && filteredScenes[0].summary?.includes('%PDF') ? (
                <p className="no-scenes-message">This document appears to be a PDF synopsis. Scene breakdown is not available for synopsis documents.</p>
              ) : (
                filteredScenes.map((item, index) => (
                  <div className="breakdown-card" key={index} onClick={() => toggleExpand(index)}>
                    <div className="breakdown-header">
                      <h3>{item.scene}</h3>
                      <span>📍 {item.location}</span>
                    </div>
                    <div className="scene-summary">
                      <p>🎭 Cast: {item.characters.size > 0 ? [...item.characters].join(", ") : "N/A"}</p>
                      <p>🎒 Props: {item.props.size > 0 ? [...item.props].join(", ") : "N/A"}</p>
                    </div>
                    {expandedIndex === index && (
                      <div className="expanded-content">
                        <h4>Budget Estimate: ₹{scriptData?.budget?.perScene?.find(p => p.scene === item.scene)?.total?.toLocaleString('en-IN') || 0}</h4>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
            <div style={{ marginTop: 24, textAlign: 'right' }}>
              <h3 style={{ color: 'var(--accent)' }}>Estimated Total Budget: ₹{scriptData?.budget?.total?.toLocaleString('en-IN') || 0}</h3>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScriptManager;