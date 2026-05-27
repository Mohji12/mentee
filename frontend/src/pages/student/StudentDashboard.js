import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './components/StudentSidebar';
import './../../assets/css/StudentDashboard.css'; // Import the updated CSS
// import Chatbot from '../Chatbot';

const StudentDashboard = () => {
  return (
    <div className="sd-dashboard-container">
      <Sidebar />
      <div className="sd-main-content">
        <Outlet /> {/* Renders the nested routes dynamically */}
      </div>
      {/* <Sidebar/> */}
      {/* <Chatbot /> */}
      <div className="sd-powered-by">
      Powered by <a href="https://krintix.com" target="_blank" rel="noopener noreferrer" className='sd-footer-link'>KRINTIX</a>
      </div>
    </div>
  );
};

export default StudentDashboard;
