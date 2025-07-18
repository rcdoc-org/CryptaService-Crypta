import React from 'react';
import Card from './Card';

const NameInfo = ({ prefix, firstName, middleName, lastName, suffix, religiousSuffix, diocesanSuffix }) => (
  <section id="name-info">
    <Card title="Name Details">
      <div className="row">
        <div className="col-6"><strong>Prefix:</strong> {prefix || 'None'}</div>
        <div className="col-6"><strong>First Name:</strong> {firstName}</div>
      </div>
      <div className="row mt-2">
        <div className="col-6"><strong>Middle Name:</strong> {middleName || 'None'}</div>
        <div className="col-6"><strong>Last Name:</strong> {lastName}</div>
      </div>
      <div className="row mt-2">
        <div className="col-6"><strong>Suffix:</strong> {suffix || 'None'}</div>
        <div className="col-6"><strong>Religious Suffix:</strong> {religiousSuffix || 'None'}</div>
      </div>
      <div className="row mt-2">
        <div className="col-6"><strong>Diocesan Suffix:</strong> {diocesanSuffix || 'None'}</div>
      </div>
    </Card>
  </section>
);

export default NameInfo;