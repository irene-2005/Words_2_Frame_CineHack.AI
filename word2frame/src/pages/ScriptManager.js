import React, { useState, useContext, useEffect } from "react";
import "../styles/ScriptManager.css";
import { ScriptContext } from "../context/ScriptContext";
import { FaFileUpload, FaTimes, FaMapMarkerAlt, FaUser, FaTag } from "react-icons/fa";

const ScriptManager = () => {
  const { scriptData, setScriptData } = useContext(ScriptContext);
  const [breakdownData, setBreakdownData] = useState([]);
  const [expandedIndex, setExpandedIndex] = useState(null);
  // ✅ Corrected: initialize filteredScenes with an empty array or the current sceneData
  const [filteredScenes, setFilteredScenes] = useState(scriptData?.sceneData || []);
  const hasScript = !!(scriptData && scriptData.uploadedScript);
  
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedCharacter, setSelectedCharacter] = useState("");
  const [selectedProp, setSelectedProp] = useState("");

  const handleFileUpload = (event) => {
    // This function simulates the script upload and analysis.
    // In production, upload the file to Firebase Storage and then send the file/text to the Flask AI backend for analysis.
    // --- Firebase upload (commented) ---
    // const storageRef = ref(storage, `scripts/${file.name}`);
    // await uploadBytes(storageRef, file);
    // const url = await getDownloadURL(storageRef);

    // --- Flask AI breakdown call (commented) ---
    // const response = await fetch('https://your-flask-backend/predict_breakdown', {
    //   method: 'POST',
    //   body: JSON.stringify({ fileUrl: url }),
    //   headers: { 'Content-Type': 'application/json' }
    // });
    // const aiBreakdown = await response.json();
    // setScriptData({ uploadedScript: { name: file.name, url }, sceneData: aiBreakdown.scenes, budget: aiBreakdown.budget });

  const file = event.target.files[0];
    // Set uploaded script metadata; the backend/AI will populate sceneData and budget
    setScriptData(prev => ({
      ...prev,
      uploadedScript: { name: file?.name || 'Uploaded Script' },
    }));
    if (typeof window !== 'undefined' && window.showSiteToast) window.showSiteToast('Script uploaded. Analysis will run on the backend.');
  };

  const handleRemoveScript = () => {
    setScriptData({ uploadedScript: null, sceneData: [], budget: null, scheduleData: [], crew: [], reports: null, productionBoard: null });
    setBreakdownData([]);
    setFilteredScenes([]);
    setSelectedLocation("");
    setSelectedCharacter("");
    setSelectedProp("");
  };

  const toggleExpand = (i) => setExpandedIndex(expandedIndex === i ? null : i);

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
      tempScenes = tempScenes.filter((s) => [...s.props].includes(selectedProp));
    }
    setFilteredScenes(tempScenes);
  }, [selectedLocation, selectedCharacter, selectedProp, breakdownData]);
  
  const locations = [...new Set(breakdownData.map(s => s.location))];
  const characters = [...new Set(breakdownData.flatMap(s => [...s.characters]))];
  const props = [...new Set(breakdownData.flatMap(s => [...s.props]))];

  return (
    <div className="page-container">
      <h1 className="page-title">🎬 Script Manager</h1>
      <p className="page-subtitle">Instantly analyze your screenplay for production readiness.</p>

  {!scriptData?.uploadedScript ? (
        <div className="upload-section">
          <label htmlFor="script-upload" className="upload-box">
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
          />
        </div>
      ) : (
        <div className="script-view-section">
          <div className="action-row">
              <div className="uploaded-file-info">
              <strong>{scriptData?.uploadedScript?.name}</strong> uploaded.
            </div>
            <button onClick={handleRemoveScript} className="action-button remove-script-btn">
              <FaTimes /> Remove Script
            </button>
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
              {filteredScenes.length > 0 ? (
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
              ) : (
                <p className="no-scenes-message">No scenes found matching the filter criteria.</p>
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