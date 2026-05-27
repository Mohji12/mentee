import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import PullToRefresh from 'react-simple-pull-to-refresh';
import '../../assets/css/Login.css';
import { API_BASE_URL } from '../../api';

const Login = () => {
  const [loginData, setLoginData] = useState({ id: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const checkTokenAndRedirect = useCallback(() => {
    const tokenExpiry = parseInt(sessionStorage.getItem('tokenExpiry'), 10);
    const currentTime = Date.now();

    if (tokenExpiry && currentTime < tokenExpiry) {
      const role = sessionStorage.getItem('role');
      const userId = sessionStorage.getItem('userId');
      if (role && userId) {
        const rolePaths = {
          mentor: `/mentor/${userId}/profile`,
          student: `/student/${userId}/profile`,
          admin: `/admin/${userId}/profile`,
          leader: `/leader/${userId}`,
          working_committee: `/working-committee/${userId}`,
          department_faculty: `/department-faculty/${userId}`,
          hod: `/hod/${userId}`,
          program_faculty: `/program-faculty/${userId}`,
        };
        if (rolePaths[role]) {
          navigate(rolePaths[role]);
        }
      }
    }
  }, [navigate]);

  useEffect(() => {
    checkTokenAndRedirect();
  }, [checkTokenAndRedirect]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const transformedValue = name === 'id' ? value.toUpperCase() : value;
    setLoginData((prev) => ({ ...prev, [name]: transformedValue }));
  };
  

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { data } = await axios.post(`${API_BASE_URL}/auth/login`, loginData);
      const { role, access_token, expires_in, id: apiUserId } = data;
      const userId = apiUserId != null ? apiUserId : loginData.id;

      const expirationTime = Date.now() + expires_in * 1000;
      sessionStorage.setItem('access_token', access_token);
      sessionStorage.setItem('role', role);
      sessionStorage.setItem('userId', userId);
      sessionStorage.setItem('tokenExpiry', expirationTime.toString());

      const rolePaths = {
        mentor: `/mentor/${userId}/profile`,
        student: `/student/${userId}/profile`,
        admin: `/admin/${userId}/profile`,
        leader: `/leader/${userId}`,
        working_committee: `/working-committee/${userId}`,
        department_faculty: `/department-faculty/${userId}`,
        hod: `/hod/${userId}`,
        program_faculty: `/program-faculty/${userId}`,
      };

      if (rolePaths[role]) {
        navigate(rolePaths[role]);
      } else {
        setError('Unknown role. Please contact support.');
        console.error('Unknown role:', role);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid ID or password. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    window.location.reload(); // Cleaner than setting href directly
  };

  return (
    <PullToRefresh onRefresh={handleRefresh}>
      <div className="login-container">
        <Link to="/" className="login-logo-left" aria-label="Home"></Link>
        <div className="login-logo-right"></div>

        <div className="login-left">
          <h2>Login</h2>
          <form onSubmit={handleSubmit} autoComplete="on">
            <div className="form-group">
            <input
  type="text"
  id="id"
  name="id"
  value={loginData.id}
  onChange={handleChange}
  placeholder="Username"
  maxLength={10}
  required
  autoFocus
/>

            </div>
            <div className="form-group">
              <input
                type="password"
                id="password"
                name="password"
                value={loginData.password}
                onChange={handleChange}
                placeholder="Password"
                required
              />
            </div>
            {error && <p className="error-message" role="alert">{error}</p>}
            <div className="button-group">
  <button
    type="submit"
    className="login-button"
    disabled={loading}
    style={{ width: '100px' }} // Fixed width to avoid shifting
  >
    {loading ? (
      <span className="spinner" />
    ) : (
      'Login'
    )}
  </button>
  <button
    type="button"
    className="signup-button"
    onClick={() => navigate('/student_signup')}
    style={{ width: '100px' }} // Match width for symmetry
  >
    Sign Up
  </button>
</div>
          </form>

          <div className="forgot-password-container">
            <Link to="/forgotpassword" className="forgot-password-link">
              Change/Forgot Password?
            </Link>
          </div>
        </div>

        <div className="login-right">
          <h3>Mentee Tracker</h3>
          <p>
            Welcome to the Mentee Tracker, your personalized platform for tracking and managing
            your mentees' progress. Monitor their activities, schedule meetings, and ensure their
            continuous growth. Stay connected and make the most of your mentorship journey.
          </p>
        </div>

        <div className="login-powered-by">
          <p>
            Powered by{' '}
            <a
              href="https://krintix.com"
              target="_blank"
              rel="noopener noreferrer"
              className="login-footer-link"
            >
              KRINTIX
            </a>
          </p>
        </div>
      </div>
    </PullToRefresh>
  );
};

export default Login;
