import React from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../../assets/css/AdminSidebar.css';
import { FaUser, FaClipboardList, FaChartLine, FaComments } from 'react-icons/fa';

const AdminSidebar = () => {
  const { admin_id } = useParams(); // Fetch the admin_id from the URL
  return (
    <div className="admin-sidebar__container">
      <Link to={`/admin/${admin_id}/profile`}>
        <div className="admin-sidebar-logo-left"></div>
      </Link>
      <ul className="admin-sidebar__menu">
        {/* Assigned Students */}
        <li>
          <Link to={`/admin/${admin_id}/activities`} className="admin-sidebar__menu-item">
            <FaClipboardList />&nbsp;&nbsp;&nbsp;&nbsp;Activities
          </Link>
        </li>

        {/* Activity Tracking */}
        <li>
          <Link to={`/admin/${admin_id}/allstudents`} className="admin-sidebar__menu-item">
            <FaChartLine />&nbsp;&nbsp;&nbsp;&nbsp;Students
          </Link>
        </li>

        {/* Counseling Oversight */}
        <li>
          <Link to={`/admin/${admin_id}/counseling`} className="admin-sidebar__menu-item">
            <FaComments />&nbsp;&nbsp;&nbsp;&nbsp;Student Support
          </Link>
        </li>

        {/* Profile */}
        <li>
          <Link to={`/admin/${admin_id}/profile`} className="admin-sidebar__menu-item">
            <FaUser />&nbsp;&nbsp;&nbsp;&nbsp;Profile
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default AdminSidebar;
