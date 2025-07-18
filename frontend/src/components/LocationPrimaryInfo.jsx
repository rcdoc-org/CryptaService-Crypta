import React from 'react';
import Card from './Card';

const LocationPrimaryInfo = ({ details = {}, statuses = [] }) => (
  <section id="primary-info">
    <Card title="Primary Info">
      <div className="row">
        <div className="col-md-6 d-flex align-items-center">
          <i className="fas fa-map-marker-alt fa-lg me-2 text-muted" />
          <div>
            <small className="text-muted">Parish/Mission</small>
            <p className="mt-2">{details.is_mission ? 'Mission' : 'Parish'}</p>
          </div>
        </div>
        <div className="col-md-6 d-flex align-items-center">
          <div>
            <small className="text-muted">Parish ID</small>
            <p className="mt-2">{details.parish_id || 'Unknown'}</p>
          </div>
        </div>
      </div>
    </Card>
  </section>
);

export default LocationPrimaryInfo;