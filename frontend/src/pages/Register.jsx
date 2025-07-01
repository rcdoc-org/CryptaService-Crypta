import React, { useState } from 'react';
import QRCode from 'react-qr-code';
import '../styles/Login.css';
import Card from '../components/Card';
import logo from '../assets/images/logo.png';
import { register, verifyMfa } from '../api/auth';
import microsoftLogo from '../assets/images/microsoft.svg';

const Register = () => {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [otp, setOtp] = useState('');
  const [secret, setSecret] = useState('');
  const [userId, setUserId] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (step === 1) {
      if (password !== confirm) {
        setError('Passwords do not match');
        return;
      }
      try {
        const username = email;
        const { data } = await register({ username, email, password });
        setSecret(data.mfa_secret);
        setUserId(data.id);
        setStep(2);
      } catch (err) {
        setError(`Unable to register${err}`);
      }
    } else {
      try {
        await verifyMfa({ user_id: userId, otp });
        window.location.href = '/login';
      } catch (err) {
        setError('Invalid OTP');
      }
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 login-background">
      <Card className="login-card text-center rounded-4 shadow p-4">
        <img src={logo} alt="Company Logo" className="login-logo mb-4" />
        <h4 className="mb-4">Register</h4>
        <form method="post" onSubmit={handleSubmit} className="text-start">
          {step === 1 && (
            <>
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
            </>
          )}
          {step === 2 && (
            <>
              <p className="mb-3">Scan the secret below in your authenticator app and enter the code to verify.</p>
              <div className='d-flex justify-content-center mb-3'>
                <QRCode value={`otpauth://totp/Crypta:${email}?secret=${secret}&issuer=Crypta`} />
              </div>
              {/* <pre className="mb-3">{secret}</pre> */}
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
            </>
          )}
          {error && <div className="text-danger mb-2">{error}</div>}
          <button type="submit" className="btn btn-primary w-100 btn-login mb-3">{step === 1 ? 'Register' : 'Verify'}</button>
          {step === 1 && (
            <div className='text-center mt-2'>
              <div className='mb-1'>RCDOC SSO</div>
              <button
                type='button'
                className='btn btn-primary w-100 btn-login'
                onClick={() => { window.location.href = '/sso/login/'; }}
                >
                  <img src={microsoftLogo} alt='Microsoft' width='20' className='me-2' />
                  Register with Microsoft
                </button>
            </div>
          )}
          {step === 1 && (
            <button
              type="button"
              className="btn btn-primary w-100 btn-login mt-3"
              onClick={() => { window.location.href = '/login'; }}
            >
              Sign In
            </button>
          )}
        </form>
        <small className="text-muted d-block mt-4">Need help? Contact <a href="mailto:helpdesk@rcdoc.org">helpdesk@rcdoc.org</a></small>
      </Card>
    </div>
  );
};

export default Register;
