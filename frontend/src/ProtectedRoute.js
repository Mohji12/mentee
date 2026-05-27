import React from 'react';
import { Navigate, useParams } from 'react-router-dom';

const ProtectedRoute = ({ userId, requiredRole, element }) => {
  const params = useParams();
  const token = sessionStorage.getItem('access_token');
  const storedId = sessionStorage.getItem('userId');
  const storedRole = sessionStorage.getItem('role');
  const paramId = params[userId];

  // Check if token exists and is not expired
  const tokenExpiry = parseInt(sessionStorage.getItem('tokenExpiry'), 10);
  const currentTime = Date.now();
  const isTokenValid = token && tokenExpiry && currentTime < tokenExpiry;

  if (!isTokenValid || !storedId) {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('userId');
    sessionStorage.removeItem('role');
    sessionStorage.removeItem('tokenExpiry');
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && storedRole !== requiredRole) {
    return <Navigate to="/login" replace />;
  }

  if (paramId && storedId !== paramId) {
    return <Navigate to="/login" replace />;
  }

  return element;
};

export default ProtectedRoute;
