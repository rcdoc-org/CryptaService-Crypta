import React from 'react';
import '../styles/Login.css'
import Card from '../components/Card';
import logo from '../assets/images/logo.png';

const Register = () => (
  <div className="d-flex justify-content-center align-items-center vh-100 login-background">
    <Card className="login-card text-center rounded-4 shadow p-4">
      <img src={logo} alt="Company Logo" className="login-logo mb-4" />
      <h4 className="mb-4">Register</h4>
      <form method="post" className="text-start">
        <div className="mb-3">
          <label htmlFor="username" className="form-label">Username</label>
          <input type="text" name="username" className="form-control" id="username" placeholder="Enter your username" required />
        </div>
        <div className="mb-4">
          <label htmlFor="password" className="form-label">Password</label>
          <input type="password" name="password" className="form-control" id="password" placeholder="Enter your password" required />
        </div>
        <div className="mb-4">
          <label htmlFor="password" className="form-label">Confirm Password</label>
          <input type="password" name="password" className="form-control" id="password" placeholder="Enter your password" required />
        </div>
        <button type="submit" className="btn btn-primary w-100 btn-login mb-3">Register</button>
        <div className="text-center my-3">—or sign in —</div>
        <button 
            type="submit" 
            className="btn btn-primary w-100 btn-login mb-3"
            onClick={() => {
                // Clear local storage and redirect to login page
                localStorage.clear();
                window.location.href = '/login';
            }}
            >
                Sign In
                </button>
      </form>
      <small className="text-muted d-block mt-4">Need help? Contact <a href="mailto:helpdesk@rcdoc.org">helpdesk@rcdoc.org</a></small>
    </Card>
  </div>
);

export default Register;