import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../assets/css/StudentSignup.css';
import { API_BASE_URL } from '../../api';
import { Link } from 'react-router-dom';

const StudentSignup = () => {
  const [signupData, setSignupData] = useState({
    student_email: '',
    student_password: '',
    student_confirm_password: '',
    student_usn: '',
  });

  const [errors, setErrors] = useState({});
  const [studentId, setStudentId] = useState('');
  const [otp, setOtp] = useState('');
  const [isOtpSent, setIsOtpSent] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');
  const [isOtpButtonDisabled, setIsOtpButtonDisabled] = useState(false);
  const [isSignupButtonDisabled, setIsSignupButtonDisabled] = useState(false);
  const [isChecked, setIsChecked] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const navigate = useNavigate();

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown((prev) => prev - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const validatePassword = (password) => {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password)
      ? ''
      : 'Password must contain at least 1 uppercase, 1 lowercase, 1 number, and 1 special character.';
  };

  // Validation Functions
  const validateEmail = (email) => {
    const regex = /^[a-zA-Z0-9._-]+@jainuniversity\.ac\.in$/;
    return regex.test(email) ? '' : 'Please enter a valid email address ending with @jainuniversity.ac.in.';
  };

  const validateConfirmPassword = (password, confirmPassword) => {
    return password === confirmPassword ? '' : 'Passwords do not match.';
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSignupData({ ...signupData, [name]: value });

    let error = '';
    if (name === 'student_email') error = validateEmail(value);
    if (name === 'student_password') error = validatePassword(value);
    if (name === 'student_confirm_password') error = validateConfirmPassword(signupData.student_password, value);

    setErrors({ ...errors, [name]: error });
  };

  const handleStudentSignup = async () => {
    if (Object.values(errors).every((err) => err === '') && Object.values(signupData).every((field) => field !== '')) {
      setIsSignupButtonDisabled(true);
      try {
        const response = await fetch(`${API_BASE_URL}/auth/signup/student`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(signupData),
        });

        const data = await response.json();

        if (response.ok) {
          setResponseMessage('OTP sent to your email. Please verify.');
          setStudentId(signupData.student_usn);
          setIsOtpSent(true);
          setResendCooldown(30); // Cooldown for resend
        } else {
          setResponseMessage(`Error: ${data.detail || 'An error occurred during signup.'}`);
        }
      } catch (error) {
        console.error('Signup Error:', error);
        setResponseMessage('An unknown error occurred during signup.');
      }
      setIsSignupButtonDisabled(false);
    } else {
      setResponseMessage('Please fix validation errors before submitting.');
    }
  };

  const handleOtpValidation = async () => {
    setIsOtpButtonDisabled(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/student/${studentId}/otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ otp }),
      });

      const data = await response.json();

      if (response.ok) {
        setResponseMessage('Registration successful! Redirecting to login...');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setResponseMessage(`Error: ${data.detail || 'Invalid OTP'}`);
        setIsOtpButtonDisabled(false);
      }
    } catch (error) {
      console.error('OTP Validation Error:', error);
      setResponseMessage('An unknown error occurred during OTP validation.');
      setIsOtpButtonDisabled(false);
    }
  };

  const handleResendOtp = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup/student`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(signupData),
      });

      const data = await response.json();

      if (response.ok) {
        setResponseMessage('OTP resent to your email.');
        setResendCooldown(30); // Reset cooldown
      } else {
        setResponseMessage(`Error: ${data.detail || 'Failed to resend OTP.'}`);
      }
    } catch (error) {
      console.error('Resend OTP Error:', error);
      setResponseMessage('An error occurred while resending OTP.');
    }
  };

  return (
    <div className="student-signup-page">
      <Link to="/">
        <div className="ssg-logo-left"></div>
      </Link>
      <div className="ssg-logo-right"></div>

      <div className="student-signup-form-container">
        <h1>Signup</h1>

        {responseMessage && (
          <p
            className={`student-signup-response-message ${
              responseMessage.includes('Error') ? 'student-signup-error-message' : 'student-signup-success-message'
            }`}
          >
            {responseMessage}
          </p>
        )}

        {!isOtpSent ? (
          <>
            <input
              className="student-signup-input"
              type="text"
              name="student_usn"
              placeholder="Enter your USN (Student ID)"
              value={signupData.student_usn}
              maxLength={10}
              onChange={handleChange}
              required
            />
            {errors.student_usn && <p className="student-signup-input-error">{errors.student_usn}</p>}

            <input
              className="student-signup-input"
              type="email"
              name="student_email"
              placeholder="Enter your email"
              value={signupData.student_email}
              onChange={handleChange}
              required
            />
            {errors.student_email && <p className="student-signup-input-error">{errors.student_email}</p>}

            <input
              className="student-signup-input"
              type="password"
              name="student_password"
              placeholder="Enter password"
              value={signupData.student_password}
              onChange={handleChange}
              required
            />
            {errors.student_password && <p className="student-signup-input-error">{errors.student_password}</p>}

            <input
              className="student-signup-input"
              type="password"
              name="student_confirm_password"
              placeholder="Confirm password"
              value={signupData.student_confirm_password}
              onChange={handleChange}
              required
            />
            {errors.student_confirm_password && (
              <p className="student-signup-input-error">{errors.student_confirm_password}</p>
            )}

<div className="terms-container1">
  <input
    type="checkbox"
    id="termsCheckbox1"
    checked={isChecked}
    onChange={() => setIsChecked(!isChecked)}
    className="terms-checkbox"
    required
  />
  <label htmlFor="termsCheckbox1" className="terms-label">
    I have read and agree to the&nbsp;
    <a href="/terms-of-service" target="_blank" rel="noopener noreferrer" className="terms-link">
      Terms of Service
    </a>
    &nbsp;and&nbsp;
    <a href="/privacy-policy" target="_blank" rel="noopener noreferrer" className="terms-link">
      Privacy Policy
    </a>.
  </label>
</div>

            <button onClick={handleStudentSignup} disabled={!isChecked || isSignupButtonDisabled}>
              {isSignupButtonDisabled ? 'Signing Up...' : 'Sign Up'}
            </button>

            <p>
              Already have an account?{' '}
              <button onClick={() => navigate('/login')}>Login</button>
            </p>
          </>
        ) : (
          <>
            <h2 className="student-signup-header">Verify OTP</h2>
            <p>Student ID: {studentId}</p>
            <input
              className="student-signup-otp-input"
              type="text"
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <button
              className="student-signup-otp-button"
              onClick={handleOtpValidation}
              disabled={isOtpButtonDisabled}
            >
              {isOtpButtonDisabled ? 'Validating...' : 'Validate OTP'}
            </button>

            <button
              className="resend-otp-button"
              onClick={handleResendOtp}
              disabled={resendCooldown > 0}
            >
              {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP'}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default StudentSignup;