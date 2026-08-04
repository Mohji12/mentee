import React from 'react';
import { Outlet } from 'react-router-dom';
import WorkingCommitteeSidebar from './WorkingCommitteeSidebar';
import '../../assets/css/AdminDashboard.css';

const WorkingCommitteeDashboard = () => {
  return (
    <div className="admin-dashboard__container">
      <div className="ad-logo-right"></div>
      <div className="admin-dashboard__sidebar-container">
        <WorkingCommitteeSidebar />
      </div>
      <div className="admin-dashboard__main-content-container">
        <Outlet />
      </div>
      <div className="admin-dashboard-powered-by">
        Powered by <a href="https://biogred.com" target="_blank" rel="noopener noreferrer" className="ad-footer-link">BIOGRED</a>
      </div>
    </div>
  );
};

export default WorkingCommitteeDashboard;
