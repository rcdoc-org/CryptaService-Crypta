import React, { use, useState } from 'react';
import { enableMFA, verifyMFA, disableMFA } from '../api/auth';

const Account = () => {
    const [secret, setSecret ] = useState(null);
    const [otp, setOtp ] = useState('');
    const [message, setMessage ] = useState('');

    const startEnable = async () => {
        try {
            const { data } = await enableMFA();
            setSecret(data.secret);
        } catch (err) {
            setMessage('Unable to start MFA');
        }
    };

    const handleVerify = async () => {
        try { 
            await verifyMFA({ otp });
            setMessage('MFA enabled');
            setSecret(null);
            setOtp('');
        } catch (err) {
            setMessage('Invalid code');
        }
    };

    const handleDisable = async () => {
        await disableMFA ();
        setMessage('MFA disabled');
        setSecret(null);
    };

    return (
    <div className="container mt-4">
      <h2>Multi-Factor Authentication</h2>
      {secret ? (
        <div>
          <p>Scan the code or enter the secret in your authenticator app.</p>
          <p><strong>{secret}</strong></p>
          <input
            type="text"
            className="form-control mb-2"
            placeholder="Enter verification code"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
          />
          <button className="btn btn-primary me-2" onClick={handleVerify}>Verify</button>
        </div>
      ) : (
        <button className="btn btn-primary me-2" onClick={startEnable}>Enable MFA</button>
      )}
      <button className="btn btn-secondary" onClick={handleDisable}>Disable MFA</button>
      {message && <p className="mt-3">{message}</p>}
    </div>
  );
};

export default Account;