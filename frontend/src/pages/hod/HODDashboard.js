import React from 'react';
import { Outlet } from 'react-router-dom';
import HODSidebar from './HODSidebar';
import '../../assets/css/AdminDashboard.css';

const HODDashboard = () => {
  return (
    <div className="admin-dashboard__container">
      <div className="ad-logo-right"></div>
      <div className="admin-dashboard__sidebar-container">
        <HODSidebar />
      </div>
      <div className="admin-dashboard__main-content-container">
        <Outlet />
      </div>
      <div className="admin-dashboard-powered-by">
        Powered by <a href="https://krintix.com" target="_blank" rel="noopener noreferrer" className="ad-footer-link">KRINTIX</a>
      </div>
    </div>
  );
};

export default HODDashboard;
