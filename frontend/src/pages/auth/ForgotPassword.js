import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../assets/css/ForgotPassword.css';
import { API_BASE_URL } from '../../api';
import PullToRefresh from 'react-simple-pull-to-refresh';
import { Link } from 'react-router-dom'; // Importing Link for navigation
// import Chatbot from '../Chatbot';

const ForgotPassword = () => {
    const [step, setStep] = useState(1); // Step 1: Request OTP, Step 2: Verify OTP, Step 3: Reset Password
    const [id, setId] = useState('');
    const [otp, setOtp] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleIdChange = (e) => {
        setId(e.target.value.toUpperCase());
      };
      

    const handleOtpChange = (e) => {
        setOtp(e.target.value);
    };

    const handlePasswordChange = (e) => {
        setNewPassword(e.target.value);
    };

    const handleConfirmPasswordChange = (e) => {
        setConfirmPassword(e.target.value);
    };

    const handleRequestOtp = async (e) => {
        e.preventDefault();
        if (!id) {
            setError('Please enter your ID');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/forgot-password?id=` + id, {
                method: 'POST',
            });

            const result = await response.json();

            if (response.status === 200) {
                setError('');
                setSuccess(result.message);
                setStep(2); // Move to Step 2: OTP Verification
            } else {
                setError(result.detail || 'Error sending OTP');
            }
        } catch (err) {
            setError('An error occurred while requesting OTP. Please try again.');
        }
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        if (!otp) {
            setError('Please enter the OTP');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/verify-otp?id=` + id + '&otp=' + otp, {
                method: 'POST',
            });

            const result = await response.json();

            if (response.status === 200) {
                setError('');
                setSuccess(result.message);
                setStep(3); // Move to Step 3: Password Reset
            } else {
                setError(result.detail || 'Invalid OTP');
            }
        } catch (err) {
            setError('An error occurred while verifying OTP. Please try again.');
        }
    };

    // Refresh Function
    const handleRefresh = async () => {
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate API call
        window.location.href = window.location.href; // Force full page refresh
        };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        if (!newPassword || !confirmPassword || newPassword !== confirmPassword) {
            setError('Please make sure passwords match and are not empty.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/reset-password?id=` + id + '&new_password=' + newPassword + '&confirm_password=' + confirmPassword + '&otp=' + otp, {
                method: 'POST',
            });

            const result = await response.json();

            if (response.status === 200) {
                setError('');
                setSuccess(result.message);
                navigate('/login'); // Redirect to login page after successful reset
            } else {
                setError(result.detail || 'Error resetting password');
            }
        } catch (err) {
            setError('An error occurred while resetting the password. Please try again.');
        }
    };

    return (
        <PullToRefresh onRefresh={handleRefresh}>
        <div className="forgot-password-container">
            <Link to="/"><div className="fp-logo-left"></div></Link>
            <div className="fp-logo-right"></div> {/* Right logo */}
            <div className="forgot-password-left">
                <h2>Change/Forgot Password</h2>

                {/* Step 1: Request OTP */}
                {step === 1 && (
                    <div>
                        <form onSubmit={handleRequestOtp}>
                            <div className="fp-form-group">
                                <label htmlFor="id">User ID</label>
                                <input
  type="text"
  id="id"
  name="id"
  value={id}
  onChange={handleIdChange}
  placeholder="Username"
  required
/>

                            </div>
                            {error && <p className="error-message">{error}</p>}
                            {success && <p className="success-message">{success}</p>}
                            <button className = 'fp-button' type="submit">Send OTP</button>
                        </form>
                    </div>
                )}

                {/* Step 2: Verify OTP */}
                {step === 2 && (
                    <div>
                        <form onSubmit={handleVerifyOtp}>
                            <div className="fp-form-group">
                                <label htmlFor="otp">OTP</label>
                                <input
                                    type="text"
                                    id="otp"
                                    name="otp"
                                    value={otp}
                                    onChange={handleOtpChange}
                                    placeholder="Enter the OTP sent to your email"
                                    required
                                />
                            </div>
                            {error && <p className="error-message">{error}</p>}
                            {success && <p className="success-message">{success}</p>}
                            <button className='fp-button' type="submit">Verify OTP</button>
                        </form>
                    </div>
                )}

                {/* Step 3: Reset Password */}
                {step === 3 && (
                    <div>
                        <form onSubmit={handleResetPassword}>
                            <div className="fp-form-group">
                                <label htmlFor="newPassword">New Password</label>
                                <input
                                    type="password"
                                    id="newPassword"
                                    name="newPassword"
                                    value={newPassword}
                                    onChange={handlePasswordChange}
                                    placeholder="New password"
                                    required
                                />
                            </div>
                            <div className="fp-form-group">
                                <label htmlFor="confirmPassword">Confirm Password</label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    value={confirmPassword}
                                    onChange={handleConfirmPasswordChange}
                                    placeholder="Confirm password"
                                    required
                                />
                            </div>
                            {error && <p className="error-message">{error}</p>}
                            {success && <p className="success-message">{success}</p>}
                            <button className='fp-button' type="submit">Reset Password</button>
                        </form>
                    </div>
                )}
            </div>

            <div className="forgot-password-right">
                <h3>Mentee Tracker</h3>
                <p>
                Welcome to the Mentee Tracker, your personalized platform for tracking and managing <br/>your mentees’ progress. Monitor their activities, schedule meetings, <br/>and ensure their continuous growth. Stay connected and <br/>make the most of your mentorship journey.
                </p>
            </div>

            {/* <Chatbot /> */}
        {/* "Powered by Krintix" Text with Class */}
        <div className="fp-powered-by">
            <p>Powered by <a href="https://krintix.com" target="_blank" rel="noopener noreferrer" className="fp-footer-link">KRINTIX</a></p>
            </div>
            </div>
            </PullToRefresh>

    );
};

export default ForgotPassword;
