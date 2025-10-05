import React, { useContext, useState } from 'react';
import { ScriptContext } from '../context/ScriptContext';

const departments = [
  'Production',
  'Camera',
  'Lighting',
  'Sound',
  'Editing',
  'VFX',
  'Art Department',
];

const CrewManagement = () => {
  const { scriptData, setScriptData } = useContext(ScriptContext);
  const [assignments, setAssignments] = useState(() => scriptData?.crewList?.reduce((acc, cur) => ({ ...acc, [cur.role]: cur.name }), {}) || {});

  const handleAssign = (role, name) => {
    const next = { ...assignments, [role]: name };
    setAssignments(next);
    const crewList = Object.keys(next).map((r) => ({ role: r, name: next[r] }));
    setScriptData((prev) => ({ ...prev, crewList }));
  };

  return (
    <div style={{ textAlign: 'left' }}>
      <h2 style={{ color: '#FFC759' }}>Crew Management</h2>
      <p style={{ color: '#ccc' }}>Assign leads for each department</p>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        {departments.map((d) => (
          <div key={d} style={{ background: '#0f0f0f', padding: 12, borderRadius: 8 }}>
            <strong style={{ color: '#fff' }}>{d}</strong>
            <div style={{ marginTop: 8 }}>
              <input
                placeholder={`Assign ${d} lead`}
                value={assignments[d] || ''}
                onChange={(e) => handleAssign(d, e.target.value)}
                style={{ width: '100%', padding: 8, borderRadius: 6, background: '#111', color: '#fff', border: '1px solid #222' }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CrewManagement;