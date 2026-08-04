import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/StudentProfile.css';
import { FaFilePdf, FaEye } from 'react-icons/fa';

const SEM_LABELS = ['I Sem', 'II Sem', 'III Sem', 'IV Sem'];

const AcademicPerformanceSummary = () => {
  const { student_usn } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [maxSemesters, setMaxSemesters] = useState(4);
  const [semesters, setSemesters] = useState([]);
  const [marksheets, setMarksheets] = useState({});

  const [secondaryMarksheets, setSecondaryMarksheets] = useState({});
  const [documentsSummary, setDocumentsSummary] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError('');
      try {
        const token = sessionStorage.getItem('access_token');
        if (!token) {
          setError('Please log in again.');
          setLoading(false);
          return;
        }
        const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          if (res.status === 403) {
            setError('You do not have access.');
          } else {
            setError('Failed to load academic performance.');
          }
          setLoading(false);
          return;
        }
        const data = await res.json();
        setMaxSemesters(data.max_semesters ?? 4);
        setSemesters(data.semesters ?? []);
        setSecondaryMarksheets(data.secondary_marksheets || {});
        setDocumentsSummary(data.documents_summary || null);
        
        // Extract marksheet info
        const marksheetMap = {};
        (data.semesters || []).forEach(sem => {
          if (sem.marksheet) {
            marksheetMap[sem.semester] = sem.marksheet;
          }
        });
        setMarksheets(marksheetMap);
      } catch (e) {
        setError('Network error. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [student_usn]);

  if (loading) {
    return (
      <div className="ap-summary-container">
        <div className="ap-summary-loading">Loading academic performance...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ap-summary-container">
        <div className="ap-summary-error">{error}</div>
      </div>
    );
  }

  // Check if there's any data
  const hasData =
    semesters.some((sem) => (sem.rows && sem.rows.length > 0) || sem.marksheet) ||
    Object.keys(secondaryMarksheets || {}).length > 0 ||
    (documentsSummary && documentsSummary.total_uploaded > 0);

  if (!hasData) {
    return (
      <div className="ap-summary-container">
        <h3 className="ap-summary-title">Academic Performance</h3>
        <div className="ap-summary-empty">
          <p>No academic performance data available yet.</p>
          <p className="ap-summary-hint">Visit the Academic Performance form to add your grades.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ap-summary-container">
      <h3 className="ap-summary-title">Academic Performance</h3>
      {documentsSummary && (
        <div className="ap-docs-summary" style={{ marginBottom: '1rem' }}>
          <div className="ap-docs-stat"><span>Uploaded</span><strong>{documentsSummary.total_uploaded}</strong></div>
          <div className="ap-docs-stat"><span>Missing</span><strong>{documentsSummary.missing_count}</strong></div>
          <div className="ap-docs-stat"><span>Pending</span><strong>{documentsSummary.pending_verification}</strong></div>
          <div className="ap-docs-stat"><span>Verified</span><strong>{documentsSummary.verified}</strong></div>
          <div className="ap-docs-stat"><span>Rejected</span><strong>{documentsSummary.rejected}</strong></div>
        </div>
      )}
      {(secondaryMarksheets[10] || secondaryMarksheets['10'] || secondaryMarksheets[12] || secondaryMarksheets['12']) && (
        <div className="ap-summary-semester" style={{ marginBottom: '1rem' }}>
          <h4 className="ap-summary-semester-label">School Marksheets</h4>
          {[10, 12].map((std) => {
            const info = secondaryMarksheets[std] || secondaryMarksheets[String(std)];
            if (!info) return null;
            return (
              <div key={std} className="ap-summary-marksheet">
                <div className="ap-summary-marksheet-info">
                  <FaFilePdf className="ap-summary-marksheet-icon" />
                  <span>{std}th Standard</span>
                  <span className={`ap-badge ap-badge-${(info.verification_status || 'pending').replace('_', '-')}`}>
                    {(info.verification_status || 'pending').replace('_', ' ')}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <div className="ap-summary-content">
        {semesters.map((sem) => {
          const rows = sem.rows || [];
          if (rows.length === 0 && !marksheets[sem.semester]) return null;

          return (
            <div key={sem.semester} className="ap-summary-semester">
              <h4 className="ap-summary-semester-label">
                {SEM_LABELS[sem.semester - 1] || `Semester ${sem.semester}`}
              </h4>
              {rows.length > 0 && (
              <div className="ap-summary-table-wrapper">
                <table className="ap-summary-table">
                  <thead>
                    <tr>
                      <th>Course</th>
                      <th>Grade</th>
                      <th>Attendance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row, idx) => (
                      <tr key={row.id || idx}>
                        <td>{row.course || '—'}</td>
                        <td>{row.grade || '—'}</td>
                        <td>{row.overall_attendance || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              )}
              
              {/* Marksheet Display */}
              {marksheets[sem.semester] && (
                <div className="ap-summary-marksheet">
                  <div className="ap-summary-marksheet-info">
                    <FaFilePdf className="ap-summary-marksheet-icon" />
                    <span>Marksheet Available</span>
                    <span className={`ap-badge ap-badge-${(marksheets[sem.semester].verification_status || 'pending').replace('_', '-')}`}>
                      {(marksheets[sem.semester].verification_status || 'pending').replace('_', ' ')}
                    </span>
                    {marksheets[sem.semester].uploaded_at && (
                      <span className="ap-summary-marksheet-date">
                        ({new Date(marksheets[sem.semester].uploaded_at).toLocaleDateString()})
                      </span>
                    )}
                  </div>
                  <button
                    className="ap-summary-view-marksheet-btn"
                    onClick={() => {
                      const marksheet = marksheets[sem.semester];
                      if (marksheet.marksheet_view_url) {
                        window.open(marksheet.marksheet_view_url, '_blank');
                      } else {
                        // Fetch fresh URL
                        const token = sessionStorage.getItem('access_token');
                        fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/marksheet/${sem.semester}`, {
                          headers: { Authorization: `Bearer ${token}` },
                        })
                          .then(res => res.json())
                          .then(data => {
                            if (data.marksheet_view_url) {
                              window.open(data.marksheet_view_url, '_blank');
                            }
                          })
                          .catch(() => setError('Failed to load marksheet.'));
                      }
                    }}
                  >
                    <FaEye /> View Marksheet
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AcademicPerformanceSummary;
