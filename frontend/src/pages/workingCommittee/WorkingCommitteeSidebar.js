import React from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../assets/css/AdminSidebar.css';
import { FaChartLine, FaList, FaUniversity, FaTachometerAlt, FaUserTie } from 'react-icons/fa';

const WorkingCommitteeSidebar = () => {
  const { member_id } = useParams();
  
  return (
    <div className="admin-sidebar__container">
      <Link to={`/working-committee/${member_id}`}>
        <div className="admin-sidebar-logo-left"></div>
      </Link>
      <ul className="admin-sidebar__menu">
        <li>
          <Link to={`/working-committee/${member_id}`} className="admin-sidebar__menu-item">
            <FaTachometerAlt />&nbsp;&nbsp;&nbsp;&nbsp;Dashboard
          </Link>
        </li>
        <li>
          <Link to={`/working-committee/${member_id}/departments`} className="admin-sidebar__menu-item">
            <FaUniversity />&nbsp;&nbsp;&nbsp;&nbsp;My Departments
          </Link>
        </li>
        <li>
          <Link to={`/working-committee/${member_id}/students`} className="admin-sidebar__menu-item">
            <FaList />&nbsp;&nbsp;&nbsp;&nbsp;Students
          </Link>
        </li>
        <li>
          <Link to={`/working-committee/${member_id}/mentors`} className="admin-sidebar__menu-item">
            <FaUserTie />&nbsp;&nbsp;&nbsp;&nbsp;Mentors
          </Link>
        </li>
        <li>
          <Link to="/logout" className="admin-sidebar__menu-item">
            <FaChartLine />&nbsp;&nbsp;&nbsp;&nbsp;Logout
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default WorkingCommitteeSidebar;
