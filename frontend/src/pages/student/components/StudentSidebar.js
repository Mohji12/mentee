import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { Link, useParams } from 'react-router-dom';
import '../../../assets/css/StudentSidebar.css';
import '../../../assets/css/Loader.css';
import { FaUser, FaClipboardList, FaChartLine, FaTasks, FaRegClock, FaChevronDown, FaChevronUp, FaComments, FaGraduationCap, FaDownload } from 'react-icons/fa';
import { API_BASE_URL } from '../../../api';
import { triggerPdfDownload } from '../../../utils/triggerPdfDownload';

const StudentSidebar = () => {
  const { student_usn } = useParams();
  const [academicsDropdown, setAcademicsDropdown] = useState(false);
  const [activitiesDropdown, setActivitiesDropdown] = useState(false);
  const [meetingsDropdown, setMeetingsDropdown] = useState(false);
  const [formsDropdown, setFormsDropdown] = useState(false);
  const [mcaDownloadBusy, setMcaDownloadBusy] = useState(false);
  const sidebarRef = useRef();

  const closeDropdowns = useCallback(() => {
    setAcademicsDropdown(false);
    setActivitiesDropdown(false);
    setMeetingsDropdown(false);
    setFormsDropdown(false);
  }, []);

  const handleMcaDownload = useCallback(async (e) => {
    e?.preventDefault?.();
    e?.stopPropagation?.();
    closeDropdowns();
    // Prefer session userId (matches auth) in case route params are ever missing
    const usn = sessionStorage.getItem('userId') || student_usn;
    if (!usn) {
      window.alert('Session expired. Please log in again.');
      return;
    }
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      window.alert('Please log in again to download your report.');
      return;
    }

    setMcaDownloadBusy(true);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000);
    try {
      const response = await fetch(`${API_BASE_URL}/student/${usn}/reportdownload`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal,
      });

      if (!response.ok) {
        let errorMessage = 'Failed to download MCA report.';
        try {
          const ct = response.headers.get('content-type');
          if (ct && ct.includes('application/json')) {
            const data = await response.json();
            errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail || data);
          } else {
            const text = await response.text();
            errorMessage = text || errorMessage;
          }
        } catch (_) {
          errorMessage = `Server error: ${response.status}`;
        }
        window.alert(errorMessage);
        return;
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/pdf')) {
        window.alert('The server did not return a PDF. Complete the MCA flow and try again.');
        return;
      }

      const blob = await response.blob();
      if (!blob || blob.size === 0) {
        window.alert('Received an empty file. Please try again later.');
        return;
      }

      triggerPdfDownload(blob, `student_profile_${usn}.pdf`);
    } catch (err) {
      if (err.name === 'AbortError') {
        window.alert('Download timed out. Wait a moment and try again, or open MCA Form and download from there.');
      } else {
        window.alert(err.message || 'Could not download the MCA report.');
      }
    } finally {
      clearTimeout(timeoutId);
      setMcaDownloadBusy(false);
    }
  }, [student_usn, closeDropdowns]);

  const toggleAcademicsDropdown = () => {
    setAcademicsDropdown(!academicsDropdown);
    setActivitiesDropdown(false);
    setMeetingsDropdown(false);
    setFormsDropdown(false);
  };

  const toggleActivitiesDropdown = () => {
    setActivitiesDropdown(!activitiesDropdown);
    setAcademicsDropdown(false);
    setMeetingsDropdown(false);
    setFormsDropdown(false);
  };

  const toggleMeetingsDropdown = () => {
    setMeetingsDropdown(!meetingsDropdown);
    setAcademicsDropdown(false);
    setActivitiesDropdown(false);
    setFormsDropdown(false);
  };

  const toggleFormsDropdown = () => {
    setFormsDropdown(!formsDropdown);
    setAcademicsDropdown(false);
    setActivitiesDropdown(false);
    setMeetingsDropdown(false);
  };

  // Close dropdown if clicked outside the sidebar
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        closeDropdowns(); // Close all dropdowns
      }
    };

    // Add event listener for clicks
    document.addEventListener('mousedown', handleClickOutside);

    // Cleanup the event listener on component unmount
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [closeDropdowns]);

  const mcaDownloadLoader =
    mcaDownloadBusy &&
    createPortal(
      <div className="loader-overlay" role="status" aria-live="polite" aria-busy="true">
        <div className="ss-mca-download-loader-inner">
          <div className="loader" />
          <p className="ss-mca-download-loader-text">Preparing your MCA report…</p>
        </div>
      </div>,
      document.body
    );

  return (
    <>
      {mcaDownloadLoader}
      <div ref={sidebarRef} className="ss-sidebar-container">
      <Link to={`/student/${student_usn}/profile`}>
        <div className="ss-logo-left ss-logo-mobile-left"></div>
      </Link>
      <ul className="ss-sidebar-menu">
        {/* Dashboard */}
        <li>
          <Link to={`/student/${student_usn}/dashboard`} className="ss-sidebar-menu-item" onClick={closeDropdowns}>
            <FaChartLine />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Dashboard</span>
          </Link>
        </li>

        {/* Profile */}
        <li>
          <Link to={`/student/${student_usn}/profile`} className="ss-sidebar-menu-item" onClick={closeDropdowns}>
            <FaUser />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Profile</span>
          </Link>
        </li>

        {/* Academics Dropdown */}
        <li className="ss-dropdown-container">
          <div className="ss-sidebar-menu-item" onClick={toggleAcademicsDropdown}>
            <FaGraduationCap />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Academics</span>
            <span className="d-desktop-inline">{academicsDropdown ? <FaChevronUp /> : <FaChevronDown />}</span>
          </div>
          {academicsDropdown && (
            <ul className="ss-dropdown-menu">
              <li>
                <Link to={`/student/${student_usn}/academic-performance`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Academic Performance
                </Link>
              </li>
              <li>
                <Link to={`/student/${student_usn}/experiential-learning`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Experiential Learning
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* Attendance */}
        <li>
          <Link to={`/student/${student_usn}/attendance`} className="ss-sidebar-menu-item" onClick={closeDropdowns}>
            <FaRegClock />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Attendance</span>
          </Link>
        </li>

        {/* Meetings Dropdown */}
        <li className="ss-dropdown-container">
          <div className="ss-sidebar-menu-item" onClick={toggleMeetingsDropdown}>
            <FaRegClock />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Meetings</span>
            <span className="d-desktop-inline">{meetingsDropdown ? <FaChevronUp /> : <FaChevronDown />}</span>
          </div>
          {meetingsDropdown && (
            <ul className="ss-dropdown-menu">
              <li>
                <Link to={`/student/${student_usn}/scheduled_meetings`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Scheduled Meetings
                </Link>
              </li>
              <li>
                <Link to={`/student/${student_usn}/appointments`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Meeting Requests
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* Student Support */}
        <li>
          <Link to={`/student/${student_usn}/counseling`} className="ss-sidebar-menu-item" onClick={closeDropdowns}>
            <FaComments />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Student Support</span>
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
                <Link to={`/student/${student_usn}/activities`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Assigned Activities
                </Link>
              </li>
              <li>
                <Link to={`/student/${student_usn}/logged_activities`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Logged Activities
                </Link>
              </li>
              <li>
                <Link to={`/student/${student_usn}/submissions`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Activities Submission
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* Forms Dropdown */}
        <li className="ss-dropdown-container">
          <div className="ss-sidebar-menu-item" onClick={toggleFormsDropdown}>
            <FaClipboardList />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Forms</span>
            <span className="d-desktop-inline">{formsDropdown ? <FaChevronUp /> : <FaChevronDown />}</span>
          </div>
          {formsDropdown && (
            <ul className="ss-dropdown-menu">
              <li>
                <Link to={`/student/${student_usn}/psychometric`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  Psychometric Form
                </Link>
              </li>
              <li>
                <Link to={`/student/${student_usn}/mca_form`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  MCA Form
                </Link>
              </li>
              <li>
                <Link to={`/student/${student_usn}/pf16-form`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  16PF Form
                </Link>
              </li>
              <li>
                <Link to={`/student/${student_usn}/ibp-form`} className="ss-dropdown-menu-item" onClick={closeDropdowns}>
                  IBP Form
                </Link>
              </li>
            </ul>
          )}
        </li>

        {/* MCA report PDF download */}
        <li>
          <button
            type="button"
            className="ss-sidebar-menu-item ss-sidebar-menu-button"
            onClick={handleMcaDownload}
            disabled={mcaDownloadBusy}
            aria-busy={mcaDownloadBusy}
            style={{ touchAction: 'manipulation' }}
          >
            <FaDownload />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;MCA Download</span>
          </button>
        </li>

        {/* Report */}
        <li>
          <Link to={`/student/${student_usn}/report`} className="ss-sidebar-menu-item" onClick={closeDropdowns}>
            <FaChartLine />
            <span className="d-desktop-inline">&nbsp;&nbsp;&nbsp;&nbsp;Report</span>
          </Link>
        </li>
      </ul>
    </div>
    </>
  );
};

export default StudentSidebar;