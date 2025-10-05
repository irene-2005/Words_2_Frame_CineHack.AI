import React, { createContext, useState, useEffect } from "react";

export const ScriptContext = createContext();

export const ScriptProvider = ({ children }) => {
  const [scriptData, setScriptData] = useState(() => {
    const saved = localStorage.getItem("scriptData");
    return saved
      ? JSON.parse(saved)
      : { uploadedScript: null, sceneData: [], crewList: [], budget: { total: 0, perScene: [] } };
  });

  useEffect(() => {
    localStorage.setItem("scriptData", JSON.stringify(scriptData));
  }, [scriptData]);

  return (
    <ScriptContext.Provider value={{ scriptData, setScriptData }}>
      {children}
    </ScriptContext.Provider>
  );
};