import React from 'react';
import Card from './Card';

const EmergencyInfo = ({ contacts = [] }) => (
  <section id="emergency-info">
    <Card title="Emergency Contacts">
      {contacts.length > 0 ? (
        contacts.map(c => (
          <div key={c.id} className="mb-4">
            <div><dt>Name:</dt> <dd>{c.name} ({c.relationship})</dd></div>
            <div><dt>Address:</dt> <dd>{c.address || 'None'}</dd></div>
            <div><dt>Phone 1:</dt> <dd>{c.phone1 || 'Not Recorded'}</dd></div>
            <div><dt>Phone 2:</dt> <dd>{c.phone2 || 'Not Recorded'}</dd></div>
            <div><dt>Email 1:</dt> <dd>{c.email1 || 'Not Recorded'}</dd></div>
            <div><dt>Email 2:</dt> <dd>{c.email2 || 'Not Recorded'}</dd></div>
          </div>
        ))
      ) : (
        <p>None recorded</p>
      )}
    </Card>
  </section>
);

export default EmergencyInfo;