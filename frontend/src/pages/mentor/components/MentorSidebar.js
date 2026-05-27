import React, { useState, useEffect, useRef } from 'react';
import { Link, useParams } from 'react-router-dom';
import '../../../assets/css/MentorSidebar.css';
import { FaUser, FaClipboardList, FaChartLine, FaRegClock, FaTasks, FaChevronDown, FaChevronUp, FaComments, FaTachometerAlt, FaGraduationCap } from 'react-icons/fa';

const MentorSidebar = () => {
  const { mentor_id } = useParams(); // Fetch the mentor_id from the URL
  const [activitiesDropdown, setActivitiesDropdown] = useState(false);
  const [reportsDropdown, setReportsDropdown] = useState(false); // State for Reports dropdown
  const sidebarRef = useRef(); // Reference for sidebar container

  const toggleActivitiesDropdown = () => {
    setActivitiesDropdown(!activitiesDropdown);
  };

  const toggleReportsDropdown = () => {
    setReportsDropdown(!reportsDropdown);
  };

  // Close dropdown if clicked outside or on another menu item
  const closeDropdown = () => {
    setActivitiesDropdown(false);
    setReportsDropdown(false); // Close both dropdowns when clicking outside
  };

  // Close dropdown if clicked outside the sidebar
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        setActivitiesDropdown(false); // Close the activities dropdown if clicked outside
        setReportsDropdown(false); // Close the reports dropdown if clicked outside
      }
    };

    // Add event listener for clicks
    document.addEventListener('mousedown', handleClickOutside);

    // Cleanup the event listener on component unmount
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="mentor-sidebar__container" ref={sidebarRef}>
      <Link to={`/mentor/${mentor_id}/profile`}>
        <div className="mentor-sidebar-logo-left"></div>
      </Link>
      <ul className="mentor-sidebar__menu">
        {/* Profile */}
        <li>
          <Link to={`/mentor/${mentor_id}/profile`} className="mentor-sidebar__menu-item">
            <FaUser />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Profile</span>
          </Link>
        </li>

        {/* Dashboard */}
        <li>
          <Link to={`/mentor/${mentor_id}`} className="mentor-sidebar__menu-item">
            <FaTachometerAlt />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Dashboard</span>
          </Link>
        </li>

        {/* Assigned Students */}
        <li>
          <Link to={`/mentor/${mentor_id}/assigned_students`} className="mentor-sidebar__menu-item">
            <FaClipboardList />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Assigned Students</span>
          </Link>
        </li>

        {/* Consolidated internal marks (mentor-only view) */}
        <li>
          <Link to={`/mentor/${mentor_id}/consolidated-internal-marks`} className="mentor-sidebar__menu-item">
            <FaGraduationCap />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Internal Marks</span>
          </Link>
        </li>

        {/* Activities Dropdown */}
        <li className="ss-dropdown-container">
          <div className="ss-sidebar-menu-item" onClick={toggleActivitiesDropdown}>
            <FaTasks />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Activities</span>
            <span className="d-desktop-inline">{activitiesDropdown ? <FaChevronUp /> : <FaChevronDown />}</span>
          </div>
          {activitiesDropdown && (
            <ul className="ss-dropdown-menu">
              <li>
                <Link to={`/mentor/${mentor_id}/activity_tracking`} className="ss-dropdown-menu-item" onClick={closeDropdown}>
                  Activity Tracking
                </Link>
              </li>
              <li>
                <Link to={`/mentor/${mentor_id}/approvals`} className="ss-dropdown-menu-item" onClick={closeDropdown}>
                  Submissions
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* Meetings Dropdown */}
        <li className="ss-dropdown-container">
          <div className="ss-sidebar-menu-item" onClick={toggleReportsDropdown}>
            <FaChartLine />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Meetings</span>
            <span className="d-desktop-inline">{reportsDropdown ? <FaChevronUp /> : <FaChevronDown />}</span>
          </div>
          {reportsDropdown && (
            <ul className="ss-dropdown-menu">
              <li>
                <Link to={`/mentor/${mentor_id}/meetings`} className="ss-dropdown-menu-item" onClick={closeDropdown}>
                  Schedule Meetings
                </Link>
              </li>
              <li>
                <Link to={`/mentor/${mentor_id}/appointments`} className="ss-dropdown-menu-item" onClick={closeDropdown}>
                  Appointment Approvals
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* Student Support */}
        <li>
          <Link to={`/mentor/${mentor_id}/counseling`} className="mentor-sidebar__menu-item">
            <FaComments />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Student Support</span>
          </Link>
        </li>

        {/* Attendance */}
        <li>
          <Link to={`/mentor/${mentor_id}/attendance`} className="mentor-sidebar__menu-item">
            <FaRegClock />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Attendance</span>
          </Link>
        </li>
      </ul>
    </div>
  );
};

export default MentorSidebar;
