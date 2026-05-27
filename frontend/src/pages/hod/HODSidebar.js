import React from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../assets/css/AdminSidebar.css';
import { FaChartLine, FaList } from 'react-icons/fa';

function HODSidebar() {
  const { member_id } = useParams();
  return (
    <div className="admin-sidebar__container">
      <Link to={'/hod/' + member_id}>
        <div className="admin-sidebar-logo-left"></div>
      </Link>
      <ul className="admin-sidebar__menu">
        <li>
          <Link to={'/hod/' + member_id} className="admin-sidebar__menu-item">
            <FaChartLine /> HOD Dashboard
          </Link>
        </li>
        <li>
          <Link to={'/hod/' + member_id + '/students'} className="admin-sidebar__menu-item">
            <FaList /> Department Students
          </Link>
        </li>
        <li>
          <Link to="/logout" className="admin-sidebar__menu-item">Logout</Link>
        </li>
      </ul>
    </div>
  );
}

export default HODSidebar;
