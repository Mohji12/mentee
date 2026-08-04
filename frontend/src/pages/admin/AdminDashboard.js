import React from 'react';
import { Outlet } from 'react-router-dom';
import AdminSidebar from './components/AdminSidebar';
import '../../assets/css/AdminDashboard.css';

const AdminDashboard = () => {
  return (
    <div className="admin-dashboard__container">
      <div className="ad-logo-right"></div> {/* Right logo */}
      <div className="admin-dashboard__sidebar-container">
        <AdminSidebar />
      </div>
      <div className="admin-dashboard__main-content-container">
        <Outlet /> {/* This renders nested routes dynamically */}
      </div>
      <div className="admin-dashboard-powered-by">
      Powered by <a href="https://biogred.com" target="_blank" rel="noopener noreferrer" className='ad-footer-link'>BIOGRED</a>
      </div>
    </div>
  );
};

export default AdminDashboard;
