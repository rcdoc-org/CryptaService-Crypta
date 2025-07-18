import React from 'react';
import Card from './Card';

const StandingInfo = ({ statuses = [] }) => (
  <section id="standing-info">
    <Card title="Standing in Diocese">
      {statuses.length > 0 ? (
        statuses.map(s => (
          <div key={s.id} className="mb-2">
            <p>
              <strong>{s.name}</strong>: {s.date_assigned}{s.date_released ? ` - ${s.date_released}` : ' - Present'}
            </p>
          </div>
        ))
      ) : (
        <p>No status history recorded</p>
      )}
    </Card>
  </section>
);

export default StandingInfo;