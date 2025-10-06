import React, { useContext } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import '../styles/other-pages.css';
import { ScriptContext } from '../context/ScriptContext';

const BudgetPrediction = () => {
  const { scriptData } = useContext(ScriptContext);
  const perScene = scriptData?.budget?.perScene || [];
  const total = scriptData?.budget?.total || 0;

  // 🤖 TODO: Send script to Flask AI for more accurate budget prediction
  // const resp = await fetch('/api/predict_budget', { method: 'POST', body: JSON.stringify({ scriptText }) });

  const chartData = perScene.map((d) => ({ name: d.scene, value: d.total }));

  return (
    <div className="page-container">
      <h1 className="page-title">Budget Prediction</h1>
      <p className="page-subtitle">Estimated costs based on scene breakdown</p>

      <div className="grid-2">
        <div className="card">
          <h3>Estimated Total</h3>
          <p style={{ fontSize: 22, color: 'var(--accent)' }}>₹ {total.toLocaleString('en-IN')}</p>
          <div style={{ height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#ccc" />
                <YAxis stroke="#ccc" />
                <Tooltip />
                <Bar dataKey="value" fill="var(--accent)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3>Breakdown</h3>
          {perScene.length === 0 ? <p>No budget data available. Run analysis in Script Manager.</p> : (
            <ul>
              {perScene.map((p, i) => (
                <li key={i}><strong>{p.scene}:</strong> ₹ {p.total.toLocaleString('en-IN')}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default BudgetPrediction;
