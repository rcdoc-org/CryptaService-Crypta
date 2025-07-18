import React from 'react';
import Card from './Card';

const BirthInfo = ({ dateOfBirth, birthPlace, baptismDate, baptismPlace }) => (
  <section id="birth-info">
    <Card title="Birth/Sacraments">
      <div className="row">
        <div className="col-md-6">
          <h6>Birth Details</h6>
          {dateOfBirth || birthPlace ? (
            <>
              {dateOfBirth && <p>Date of Birth: {dateOfBirth}</p>}
              {birthPlace && <p>Place of Birth: {birthPlace}</p>}
            </>
          ) : (
            <p>No birth details</p>
          )}
        </div>
        <div className="col-md-6">
          <h6>Sacraments</h6>
          {(baptismDate || baptismPlace) ? (
            <>
              {baptismDate && <p>Baptism Date: {baptismDate}</p>}
              {baptismPlace && <p>Place of Baptism: {baptismPlace}</p>}
            </>
          ) : (
            <p>No sacrament info</p>
          )}
        </div>
      </div>
    </Card>
  </section>
);

export default BirthInfo;