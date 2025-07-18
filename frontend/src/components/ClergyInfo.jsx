import React from 'react';
import Card from './Card';

const ClergyInfo = ({ clergy = [] }) => (
  <section id="clergy-info">
    <Card title="Assigned Personnel">
      {clergy.length > 0 ? (
        clergy.map(c => (
          <p key={c.id}><a href={`/details/person/${c.id}`}>{c.name}</a> — {c.role}</p>
        ))
      ) : (
        <p>No staff assigned</p>
      )}
    </Card>
  </section>
);

export default ClergyInfo;
