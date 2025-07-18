import React from 'react';
import Card from './Card';

const DegreeInfo = ({ degrees = [], languages = [], otherSkills }) => (
  <section id="degree-info">
    <Card title="Degrees & Certificates">
      {degrees.length > 0 ? (
        degrees.map(d => (
          <p key={d.id}>
            {d.institute} {d.subject} — {d.degreeType} ({d.dateAcquired}{d.dateExpiration ? ` - ${d.dateExpiration}` : ''})
          </p>
        ))
      ) : (
        <p>None recorded</p>
      )}
    </Card>
    <Card title="Languages & Skills">
      {languages.length > 0 ? (
        languages.map(l => (
          <p key={l.id}>{l.name} — {l.proficiency}</p>
        ))
      ) : (
        <p>None recorded</p>
      )}
      <p>Other Skills: {otherSkills || 'None'}</p>
    </Card>
  </section>
);

export default DegreeInfo;
