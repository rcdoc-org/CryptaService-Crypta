import React, { useState } from 'react';
import '../styles/Login.css'
import Card from '../components/Card';
import logo from '../assets/images/logo.png';
import { register, oauthLogin } from '../api/auth';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    try {
      await register({ email, password });
      window.location.href = '/login';
    } catch (err) {
      setError('Unable to register');
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 login-background">
    <Card className="login-card text-center rounded-4 shadow p-4">
      <img src={logo} alt="Company Logo" className="login-logo mb-4" />
      <h4 className="mb-4">Register</h4>
      <form method="post" className="text-start">
        <div className="mb-3">
          <label htmlFor="email" className="form-label">Email</label>
          <input 
            type="email"
            className="form-control"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="password" className="form-label">Password</label>
          <input 
            type="password" 
            className="form-control" 
            id="password" 
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required 
          />
        </div>
        <div className="mb-4">
          <label htmlFor="confirm" className="form-label">Confirm Password</label>
          <input 
            type="password" 
            className="form-control" 
            id="confirm" 
            placeholder="Enter your password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required 
          />
        </div>
        {error && <div className="text-danger mb-2">{error}</div>}
        <button type="submit" className="btn btn-primary w-100 btn-login mb-3">Register</button>
        <div className="text-center my-3">—or sign up with—</div>
        <button type="button" className="btn btn-light w-100 mb-2 oauth-btn oauth-google" onClick={() => oauthLogin('google')}>
            <img src="/assets/images/google-logo.png" alt="Google Logo" className="oauth-logo me-2" />Google
          </button>
          <button type="button" className="btn btn-light w-100 oauth-btn oauth-microsoft" onClick={() => oauthLogin('microsoft')}>
            <img src="/assets/images/microsoft-logo.png" alt="Microsoft Logo" className="oauth-logo me-2" />
          </button>
          <button
            type="button"
            className="btn btn-primary w-100 btn-login mt-3"
            onClick={() => { window.location.href = '/login'; }}
          >
            Sign In
          </button>
      </form>
      <small className="text-muted d-block mt-4">Need help? Contact <a href="mailto:helpdesk@rcdoc.org">helpdesk@rcdoc.org</a></small>
    </Card>
  </div>
  )
};

export default Register;