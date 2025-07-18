import React from 'react';
import Card from './Card';

const MassInfo = ({ masses = [], octoberCounts = {} }) => (
  <section id="mass-info">
    <Card title="Mass Languages & Times">
      {masses.length > 0 ? masses.map(m => (
        <p key={`${m.day}-${m.time}`}>{m.day.toUpperCase()}: {m.time} — {m.language}</p>
      )) : <p>No mass schedule recorded</p>}
    </Card>
    <Card title="October Mass Counts">
      {Object.entries(octoberCounts).map(([week, count]) => (
        <p key={week}>{week}: {count}</p>
      ))}
    </Card>
  </section>
);

export default MassInfo;