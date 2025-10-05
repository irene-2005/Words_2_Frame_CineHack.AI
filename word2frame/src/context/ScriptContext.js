import React, { createContext, useState, useEffect } from "react";

export const ScriptContext = createContext();

export const DUMMY_SCRIPT_DATA = {
  uploadedScript: {
    name: "Demo_ Forrest Gump - Filmustage - Script - Synopsis.pdf",
    content: `
      --- PAGE 1 ---
      [Image]
      Script Synopsis
      Project name: Demo: Forrest Gump
      Created: Sep 29, 2025
      ... (Full synopsis content as provided) ...
    `,
  },
  sceneData: [
    {
      scene: "Scene 1",
      location: "Doctor's Office",
      type: "INT.",
      characters: new Set(["FORREST", "DOCTOR", "MRS. GUMP"]),
      props: new Set(["ORTHOPEDIC SHOES", "METAL LEG BRACES"]),
      time: "DAY",
    },
    {
      scene: "Scene 2",
      location: "Gump Boarding House",
      type: "INT.",
      characters: new Set(["FORREST", "MRS. GUMP", "TRAVELERS"]),
      props: new Set(["ROOM KEY"]),
      time: "DAY",
    },
    {
      scene: "Scene 3",
      location: "Bus Bench, Savannah",
      type: "EXT.",
      characters: new Set(["FORREST", "STRANGERS"]),
      props: new Set(["BOX OF CHOCOLATES"]),
      time: "DAY",
    },
  ],
  scheduleData: [
    { id: 1, scene: 'Scene 1', date: '2025-10-15', location: 'Doctor\'s Office', cast: ['Forrest', 'Doctor', 'Mrs. Gump'] },
    { id: 2, scene: 'Scene 2', date: '2025-10-16', location: 'Gump Boarding House', cast: ['Forrest', 'Mrs. Gump', 'Travelers'] },
    { id: 3, scene: 'Scene 3', date: '2025-10-17', location: 'Bus Bench, Savannah', cast: ['Forrest', 'Strangers'] },
  ],
  budget: {
    total: 350000, // Realistic INR budget for a small project
    perScene: [
      { scene: 'Scene 1', total: 100000 },
      { scene: 'Scene 2', total: 125000 },
      { scene: 'Scene 3', total: 125000 },
    ]
  },
  crew: [
    { name: 'Forrest Gump', role: 'Actor (Lead)' },
    { name: 'Mrs. Gump', role: 'Actor (Supporting)' },
    { name: 'Jenny Curran', role: 'Actor (Supporting)' },
    { name: 'Travelers', role: 'Actors (Extras)' },
    { name: 'Director', role: 'Director' },
    { name: 'DOP', role: 'Cinematographer' },
    { name: 'Production Designer', role: 'Production Designer' },
  ],
  reports: {
    sceneCount: 3,
    locations: 3,
    characters: 4,
    mostUsedCharacter: 'FORREST',
    estimatedBudget: '₹ 3,50,000'
  },
  productionBoard: {
    'Pre-Production': [
      { id: 1, title: 'Finalize Script', scene: 'All Scenes', assignedTo: 'Director' },
      { id: 2, title: 'Location Scouting', scene: 'Scene 1, 2, 3', assignedTo: 'Director, Prod. Designer' },
      { id: 3, title: 'Casting Auditions', scene: 'All Scenes', assignedTo: 'Director' },
    ],
    'Production': [
      { id: 4, title: 'Shoot Scene 1', scene: 'Scene 1', assignedTo: 'Crew' },
      { id: 5, title: 'Shoot Scene 2', scene: 'Scene 2', assignedTo: 'Crew' },
      { id: 6, title: 'Shoot Scene 3', scene: 'Scene 3', assignedTo: 'Crew' },
    ],
    'Post-Production': [
      { id: 7, title: 'Video Editing', scene: 'All Scenes', assignedTo: 'Editor' },
      { id: 8, title: 'VFX & Color Grading', scene: 'All Scenes', assignedTo: 'VFX Artist' },
      { id: 9, title: 'Audio Editing & Mixing', scene: 'All Scenes', assignedTo: 'Sound Designer' },
    ]
  }
};

export const ScriptProvider = ({ children }) => {
  const [scriptData, setScriptData] = useState({
    uploadedScript: null,
    sceneData: [],
    budget: null,
    scheduleData: [],
    crew: [],
    reports: null,
    productionBoard: null,
  });

  // No dev helpers exposed in production — keep ScriptContext pure
  useEffect(() => {}, [scriptData, setScriptData]);

  return (
    <ScriptContext.Provider value={{ scriptData, setScriptData }}>
      {children}
    </ScriptContext.Provider>
  );
};