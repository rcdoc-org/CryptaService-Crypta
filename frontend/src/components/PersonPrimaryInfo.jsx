import React from 'react';
import Card from './Card';

const PersonPrimaryInfo = ({ assignments = [], statuses = [] }) => (
  <section id="primary-info">
    <Card title="Primary Info">
      <div className="row">
        <div className="col">
          <h6>Current Assignment</h6>
          {assignments.filter(a => !a.date_released).length > 0 ? (
            assignments.filter(a => !a.date_released).map(a => (
              <p key={a.id}>
                {a.assignmentType} at {a.locationName} (As of {a.date_assigned})
              </p>
            ))
          ) : (
            <p>No assignments found</p>
          )}
        </div>
        <div className="col">
          <h6>Status Info</h6>
          {statuses.length > 0 ? (
            (() => {
              const latest = statuses[statuses.length - 1];
              return <p>{latest.statusName} (As of {latest.date_assigned})</p>;
            })()
          ) : (
            <p>No status recorded</p>
          )}
        </div>
      </div>
    </Card>
  </section>
);

export default PersonPrimaryInfo;