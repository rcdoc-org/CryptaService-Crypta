import React from 'react';
import Card from './Card';

const ContactInfo = ({ emails = [], phones = [], residence, mailing }) => (
  <section id="contact-info">
    <Card title="Contact Info">
      <div className="row">
        <div className="col">
          <h6>Phone Numbers</h6>
          {phones.length > 0 ? (
            phones.map(p => (
              <p key={p.id}>
                <a href={`tel:${p.number}`}>{p.type}: {p.number}</a>
              </p>
            ))
          ) : (
            <p>Not Recorded</p>
          )}
        </div>
        <div className="col">
          <h6>Emails</h6>
          {emails.length > 0 ? (
            emails.map(e => (
              <p key={e.id}>
                <a href={`mailto:${e.email}`}>{e.type}: {e.email}</a>
              </p>
            ))
          ) : (
            <p>Not Recorded</p>
          )}
        </div>
      </div>
      <div className="row mt-3">
        <div className="col">
          <h6>Residence Address</h6>
          {residence ? (
            <address>{residence}</address>
          ) : (
            <p>None</p>
          )}
        </div>
        <div className="col">
          <h6>Mailing Address</h6>
          {mailing ? (
            <address>{mailing}</address>
          ) : (
            <p>None</p>
          )}
        </div>
      </div>
    </Card>
  </section>
);

export default ContactInfo;
