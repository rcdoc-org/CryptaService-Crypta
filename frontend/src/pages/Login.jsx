import React from 'react';
import '../styles/Login.css'
import Card from '../components/Card';

const Login = () => (
  <div className="d-flex justify-content-center align-items-center vh-100">
    <Card className="login-card text-center rounded-4 shadow p-4">
      <img src="/assets/images/logo.png" alt="Company Logo" className="login-logo mb-4" />
      <h4 className="mb-4">Sign in to Your Account</h4>
      <form method="post" className="text-start">
        <div className="mb-3">
          <label htmlFor="username" className="form-label">Username</label>
          <input type="text" name="username" className="form-control" id="username" placeholder="Enter your username" required />
        </div>
        <div className="mb-4">
          <label htmlFor="password" className="form-label">Password</label>
          <input type="password" name="password" className="form-control" id="password" placeholder="Enter your password" required />
        </div>
        <button type="submit" className="btn btn-primary w-100 btn-login mb-3">Sign In</button>
        <div className="text-center my-3">—or sign in with—</div>
        <button type="submit" name="oauth_provider" value="google" className="btn btn-light w-100 mb-2 oauth-btn oauth-google">
          <img src="/assets/images/google-logo.png" alt="Google Logo" className="oauth-logo me-2" />Google
        </button>
        <button type="submit" name="oauth_provider" value="microsoft" className="btn btn-light w-100 oauth-btn oauth-microsoft">
          <img src="/assets/images/microsoft-logo.png" alt="Microsoft Logo" className="oauth-logo me-2" />Microsoft
        </button>
      </form>
      <small className="text-muted d-block mt-4">Need help? Contact <a href="mailto:helpdesk@rcdoc.org">helpdesk@rcdoc.org</a></small>
    </Card>
  </div>
);

export default Login;