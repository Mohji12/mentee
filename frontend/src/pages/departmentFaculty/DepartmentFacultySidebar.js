import React from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../assets/css/AdminSidebar.css';
import { FaChartLine, FaList, FaUserTie } from 'react-icons/fa';

function DepartmentFacultySidebar() {
  const { member_id } = useParams();
  return (
    <div className="admin-sidebar__container">
      <Link to={'/department-faculty/' + member_id}>
        <div className="admin-sidebar-logo-left"></div>
      </Link>
      <ul className="admin-sidebar__menu">
        <li>
          <Link to={'/department-faculty/' + member_id} className="admin-sidebar__menu-item">
            <FaChartLine /> Dashboard
          </Link>
        </li>
        <li>
          <Link to={'/department-faculty/' + member_id + '/students'} className="admin-sidebar__menu-item">
            <FaList /> Department Students
          </Link>
        </li>
        <li>
          <Link to={'/department-faculty/' + member_id + '/mentors'} className="admin-sidebar__menu-item">
            <FaUserTie /> Department Mentors
          </Link>
        </li>
        <li>
          <Link to="/logout" className="admin-sidebar__menu-item">Logout</Link>
        </li>
      </ul>
    </div>
  );
}

export default DepartmentFacultySidebar;
