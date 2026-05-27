import React from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../assets/css/AdminSidebar.css';
import { FaUser, FaChartLine, FaList, FaChalkboardTeacher } from 'react-icons/fa';

const LeaderSidebar = () => {
  const { leader_id } = useParams();
  return (
    <div className="admin-sidebar__container">
      <Link to={`/leader/${leader_id}`}>
        <div className="admin-sidebar-logo-left"></div>
      </Link>
      <ul className="admin-sidebar__menu">
        <li>
          <Link to={`/leader/${leader_id}`} className="admin-sidebar__menu-item">
            <FaChartLine />&nbsp;&nbsp;&nbsp;&nbsp;Dashboard
          </Link>
        </li>
        <li>
          <Link to={`/leader/${leader_id}/students`} className="admin-sidebar__menu-item">
            <FaList />&nbsp;&nbsp;&nbsp;&nbsp;All Students
          </Link>
        </li>
        <li>
          <Link to={`/leader/${leader_id}/mentors`} className="admin-sidebar__menu-item">
            <FaChalkboardTeacher />&nbsp;&nbsp;&nbsp;&nbsp;Mentors
          </Link>
        </li>
        <li>
          <Link to="/logout" className="admin-sidebar__menu-item">
            <FaUser />&nbsp;&nbsp;&nbsp;&nbsp;Logout
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default LeaderSidebar;
