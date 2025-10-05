import React, { useState, useContext } from "react";
import "../styles/ScriptManager.css";
import { ScriptContext } from "../context/ScriptContext";


const estimateBudget = (scenes) => {
  // Dummy budget per scene: base + per-character + prop cost
  const perScene = scenes.map((s, idx) => {
    const base = 1500 + idx * 100; // small variance
    const perChar = (s.characters?.length || 0) * 300;
    const perProp = (s.props?.length || 0) * 50;
    const locationCost = s.location === "Beach" ? 700 : s.location === "Street" ? 300 : 400;
    const sceneTotal = base + perChar + perProp + locationCost;
    return { scene: s.scene, total: sceneTotal };
  });
  const total = perScene.reduce((sum, p) => sum + p.total, 0);
  return { total, perScene };
};

const ScriptManager = () => {
  const { scriptData, setScriptData } = useContext(ScriptContext);
  const [selectedFile, setSelectedFile] = useState(scriptData.uploadedScript || null);
  const [breakdownData, setBreakdownData] = useState(scriptData.sceneData || []);
  const [expandedIndex, setExpandedIndex] = useState(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    // Do not auto-generate breakdowns. Only persist uploaded file metadata.
    setScriptData((prev) => ({
      ...prev,
      uploadedScript: file ? { name: file.name } : null,
    }));
  };

  const toggleExpand = (i) => setExpandedIndex(expandedIndex === i ? null : i);

  const updateSceneCharacters = (i, val) => {
    const copy = [...breakdownData];
    copy[i].characters = val.split(",").map((c) => c.trim()).filter(Boolean);
    setBreakdownData(copy);
    const budget = estimateBudget(copy);
    setScriptData((prev) => ({ ...prev, sceneData: copy, budget }));
  };

  return (
    <div className="scriptmanager-container">
      <h1 className="page-title">🎬 Script Manager</h1>

      <div className="upload-section">
        <label htmlFor="script-upload" className="upload-box">
          {selectedFile ? (
            <p>
              <strong>{selectedFile.name}</strong> uploaded successfully!
            </p>
          ) : (
            <p>Click to upload your script (PDF, DOCX, or TXT)</p>
          )}
        </label>
        <input
          type="file"
          id="script-upload"
          accept=".pdf,.docx,.txt"
          onChange={handleFileUpload}
          style={{ display: "none" }}
        />
        <div style={{ marginLeft: 20, display: 'flex', gap: 10, alignItems: 'center' }}>
          <div>
            <input
              placeholder="Scene Name"
              id="new-scene-name"
              style={{ padding: 8, borderRadius: 8, border: '1px solid #333', background: '#0f0f0f', color: '#fff' }}
            />
          </div>
          <div>
            <input
              placeholder="Location"
              id="new-scene-location"
              style={{ padding: 8, borderRadius: 8, border: '1px solid #333', background: '#0f0f0f', color: '#fff' }}
            />
          </div>
          <div>
            <button
              className="upload-box"
              onClick={() => {
                const name = document.getElementById('new-scene-name').value.trim();
                const location = document.getElementById('new-scene-location').value.trim();
                if (!name) return alert('Please provide a scene name');
                const newScene = { scene: name, location: location || 'Unknown', characters: [], time: 'Day', props: [] };
                const updated = [...(breakdownData || []), newScene];
                const budget = estimateBudget(updated);
                setBreakdownData(updated);
                setScriptData((prev) => ({ ...prev, sceneData: updated, budget }));
                document.getElementById('new-scene-name').value = '';
                document.getElementById('new-scene-location').value = '';
              }}
            >
              Add Scene
            </button>
          </div>
        </div>
      </div>

      {breakdownData && breakdownData.length > 0 && (
        <div className="breakdown-section">
          <div className="breakdown-header-row">
            <h2>Script Breakdown</h2>
            <select className="breakdown-dropdown">
              <option>All Scenes</option>
              {breakdownData.map((item, index) => (
                <option key={index}>{item.scene}</option>
              ))}
            </select>
          </div>

          <div className="breakdown-grid">
            {breakdownData.map((item, index) => (
              <div className="breakdown-card" key={index} onClick={() => toggleExpand(index)}>
                <div className="breakdown-header">
                  <h3>{item.scene}</h3>
                  <span>📍 {item.location}</span>
                </div>
                <div className="scene-summary">
                  <p>⏱️ {item.time}</p>
                  <p>🎭 Characters: {item.characters.join(", ")}</p>
                  <p>🎒 Props: {item.props.join(", ")}</p>
                </div>
                {expandedIndex === index && (
                  <div className="expanded-content">
                    <h4>Budget Estimate: ${scriptData?.budget?.perScene?.find(p => p.scene === item.scene)?.total || 0}</h4>
                    <label>Characters (comma separated)</label>
                    <input type="text" value={item.characters.join(", ")}
                      onChange={(e) => updateSceneCharacters(index, e.target.value)} />
                    <p style={{ marginTop: 8 }}><strong>Props:</strong> {item.props.join(", ")}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <h3 style={{ color: '#FFC759' }}>Estimated Total Budget: ${scriptData?.budget?.total || 0}</h3>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScriptManager;
