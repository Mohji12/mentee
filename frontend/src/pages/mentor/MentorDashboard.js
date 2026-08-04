import React from 'react';
import { Outlet } from 'react-router-dom';
import MentorSidebar from './components/MentorSidebar';
import '../../assets/css/MentorDashboard.css';

const MentorDashboard = () => {
  return (
    <div className="mentor-dashboard__container">
      <div className="md-logo-right"></div> {/* Right logo */}
      <div className="mentor-dashboard__sidebar-container">
        <MentorSidebar />
      </div>
      <div className="mentor-dashboard__main-content-container">
        <Outlet /> {/* This renders nested routes dynamically */}<br/><br/><br/><br/><br/><br/>
      </div>
      <div className="mentor-dashboard-powered-by">
      Powered by <a href="https://biogred.com" target="_blank" rel="noopener noreferrer" className='mt-footer-link'>BIOGRED</a>
      </div>
    </div>
  );
};

export default MentorDashboard;
