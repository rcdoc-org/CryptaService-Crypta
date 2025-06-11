import React from 'react';
import Card from './Card';

const FormationInfo = ({ formationDates = {} }) => (
  <section id="formation-info">
    <Card title="Formation Dates">
      {Object.keys(formationDates).length > 0 ? (
        Object.entries(formationDates).map(([key, date]) => (
          <p key={key}>
            {key.replace(/([A-Z])/g, ' $1').trim()}: {date}
          </p>
        ))
      ) : (
        <p>No formation info</p>
      )}
    </Card>
  </section>
);

export default FormationInfo;