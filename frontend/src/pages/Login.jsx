import React, { useState } from 'react';
import '../styles/Login.css'
import Card from '../components/Card';
import logo from '../assets/images/logo.png';
import { login } from '../api/auth';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [step, setStep] = useState(1);
  const [error, setError] = useState(null);

  const handleEmailSubmit = (e) => {
    e.preventDefault()
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailRegex.test(email)) {
      setError(null);
      setStep(2);
    } else {
      setError('Please enter a valid email address');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const { data } = await login({ email, password });
      localStorage.setItem('token', data.access_token);
      window.location.href = '/';
    } catch (err) {
      setError('Invalid Credentials');
    }
  };

return (
  <div className="d-flex justify-content-center align-items-center vh-100 login-background">
    <Card className="login-card text-center rounded-4 shadow p-4">
      <img src={logo} alt="Company Logo" className="login-logo mb-4" />
      <h4 className="mb-4">Sign in to Your Account</h4>
      <form onSubmit={step === 1 ? handleEmailSubmit : handleLogin} className="text-start">
          <div className="mb-4">
            <label htmlFor="email" className="form-label">Email</label>
            <input
              type="email"
              className="form-control"
              id="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
              }
              }
              required
              />
          </div>
        {step === 2 && (
          <>
            <div className="mb-4">
              <label htmlFor="password" className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                />
            </div>
            {error && <div className="text-danger mb-2">{error}</div>}
          </>
        )}
        <button type="submit" className="btn btn-primary w-100 btn-login mb-3">
          {step === 1 ? "Next" : "Sign In"}
        </button>
        {step === 2 && (
          <button type="button" className="btn btn-link w-100 mb-3" onClick={() => setStep(1)}>
            Back
          </button>
        )}
        <button
          type="button"
          className="btn btn-primary w-100 btn-login mb-3"
          onClick={() => {
            localStorage.clear();
            window.location.href = '/register';
          }}
          >
            Register
            </button>
          </form>
        <small className="text-muted d-block mt-4">Need help? Contact <a href="mailto:helpdesk@rcdoc.org">helpdesk@rcdoc.org</a></small>
      </Card>
    </div>
  );
};

export default Login;