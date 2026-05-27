import React from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../assets/css/AdminSidebar.css';
import { FaTachometerAlt, FaList, FaUserTie } from 'react-icons/fa';

const ProgramFacultySidebar = () => {
  const { member_id } = useParams();
  
  return (
    <div className="admin-sidebar__container">
      <Link to={`/program-faculty/${member_id}`}>
        <div className="admin-sidebar-logo-left"></div>
      </Link>
      <ul className="admin-sidebar__menu">
        <li>
          <Link to={`/program-faculty/${member_id}`} className="admin-sidebar__menu-item">
            <FaTachometerAlt />&nbsp;&nbsp;&nbsp;&nbsp;Dashboard
          </Link>
        </li>
        <li>
          <Link to={`/program-faculty/${member_id}/students`} className="admin-sidebar__menu-item">
            <FaList />&nbsp;&nbsp;&nbsp;&nbsp;Students
          </Link>
        </li>
        <li>
          <Link to={`/program-faculty/${member_id}/mentors`} className="admin-sidebar__menu-item">
            <FaUserTie />&nbsp;&nbsp;&nbsp;&nbsp;Mentors
          </Link>
        </li>
        <li>
          <Link to="/logout" className="admin-sidebar__menu-item">
            <FaTachometerAlt />&nbsp;&nbsp;&nbsp;&nbsp;Logout
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default ProgramFacultySidebar;
