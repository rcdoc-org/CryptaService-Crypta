import React from 'react';
import Card from './Card';

const LocationInfo = ({ physical, mailing, rectory }) => (
  <section id="location-info">
    <Card title="Address Info">
      <div className="row">
        <div className="col">
          <h6>Physical Address</h6>
          <p>{physical || 'None'}</p>
        </div>
        <div className="col">
          <h6>Mailing Address</h6>
          <p>{mailing || 'None'}</p>
        </div>
      </div>
      {rectory && (
        <div className="mt-3">
          <h6>Rectory Address</h6>
          <p>{rectory}</p>
        </div>
      )}
    </Card>
  </section>
);

export default LocationInfo;