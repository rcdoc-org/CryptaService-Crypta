import React from 'react';
import Card from './Card';

const StaffInfo = ({ animarum = {} }) => (
  <section id="staff-info">
    <Card title="Employees">
      <p>Deacons: {animarum.fullTime_deacons}</p>
      <p>Brothers: {animarum.fullTime_brothers}</p>
      <p>Sisters: {animarum.fullTime_sisters}</p>
      <p>Lay Staff: {animarum.fullTime_other}</p>
      <p>Part Time: {animarum.partTime_staff}</p>
      <p>Catechist Paid: {animarum.catechist_paid}</p>
    </Card>
    <Card title="Volunteers">
      <p>Total: {animarum.volunteers}</p>
      <p>Catechist Vol: {animarum.catechist_vol}</p>
      <p>Youth Volunteers: {animarum.volunteersWorkingYouth}</p>
      <p>RCIA/RCIC: {animarum.rcia_rcic}</p>
    </Card>
  </section>
);

export default StaffInfo;