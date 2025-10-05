import React, { useContext } from 'react';
import { ScriptContext } from '../context/ScriptContext';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const BudgetPrediction = () => {
  const { scriptData } = useContext(ScriptContext);
  const data = scriptData?.budget?.perScene?.map((p) => ({ name: p.scene, value: p.total })) || [];

  return (
    <div style={{ textAlign: 'left' }}>
      <h2 style={{ color: '#FFC759' }}>Budget Prediction</h2>
      <p>Estimated total: <strong style={{ color: '#fff' }}>${scriptData?.budget?.total || 0}</strong></p>

      <div style={{ height: 260, background: '#0f0f0f', padding: 16, borderRadius: 12 }}>
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <XAxis dataKey="name" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip />
              <Bar dataKey="value" fill="#FFC759" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: '#aaa' }}>No breakdown available. Upload script in Script Manager to generate estimates.</p>
        )}
      </div>
    </div>
  );
};

export default BudgetPrediction;