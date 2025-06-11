import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/NotFound.css';

const NotFound = () => (
  <div className="content text-center my-5">
    <h1>404 - Page Not Found</h1>
    <p>Oops! The page you're looking for doesn't exist.</p>
    <p>But fear not, you're still under a bright nimbus cloud of guidance. Let's get you back on the right path.</p>
    <div className="image-container my-4">
      <img src="/assets/images/nimbus_church.jpg" alt="Nimbus Church" className="img-fluid rounded" />
    </div>
    <p className="link"><Link to="/" className="btn btn-primary">Return to Home</Link></p>
  </div>
);

export default NotFound;