import React, { useState, useEffect } from 'react';
import '../styles/Login.css';
import Card from '../components/Card';
import logo from '../assets/images/logo.png';
import { login, ssoCallback, ssoLogin, AUTH_SSO_LOGIN_URL } from '../api/auth';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../constants';
import microsoftLogo from '../assets/images/microsoft.svg';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [step, setStep] = useState(1);
  const [error, setError] = useState(null);
  const [otp, setOtp] = useState('');

  const handleSsoLogin = () => {
    const { data} = window.location.href = AUTH_SSO_LOGIN_URL;
    localStorage.setItem(ACCESS_TOKEN, data.access);
    localStorage.setItem(REFRESH_TOKEN, data.refresh);
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      (async () => {
        try {
          const { data } = await ssoCallback({ code });
          localStorage.setItem(ACCESS_TOKEN, data.access);
          localStorage.setItem(REFRESH_TOKEN, data.refresh);
          window.location.href = '/';
        } catch (err) {
          setError('SSO login failed');
        }
      })();
    }
  }, []);

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailRegex.test(email)) {
      setError(null);
      if (step === 1) {
        setStep(2);
      } else {
        setStep(3);
      }
    } else {
      setError('Please enter a valid email address');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const { data } = await login({ username: email, password, otp });
      localStorage.setItem(ACCESS_TOKEN, data.access);
      localStorage.setItem(REFRESH_TOKEN, data.refresh);
      window.location.href = '/';
    } catch (err) {
      setError(`Invalid Credentials: ${err}`);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 login-background">
      <Card className="login-card text-center rounded-4 shadow p-4">
        <img src={logo} alt="Company Logo" className="login-logo mb-4" />
        <h4 className="mb-4">Sign in to Your Account</h4>
        <form onSubmit={step === 3 ? handleLogin : handleEmailSubmit} className="text-start">
          <div className="mb-4">
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
          {step === 3 && (
            <>
              <div className="mb-4">
                <label htmlFor="otp" className="form-label">One-Time Password</label>
                <input
                  type="text"
                  className="form-control"
                  id="otp"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  required
                />
              </div>
              {error && <div className="text-danger mb-2">{error}</div>}
            </>
          )}
          <button type="submit" className="btn btn-primary w-100 btn-login mb-3">
            {step === 1 ? 'Next' : step === 2 ? 'Next' : 'Sign In'}
          </button>
          {step === 2 && (
            <button type="button" className="btn btn-link w-100 mb-3" onClick={() => setStep(1)}>
              Back
            </button>
          )}
          {step === 3 && (
            <button type="button" className="btn btn-link w-100 mb-3" onClick={() => setStep(2)}>
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
          <div className='text-center mt-2'>
            <div className='mb-1'>RCDOC SSO</div>
            <button
              type='button'
              className='btn btn-primary w-100 btn-login'
              onClick={handleSsoLogin}
              >
                <img src={microsoftLogo} alt='Microsoft' width="20" className='me-2' />
                Sign in with Microsoft
              </button>
          </div>
        </form>
        <small className="text-muted d-block mt-4">Need help? Contact <a href="mailto:helpdesk@rcdoc.org">helpdesk@rcdoc.org</a></small>
      </Card>
    </div>
  );
};

export default Login;
