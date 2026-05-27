import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import '../../../assets/css/AssignedStudents.css';
import '../../../assets/css/AcademicPerformance.css';
import { API_BASE_URL } from "../../../api";
import { triggerPdfDownload } from '../../../utils/triggerPdfDownload';
import * as XLSX from 'xlsx';
import Modal from 'react-modal';
import { FaFilePdf, FaEye, FaDownload } from 'react-icons/fa';

Modal.setAppElement('#root');

const AssignedStudents = () => {
  const { mentor_id } = useParams();
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [programFilter, setProgramFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [programs, setPrograms] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [searchUSN, setSearchUSN] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [downloadStatus] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalStudentUSN, setModalStudentUSN] = useState(null);
  const [modalDownloading, setModalDownloading] = useState(false);
  const [modalStatus, setModalStatus] = useState('');
  const [acadPerfModalOpen, setAcadPerfModalOpen] = useState(false);
  const [acadPerfStudentUsn, setAcadPerfStudentUsn] = useState(null);
  const [acadPerfStudentName, setAcadPerfStudentName] = useState('');
  const [acadPerfData, setAcadPerfData] = useState(null);
  const [acadPerfLoading, setAcadPerfLoading] = useState(false);
  const [acadPerfError, setAcadPerfError] = useState('');

  const SEM_LABELS = ['I Sem', 'II Sem', 'III Sem', 'IV Sem'];

  const openAcademicPerformanceModal = (student_usn) => {
    const student = students.find(s => s.student_usn === student_usn);
    setAcadPerfStudentUsn(student_usn);
    setAcadPerfStudentName(student?.student_name || '');
    setAcadPerfModalOpen(true);
    setAcadPerfData(null);
    setAcadPerfError('');
    setAcadPerfLoading(true);
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/mentor/${mentor_id}/students/${student_usn}/academic-performance`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) {
          if (res.status === 403) throw new Error('You do not have access to this student.');
          if (res.status === 404) throw new Error('Student not found.');
          throw new Error('Failed to load academic performance.');
        }
        return res.json();
      })
      .then((data) => {
        setAcadPerfData(data);
      })
      .catch((err) => {
        setAcadPerfError(err.message || 'Failed to load.');
      })
      .finally(() => {
        setAcadPerfLoading(false);
      });
  };

  const closeAcademicPerformanceModal = () => {
    setAcadPerfModalOpen(false);
    setAcadPerfStudentUsn(null);
    setAcadPerfStudentName('');
    setAcadPerfData(null);
    setAcadPerfError('');
  };

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/assigned_students`);
        if (!response.ok) {
          throw new Error('No students have been assigned yet.');
        }
        const data = await response.json();
        setStudents(data);
        setFilteredStudents(data);
        const uniquePrograms = Array.from(new Set(data.map(student => student.program)));
        setPrograms(uniquePrograms);
        let uniqueStatuses = Array.from(new Set(data.map(student => student.status)));
        if (!uniqueStatuses.includes('Complete Flow till MCA FORM Filled')) {
          uniqueStatuses.push('Complete Flow till MCA FORM Filled');
        }
        setStatuses(uniqueStatuses);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStudents();
  }, [mentor_id]);

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/student_stats`);
      if (!response.ok) {
        throw new Error('Error fetching statistics');
      }
      const data = await response.json();
      setStats(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoadingStats(false);
    }
  };

  const applyFilters = (program, usn, status) => {
    let filtered = students;
    if (program) {
      filtered = filtered.filter(student => student.program === program);
    }
    if (usn) {
      filtered = filtered.filter(student => student.student_usn.includes(usn));
    }
    if (status) {
      filtered = filtered.filter(student => student.status === status);
    }
    setFilteredStudents(filtered);
  };

  const handleProgramFilterChange = (e) => {
    const selectedProgram = e.target.value;
    setProgramFilter(selectedProgram);
    applyFilters(selectedProgram, searchUSN, statusFilter);
  };

  const handleStatusFilterChange = (e) => {
    const selectedStatus = e.target.value;
    setStatusFilter(selectedStatus);
    applyFilters(programFilter, searchUSN, selectedStatus);
  };

  const handleSearchChange = (e) => {
    const searchValue = e.target.value;
    setSearchUSN(searchValue);
    applyFilters(programFilter, searchValue, statusFilter);
  };

  const downloadExcel = () => {
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(filteredStudents);
    XLSX.utils.book_append_sheet(wb, ws, 'Students');
    XLSX.writeFile(wb, 'students.xlsx');
  };

  const handleDownloadMCA = (student_usn) => {
    setModalStudentUSN(student_usn);
    setModalOpen(true);
    setModalStatus('');
    setModalDownloading(true);
    // Start download when modal opens
    fetch(`${API_BASE_URL}/student/${student_usn}/reportdownload`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${sessionStorage.getItem('access_token')}`
      }
    })
      .then(async (response) => {
        // Check if response is OK
        if (!response.ok) {
          // Try to get error message
          let errorMessage = 'Failed to download report.';
          try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
              const data = await response.json();
              errorMessage = typeof data.detail === 'string' ? data.detail : 
                            (data.detail && typeof data.detail === 'object' ? JSON.stringify(data.detail) : 
                            `Server error: ${response.status} ${response.statusText}`);
            } else {
              const text = await response.text();
              errorMessage = text || `Server error: ${response.status} ${response.statusText}`;
            }
          } catch (e) {
            errorMessage = `Server error: ${response.status} ${response.statusText}`;
          }
          setModalStatus(errorMessage);
          setModalDownloading(false);
          return;
        }

        // Check if response is actually a PDF
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/pdf')) {
          setModalStatus('Error: Server did not return a PDF file.');
          setModalDownloading(false);
          return;
        }

        // Create blob from response
        const blob = await response.blob();
        console.log('Blob created, size:', blob.size, 'type:', blob.type);
        
        // Check if blob is valid
        if (!blob || blob.size === 0) {
          setModalStatus('Error: Received empty file.');
          setModalDownloading(false);
          return;
        }

        try {
          triggerPdfDownload(blob, `student_profile_${student_usn}.pdf`);
          setModalStatus('Report downloaded successfully! Check your downloads folder.');
        } catch (downloadError) {
          console.error('Download error:', downloadError);
          try {
            const objectUrl = URL.createObjectURL(blob);
            window.open(objectUrl, '_blank');
            setModalStatus('Report opened in a new tab. Use Ctrl+S to save the PDF.');
            setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
          } catch (fallbackError) {
            console.error('Fallback error:', fallbackError);
            setModalStatus('Error: Could not download file. Please try again.');
          }
        }
      })
      .catch((error) => {
        console.error('Error downloading report:', error);
        setModalStatus(`Failed to download report: ${error.message || 'Unknown error'}`);
      })
      .finally(() => {
        setModalDownloading(false);
      });
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setModalStudentUSN(null);
    setModalStatus('');
    setModalDownloading(false);
  };

  if (isLoading) return <div>Loading assigned students...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="assigned-students__container">
      <div style={{ marginBottom: '1rem' }}>
        <h2 className="assigned-students__title">Assigned Students</h2>
      </div>
      <div className="assigned-students__filter">
        {/* ... (filter and search inputs) */}
        <label htmlFor="programFilter">Filter by Program:</label>
        <select id="programFilter" value={programFilter} onChange={handleProgramFilterChange}>
          <option value="">All Programs</option>
          {programs.map((program, index) => (
            <option key={index} value={program}>{program}</option>
          ))}
        </select>

        <label htmlFor="statusFilter">Filter by Status:</label>
        <select id="statusFilter" value={statusFilter} onChange={handleStatusFilterChange}>
          <option value="">All Statuses</option>
          {statuses.map((status, index) => (
            <option key={index} value={status}>{status}</option>
          ))}
        </select>

        <label htmlFor="searchUSN">Search by USN:</label>
        <input
          type="text"
          id="searchUSN"
          value={searchUSN}
          onChange={handleSearchChange}
          placeholder="Enter USN"
        />

      </div>
      <div className="button-group"> {/* Container for buttons */}
        <button className="stats-btn" onClick={fetchStats} disabled={loadingStats}>
          {loadingStats ? 'Showing... Please wait' : 'Show Stats'}
        </button>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <button className="download-btn" onClick={downloadExcel}>Download Excel</button> {/* Download Button */}
      </div>
       {/* ... (student count and stats display) */}
       <div className="student-count">
        <strong>
          Total number of students in
          <span className="highlight-text"> {programFilter ? programFilter : "All Programs"} </span>
          at
          <span className="highlight-text"> {statusFilter ? statusFilter : "All Statuses"} </span>:
          &nbsp;{filteredStudents.length}
        </strong>
      </div>

      {stats && (
        <div className="mentor-stats">
          <h3>Statistics</h3>
          <div className="mstats-circles">
            {/* ... (stats circles) */}
            <div className="mstat-circle">
              <div className="mcircle">{stats.total_students}</div>
              <p>Total Students</p>
            </div>
            <div className="mstat-circle">
              <div className="mcircle">{stats.psychometric_form_filled}</div>
              <p>Psychometric Forms Filled</p>
            </div>
            <div className="mstat-circle">
              <div className="mcircle">{stats.mca_filled}</div>
              <p>MCA Forms Filled</p>
            </div>
            <div className="mstat-circle">
              <div className="mcircle">{stats.pf16_filled || 0}</div>
              <p>16PF Forms Filled</p>
            </div>
            <div className="mstat-circle">
              <div className="mcircle">{stats.ibp_filled || 0}</div>
              <p>IBP Forms Filled</p>
            </div>
            <div className="mstat-circle">
              <div className="mcircle">{stats.report_generated}</div>
              <p>Reports Generated</p>
            </div>
            <div className="mstat-circle">
              <div className="mcircle">{stats.activities_generated}</div>
              <p>Activities Generated</p>
            </div>
          </div>
        </div>
      )}

      <div className="assigned-students__table-container">
        <table className="assigned-students__table assigned-students__table--colorful">
          <thead>
            <tr>
              <th className="th-usn">USN</th>
              <th className="th-name">Name</th>
              <th className="th-phone">Phone</th>
              <th className="th-email">Email</th>
              <th className="th-program">Program</th>
              <th className="th-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.map((student, index) => (
              <tr key={student.student_usn} className={index % 2 === 0 ? 'row-even' : 'row-odd'}>
                <td className="td-usn">
                  <Link to={`/mentor/${mentor_id}/student/${student.student_usn}`} className="student-link">
                    {student.student_usn}
                  </Link>
                </td>
                <td className="td-name">
                  {student.student_name ? (
                    <Link to={`/mentor/${mentor_id}/student/${student.student_usn}`} className="student-link">
                      {student.student_name}
                    </Link>
                  ) : '—'}
                </td>
                <td className="td-phone">{student.phone || '—'}</td>
                <td className="td-email">{student.email || '—'}</td>
                <td className="td-program">
                  <span className="program-badge">{student.program || '—'}</span>
                </td>
                <td className="td-actions">
                  <button
                    className="download-btn mca-download"
                    onClick={() => handleDownloadMCA(student.student_usn)}
                    title="Download MCA Report"
                  >
                    <FaFilePdf /> MCA
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {downloadStatus && <div className="download-status-message">{downloadStatus}</div>}
      </div>
      <Modal
        isOpen={modalOpen}
        onRequestClose={handleCloseModal}
        contentLabel="Download MCA Report"
        className="mca-modal"
        overlayClassName="mca-modal-overlay"
      >
        <h2>Download MCA Report</h2>
        <p>Downloading MCA report for student: <strong>{modalStudentUSN}</strong></p>
        {modalDownloading ? (
          <div className="loader"></div>
        ) : (
          <button onClick={handleCloseModal} className="mca-modal-button">Close</button>
        )}
        {modalStatus && <p className="mca-modal-status">{modalStatus}</p>}
      </Modal>

      <Modal
        isOpen={acadPerfModalOpen}
        onRequestClose={closeAcademicPerformanceModal}
        contentLabel="Academic Performance"
        className="ap-modal-mentor"
        overlayClassName="ap-modal-overlay-mentor"
      >
        <div className="ap-modal-header">
          <h2 className="ap-modal-title">📊 Academic Performance</h2>
          <button 
            onClick={closeAcademicPerformanceModal} 
            className="ap-modal-close-x"
            aria-label="Close"
          >
            ×
          </button>
        </div>
        
        <div className="ap-modal-student-info">
          {acadPerfStudentName && (
            <div className="ap-student-name">{acadPerfStudentName}</div>
          )}
          <div className="ap-student-usn">USN: {acadPerfStudentUsn}</div>
        </div>

        {acadPerfLoading && (
          <div className="ap-loading-container">
            <div className="loader"></div>
            <p>Loading academic performance...</p>
          </div>
        )}
        
        {acadPerfError && (
          <div className="ap-error-container">
            <p className="ap-error">{acadPerfError}</p>
          </div>
        )}
        
        {!acadPerfLoading && !acadPerfError && acadPerfData && (
          <div className="ap-modal-content">
            {/* Secondary marksheets (10th & 12th) */}
            {acadPerfData.secondary_marksheets && Object.keys(acadPerfData.secondary_marksheets).length > 0 && (
              <div className="ap-secondary-mentor">
                <h4 className="ap-marksheet-title">10th & 12th Standard Marksheets</h4>
                <div className="ap-secondary-mentor-list">
                  {[10, 12].map((std) => {
                    const info = acadPerfData.secondary_marksheets[std] || acadPerfData.secondary_marksheets[String(std)];
                    if (!info) return null;
                    return (
                      <div key={std} className="ap-secondary-mentor-item">
                        <span>{std}th Standard</span>
                        {info.uploaded_at && (
                          <span className="ap-marksheet-date">({new Date(info.uploaded_at).toLocaleDateString()})</span>
                        )}
                        <button
                          type="button"
                          className="ap-view-marksheet-btn"
                          onClick={() => {
                            if (info.marksheet_view_url) {
                              window.open(info.marksheet_view_url, '_blank');
                            } else {
                              const token = sessionStorage.getItem('access_token');
                              fetch(`${API_BASE_URL}/mentor/${mentor_id}/students/${acadPerfStudentUsn}/academic-performance/secondary-marksheet/${std}`, {
                                headers: { Authorization: `Bearer ${token}` },
                              })
                                .then(res => res.json())
                                .then(data => {
                                  if (data.marksheet_view_url) window.open(data.marksheet_view_url, '_blank');
                                  else alert('Failed to load marksheet.');
                                })
                                .catch(() => alert('Failed to load marksheet.'));
                            }
                          }}
                        >
                          <FaEye /> View
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            {(!acadPerfData.semesters || acadPerfData.semesters.length === 0 || 
              acadPerfData.semesters.every(s => !s.rows || s.rows.length === 0)) && (!acadPerfData.secondary_marksheets || Object.keys(acadPerfData.secondary_marksheets).length === 0) ? (
              <div className="ap-empty-state">
                <div className="ap-empty-icon">📝</div>
                <p className="ap-empty-text">No academic performance submitted yet.</p>
                <p className="ap-empty-subtext">The student hasn't added any grades yet.</p>
              </div>
            ) : (
              <>
              <div className="ap-semesters-container">
                {(acadPerfData.semesters || []).map((sec) => {
                  const hasRows = sec.rows && sec.rows.length > 0;
                  const hasMarksheet = sec.marksheet && sec.marksheet.marksheet_url;
                  
                  // Show semester card if it has rows or marksheet
                  if (!hasRows && !hasMarksheet) return null;
                  
                  return (
                    <div key={sec.semester} className="ap-semester-card">
                      <div className="ap-semester-header">
                        <span className="ap-semester-badge">{SEM_LABELS[sec.semester - 1]}</span>
                        {hasRows && (
                          <span className="ap-semester-count">{sec.rows.length} {sec.rows.length === 1 ? 'course' : 'courses'}</span>
                        )}
                      </div>
                      
                      {hasRows && (
                        <div className="ap-table-wrapper">
                        <table className="ap-table-mentor">
                          <thead>
                            <tr>
                              <th>Course</th>
                              <th>Grade</th>
                              <th>Attendance</th>
                            </tr>
                          </thead>
                          <tbody>
                            {sec.rows.map((r, i) => (
                              <tr key={r.id || i}>
                                <td className="ap-course-cell">{r.course}</td>
                                <td className="ap-grade-cell">
                                  <span className={`ap-grade-badge ap-grade-${(r.grade || '').toUpperCase().charAt(0)}`}>
                                    {r.grade || 'N/A'}
                                  </span>
                                </td>
                                <td className="ap-attendance-cell">
                                  <span className="ap-attendance-value">{r.overall_attendance || 'N/A'}</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        </div>
                      )}
                      
                      {/* Marksheet Section */}
                      {sec.marksheet && sec.marksheet.marksheet_url && (
                        <div className="ap-marksheet-section ap-marksheet-mentor">
                          <h4 className="ap-marksheet-title">Marksheet</h4>
                          <div className="ap-marksheet-uploaded">
                            <div className="ap-marksheet-info">
                              <FaFilePdf className="ap-marksheet-icon" />
                              <span>Marksheet Available</span>
                              {sec.marksheet.uploaded_at && (
                                <span className="ap-marksheet-date">
                                  ({new Date(sec.marksheet.uploaded_at).toLocaleDateString()})
                                </span>
                              )}
                            </div>
                            <button
                              type="button"
                              className="ap-view-marksheet-btn"
                              onClick={() => {
                                if (sec.marksheet.marksheet_view_url) {
                                  window.open(sec.marksheet.marksheet_view_url, '_blank');
                                } else {
                                  // Fetch fresh URL
                                  const token = sessionStorage.getItem('access_token');
                                  fetch(`${API_BASE_URL}/mentor/${mentor_id}/students/${acadPerfStudentUsn}/academic-performance/marksheet/${sec.semester}`, {
                                    headers: { Authorization: `Bearer ${token}` },
                                  })
                                    .then(res => res.json())
                                    .then(data => {
                                      if (data.marksheet_view_url) {
                                        window.open(data.marksheet_view_url, '_blank');
                                      } else {
                                        alert('Failed to load marksheet.');
                                      }
                                    })
                                    .catch(() => alert('Failed to load marksheet.'));
                                }
                              }}
                            >
                              <FaEye /> View Marksheet
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              </>
            )}
          </div>
        )}
        
        <div className="ap-modal-footer">
          <button onClick={closeAcademicPerformanceModal} className="ap-modal-close-btn">
            Close
          </button>
        </div>
      </Modal>
    </div>
  );
};

export default AssignedStudents;