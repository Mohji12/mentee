import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/StudentDetailPage.css';
import '../../../assets/css/Report.css';
import './CounselingDashboard.css';
import pdfHeaderImage from '../../../assets/images/Screenshot 2026-03-18 111022.png';
import { FaArrowLeft, FaUser, FaGraduationCap, FaClipboardList, FaTasks, FaComments, FaCalendarAlt, FaCheck, FaTimes, FaLinkedin, FaPhone, FaEnvelope, FaMapMarkerAlt, FaClock, FaExternalLinkAlt, FaEye, FaFilePdf, FaClipboardCheck, FaLightbulb, FaLink, FaHistory, FaChartLine } from 'react-icons/fa';
import { addCanvasAsFullPage, appendNodeToPdfPaged, createA4Pdf, renderNodeToCanvas } from '../../../utils/pdfExport';

const MENTEE_TRACKER_LOGO_URL = 'https://res.cloudinary.com/dvlitilou/image/upload/v1779924617/logo_mentee-removebg-preview_coyhds.png';

const StudentDetailPage = () => {
  const { mentor_id, student_usn } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [studentData, setStudentData] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [sessionChains, setSessionChains] = useState(null);
  const [chainsLoading, setChainsLoading] = useState(false);
  const [showTimeline, setShowTimeline] = useState(true);
  const [pdfDownloading, setPdfDownloading] = useState(false);
  const [pdfError, setPdfError] = useState('');
  const exportRef = useRef(null);
  const [swotReport, setSwotReport] = useState(null);
  const [swotLoading, setSwotLoading] = useState(false);
  const [swotError, setSwotError] = useState('');
  const [mentorCounselingSessions, setMentorCounselingSessions] = useState([]);

  useEffect(() => {
    fetchStudentDetails();
  }, [mentor_id, student_usn]);

  useEffect(() => {
    if (activeTab === 'counseling') {
      fetchSessionChains();
    }
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === 'report' && !swotReport && !swotLoading && !swotError) {
      fetchSwotReport();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const fetchStudentDetails = async () => {
    try {
      setLoading(true);
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/students/${student_usn}/details`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) {
        if (response.status === 403) throw new Error('You do not have access to this student.');
        if (response.status === 404) throw new Error('Student not found.');
        throw new Error('Failed to load student details.');
      }

      const data = await response.json();
      setStudentData(data);
    } catch (err) {
      setError(err.message || 'Failed to load student details.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSessionChains = async () => {
    try {
      setChainsLoading(true);
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/counseling/students/${student_usn}/session-chain`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setSessionChains(data);
      }
    } catch (err) {
      console.error('Failed to fetch session chains:', err);
    } finally {
      setChainsLoading(false);
    }
  };

  const fetchSwotReport = async () => {
    try {
      setSwotLoading(true);
      setSwotError('');
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/student/${student_usn}/swot-report`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch report');
      }
      const data = await response.json();
      if (data?.strengths || data?.weaknesses || data?.opportunities || data?.threats) {
        setSwotReport(data);
      } else {
        setSwotReport({});
      }
    } catch (e) {
      setSwotError(e?.message || 'Failed to load report.');
    } finally {
      setSwotLoading(false);
    }
  };

  const fetchMentorCounselingSessionsForStudent = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const res = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions?limit=200&offset=0`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) return;
      const data = await res.json();
      const filtered = (data || []).filter((s) => String(s.student_usn || '').trim() === String(student_usn).trim());
      setMentorCounselingSessions(filtered);
    } catch (e) {
      // ignore for PDF; fallback to basic sessions
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status) => {
    const statusLower = (status || '').toLowerCase();
    if (['completed', 'approved', 'present'].includes(statusLower)) return 'status-success';
    if (['pending', 'scheduled'].includes(statusLower)) return 'status-warning';
    if (['rejected', 'cancelled', 'absent'].includes(statusLower)) return 'status-danger';
    return 'status-default';
  };

  const getOutcomeStatusLabel = (status) => {
    const labels = {
      'fully_resolved': 'Fully Resolved',
      'partially_resolved': 'Partially Resolved',
      'unresolved': 'Unresolved',
      'needs_followup': 'Needs Follow-up'
    };
    return labels[status] || status || 'Pending';
  };

  const getOutcomeStatusClass = (status) => {
    const classes = {
      'fully_resolved': 'outcome-resolved',
      'partially_resolved': 'outcome-partial',
      'unresolved': 'outcome-unresolved',
      'needs_followup': 'outcome-followup'
    };
    return classes[status] || 'outcome-pending';
  };

  const handleDownloadPdf = async () => {
    try {
      setPdfError('');
      setPdfDownloading(true);

      const safeName = (studentData?.profile?.student_name || 'Student')
        .replace(/[\\/:*?"<>|]/g, '')
        .trim();
      const safeUsn = (studentData?.profile?.student_usn || student_usn || '')
        .replace(/[\\/:*?"<>|]/g, '')
        .trim();
      const filename = `${safeName || 'student'}_${safeUsn || 'report'}.pdf`;

      document.body.classList.add('sdp-pdf-mode');

      // Ensure counseling extra data is available for export
      if (!sessionChains) {
        await fetchSessionChains();
      }
      if (!mentorCounselingSessions || mentorCounselingSessions.length === 0) {
        await fetchMentorCounselingSessionsForStudent();
      }
      if (!swotReport && !swotLoading) {
        await fetchSwotReport();
      }

      // Give React a moment to render any newly fetched data + images into the hidden export DOM
      await new Promise((resolve) => setTimeout(resolve, 250));

      const node = exportRef.current;
      if (!node) throw new Error('Export view not ready.');

      const coverNode = node.querySelector('.sdp-pdf-cover');
      const introNode = node.querySelector('.sdp-pdf-intro');
      const intro2Node = node.querySelector('.sdp-pdf-intro-2');
      const intro3Node = node.querySelector('.sdp-pdf-intro-3');
      const bodyNode = node.querySelector('.sdp-pdf-body');

      const pdf = createA4Pdf({ orientation: 'l' });

      // Dynamic scale to prevent "Array buffer allocation failed" on long reports
      const width = Math.max(node.scrollWidth || 0, node.offsetWidth || 0);
      const height = Math.max(node.scrollHeight || 0, node.offsetHeight || 0);
      const approxPixels = width * height;
      const exportScale = approxPixels > 22_000_000 ? 1 : approxPixels > 12_000_000 ? 1.25 : 1.5;

      if (coverNode) {
        const coverCanvas = await renderNodeToCanvas(coverNode, { scale: exportScale });
        addCanvasAsFullPage(pdf, coverCanvas);
      }

      if (introNode) {
        pdf.addPage();
        const introCanvas = await renderNodeToCanvas(introNode, { scale: exportScale });
        addCanvasAsFullPage(pdf, introCanvas);
      }

      if (intro2Node) {
        pdf.addPage();
        const introCanvas2 = await renderNodeToCanvas(intro2Node, { scale: exportScale });
        addCanvasAsFullPage(pdf, introCanvas2);
      }

      if (intro3Node) {
        pdf.addPage();
        const introCanvas3 = await renderNodeToCanvas(intro3Node, { scale: exportScale });
        addCanvasAsFullPage(pdf, introCanvas3);
      }

      if (bodyNode) {
        pdf.addPage();
        await appendNodeToPdfPaged({
          pdf,
          node: bodyNode,
          // Keep margin very small/zero to prevent edge clipping.
          marginMm: 0,
          scale: exportScale,
        });
      }

      // Outcome page should be last; append after the body.
      const outcomeNode = node.querySelector('.sdp-pdf-outcome');
      if (outcomeNode) {
        // Outcome should always start on a fresh page (avoid overlap/cut on last body page).
        pdf.addPage();
        const outcomeCanvas = await renderNodeToCanvas(outcomeNode, { scale: exportScale });
        addCanvasAsFullPage(pdf, outcomeCanvas);
      }

      pdf.save(filename);
    } catch (e) {
      setPdfError(e?.message || 'Failed to generate PDF.');
    } finally {
      document.body.classList.remove('sdp-pdf-mode');
      setPdfDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="sdp-loading">
        <div className="sdp-spinner"></div>
        <p>Loading student details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sdp-error">
        <p>{error}</p>
        <button onClick={() => navigate(-1)} className="sdp-back-btn">
          <FaArrowLeft /> Go Back
        </button>
      </div>
    );
  }

  const { profile, academic_performance, forms_status, activities, counseling_sessions, meetings, attendance, experiential_learning } = studentData;

  const SEM_LABELS = ['I Sem', 'II Sem', 'III Sem', 'IV Sem'];

  const ProfileSection = (
    <div className="sdp-section sdp-profile-section">
      <h2 className="sdp-section-title">
        <FaUser /> Personal Information
      </h2>
      <div className="sdp-profile-grid">
        <div className="sdp-profile-item">
          <label>Full Name</label>
          <span>{profile.student_name || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>USN</label>
          <span>{profile.student_usn}</span>
        </div>
        <div className="sdp-profile-item">
          <label><FaEnvelope /> Email</label>
          <span>{profile.student_email || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label><FaPhone /> Phone</label>
          <span>{profile.student_phoneno || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Gender</label>
          <span>{profile.gender || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Blood Group</label>
          <span>{profile.blood_group || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Date of Birth</label>
          <span>{formatDate(profile.date_of_birth)}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Guardian Contact</label>
          <span>{profile.parent_guardian_contact || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Mother Contact</label>
          <span>{profile.mother_contact || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Father Contact</label>
          <span>{profile.father_contact || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Program</label>
          <span>{profile.student_program || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Batch</label>
          <span>{profile.student_batch || 'N/A'}</span>
        </div>
        <div className="sdp-profile-item">
          <label>Semester</label>
          <span>{profile.semester || 'N/A'}</span>
        </div>
        {profile.linkedin && (
          <div className="sdp-profile-item sdp-linkedin">
            <label><FaLinkedin /> LinkedIn</label>
            <a href={profile.linkedin} target="_blank" rel="noopener noreferrer">
              View Profile <FaExternalLinkAlt />
            </a>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="sdp-container">
      {/* Header Section */}
      <div className="sdp-header">
        <div className="sdp-header-left">
          <button onClick={() => navigate(-1)} className="sdp-back-btn">
            <FaArrowLeft /> Back to Students
          </button>
          <div className="sdp-header-info">
          <div className="sdp-avatar">
            <FaUser />
          </div>
          <div className="sdp-header-text">
            <h1>{profile.student_name || 'Student'}</h1>
            <div className="sdp-header-badges">
              <span className="sdp-usn-badge">{profile.student_usn}</span>
              {profile.student_program && (
                <span className="sdp-program-badge">{profile.student_program}</span>
              )}
              {profile.semester && (
                <span className="sdp-semester-badge">Semester {profile.semester}</span>
              )}
            </div>
          </div>
        </div>
        </div>
        <div className="sdp-header-actions">
          <button
            type="button"
            className="sdp-download-full-report-btn"
            onClick={handleDownloadPdf}
            disabled={pdfDownloading}
          >
            {pdfDownloading ? (
              <>
                <span className="sdp-download-spinner" /> Generating PDF...
              </>
            ) : (
              <>
                <FaFilePdf /> Download PDF
              </>
            )}
          </button>
          {pdfError && <div className="sdp-download-error">{pdfError}</div>}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="sdp-tabs">
        <button
          className={`sdp-tab ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <FaUser /> Profile
        </button>
        <button
          className={`sdp-tab ${activeTab === 'report' ? 'active' : ''}`}
          onClick={() => setActiveTab('report')}
        >
          <FaChartLine /> Report
        </button>
        <button
          className={`sdp-tab ${activeTab === 'academic' ? 'active' : ''}`}
          onClick={() => setActiveTab('academic')}
        >
          <FaGraduationCap /> Academic
        </button>
        <button
          className={`sdp-tab ${activeTab === 'forms' ? 'active' : ''}`}
          onClick={() => setActiveTab('forms')}
        >
          <FaClipboardList /> Forms
        </button>
        <button
          className={`sdp-tab ${activeTab === 'activities' ? 'active' : ''}`}
          onClick={() => setActiveTab('activities')}
        >
          <FaTasks /> Activities
        </button>
        <button
          className={`sdp-tab ${activeTab === 'counseling' ? 'active' : ''}`}
          onClick={() => setActiveTab('counseling')}
        >
          <FaComments /> Student Support
        </button>
        <button
          className={`sdp-tab ${activeTab === 'meetings' ? 'active' : ''}`}
          onClick={() => setActiveTab('meetings')}
        >
          <FaCalendarAlt /> Meetings
        </button>
        <button
          className={`sdp-tab ${activeTab === 'attendance' ? 'active' : ''}`}
          onClick={() => setActiveTab('attendance')}
        >
          <FaClipboardCheck /> Attendance
        </button>
        <button
          className={`sdp-tab ${activeTab === 'experiential' ? 'active' : ''}`}
          onClick={() => setActiveTab('experiential')}
        >
          <FaLightbulb /> Experiential Learning
        </button>
      </div>

      {/* Tab Content */}
      <div className="sdp-content">
        {/* Profile Tab */}
        {activeTab === 'profile' && (
          ProfileSection
        )}

        {/* Student Report Tab */}
        {activeTab === 'report' && (
          <div className="sdp-section">
            <h2 className="sdp-section-title">
              <FaChartLine /> Student Analysis Report
            </h2>
            {swotLoading && (
              <div className="report-loading">
                <div className="loading-spinner"></div>
                <p>Loading report...</p>
              </div>
            )}
            {swotError && (
              <div className="report-error">
                <div className="error-icon">⚠️</div>
                <h2>Error Loading Report</h2>
                <p>{swotError}</p>
                <button onClick={fetchSwotReport} className="retry-btn">
                  Try Again
                </button>
              </div>
            )}
            {!swotLoading && !swotError && (!swotReport || Object.keys(swotReport).length === 0) && (
              <div className="report-empty">
                <div className="empty-icon">📊</div>
                <h3>No Report Available</h3>
                <p>SWOT analysis report is not available yet for this student.</p>
              </div>
            )}
            {!swotLoading && !swotError && swotReport && Object.keys(swotReport).length > 0 && (
              <div className="report-page" style={{ padding: 0, minHeight: 'auto' }}>
                <div className="swot-section">
                  <h2 className="section-title">SWOT Analysis</h2>
                  <div className="swot-grid">
                    <div className="swot-card strengths">
                      <div className="card-header">
                        <div className="card-icon">💪</div>
                        <h3>Strengths</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.strengths || 'No strengths identified yet.'}</p>
                      </div>
                    </div>
                    <div className="swot-card opportunities">
                      <div className="card-header">
                        <div className="card-icon">🎯</div>
                        <h3>Opportunities</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.opportunities || 'No opportunities identified yet.'}</p>
                      </div>
                    </div>
                    <div className="swot-card weaknesses">
                      <div className="card-header">
                        <div className="card-icon">⚠️</div>
                        <h3>Weaknesses</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.weaknesses || 'No weaknesses identified yet.'}</p>
                      </div>
                    </div>
                    <div className="swot-card threats">
                      <div className="card-header">
                        <div className="card-icon">🚨</div>
                        <h3>Threats</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.threats || 'No threats identified yet.'}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="additional-section">
                  <h2 className="section-title">Personal Insights</h2>
                  <div className="insights-grid">
                    {swotReport.professional_aspirations && (
                      <div className="insight-card">
                        <div className="insight-header">
                          <div className="insight-icon">🎯</div>
                          <h3>Professional Aspirations</h3>
                        </div>
                        <p>{swotReport.professional_aspirations}</p>
                      </div>
                    )}
                    {swotReport['hobbies/interests'] && (
                      <div className="insight-card">
                        <div className="insight-header">
                          <div className="insight-icon">🎨</div>
                          <h3>Hobbies & Interests</h3>
                        </div>
                        <p>{swotReport['hobbies/interests']}</p>
                      </div>
                    )}
                    {swotReport.detailed_analysis && (
                      <div className="insight-card">
                        <div className="insight-header">
                          <div className="insight-icon">📊</div>
                          <h3>Detailed Analysis</h3>
                        </div>
                        <p>{swotReport.detailed_analysis}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Academic Performance Tab */}
        {activeTab === 'academic' && (
          <div className="sdp-section sdp-academic-section">
            <h2 className="sdp-section-title">
              <FaGraduationCap /> Academic Performance
            </h2>
            
            {/* Secondary Marksheets */}
            {academic_performance.secondary_marksheets && 
             Object.keys(academic_performance.secondary_marksheets).length > 0 && (
              <div className="sdp-secondary-marksheets">
                <h3>10th & 12th Marksheets</h3>
                <div className="sdp-marksheet-list">
                  {[10, 12].map((std) => {
                    const info = academic_performance.secondary_marksheets[std];
                    if (!info) return null;
                    return (
                      <div key={std} className="sdp-marksheet-item">
                        <span className="sdp-marksheet-label">{std}th Standard</span>
                        {info.uploaded_at && (
                          <span className="sdp-marksheet-date">
                            Uploaded: {formatDate(info.uploaded_at)}
                          </span>
                        )}
                        {info.marksheet_view_url && (
                          <button
                            className="sdp-view-btn"
                            onClick={() => window.open(info.marksheet_view_url, '_blank')}
                          >
                            <FaEye /> View
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Semester-wise Performance */}
            {academic_performance.semesters && 
             Object.keys(academic_performance.semesters).length > 0 ? (
              <div className="sdp-semesters">
                {Object.entries(academic_performance.semesters)
                  .sort(([a], [b]) => Number(a) - Number(b))
                  .map(([sem, data]) => {
                    const hasRows = data.rows && data.rows.length > 0;
                    const hasMarksheet = data.marksheet && data.marksheet.marksheet_url;
                    if (!hasRows && !hasMarksheet) return null;
                    
                    return (
                      <div key={sem} className="sdp-semester-card">
                        <div className="sdp-semester-header">
                          <span className="sdp-semester-badge">
                            {SEM_LABELS[Number(sem) - 1] || `Semester ${sem}`}
                          </span>
                          {hasRows && (
                            <span className="sdp-course-count">
                              {data.rows.length} {data.rows.length === 1 ? 'course' : 'courses'}
                            </span>
                          )}
                        </div>
                        
                        {hasRows && (
                          <table className="sdp-grades-table">
                            <thead>
                              <tr>
                                <th>Course</th>
                                <th>Grade</th>
                                <th>Attendance</th>
                              </tr>
                            </thead>
                            <tbody>
                              {data.rows.map((row, idx) => (
                                <tr key={row.id || idx}>
                                  <td>{row.course}</td>
                                  <td>
                                    <span className={`sdp-grade sdp-grade-${(row.grade || '').charAt(0).toUpperCase()}`}>
                                      {row.grade || 'N/A'}
                                    </span>
                                  </td>
                                  <td>{row.overall_attendance || 'N/A'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        )}
                        
                        {hasMarksheet && (
                          <div className="sdp-semester-marksheet">
                            <FaFilePdf className="sdp-pdf-icon" />
                            <span>Marksheet Available</span>
                            {data.marksheet.uploaded_at && (
                              <span className="sdp-marksheet-date">
                                ({formatDate(data.marksheet.uploaded_at)})
                              </span>
                            )}
                            <button
                              className="sdp-view-btn"
                              onClick={() => window.open(data.marksheet.marksheet_view_url, '_blank')}
                            >
                              <FaEye /> View
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaGraduationCap className="sdp-empty-icon" />
                <p>No academic performance data available yet.</p>
              </div>
            )}
          </div>
        )}

        {/* Forms Status Tab */}
        {activeTab === 'forms' && (
          <div className="sdp-section sdp-forms-section">
            <h2 className="sdp-section-title">
              <FaClipboardList /> Forms Status
            </h2>
            <div className="sdp-forms-grid">
              {/* Psychometric Form */}
              <div className={`sdp-form-card ${forms_status.psychometric.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.psychometric.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>Psychometric Form</h3>
                  <p className="sdp-form-status">
                    {forms_status.psychometric.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.psychometric.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.psychometric.submitted_at)}
                    </p>
                  )}
                </div>
              </div>

              {/* SWOT Analysis */}
              <div className={`sdp-form-card ${forms_status.swot.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.swot.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>SWOT Analysis</h3>
                  <p className="sdp-form-status">
                    {forms_status.swot.completed 
                      ? (forms_status.swot.has_analysis ? 'Generated' : 'Completed')
                      : 'Not Generated'}
                  </p>
                </div>
              </div>

              {/* MCA Assessment */}
              <div className={`sdp-form-card ${forms_status.mca.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.mca.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>MCA Assessment</h3>
                  <p className="sdp-form-status">
                    {forms_status.mca.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.mca.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.mca.submitted_at)}
                    </p>
                  )}
                </div>
              </div>

              {/* 16PF Form */}
              <div className={`sdp-form-card ${forms_status.pf16.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.pf16.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>16PF Form</h3>
                  <p className="sdp-form-status">
                    {forms_status.pf16.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.pf16.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.pf16.submitted_at)}
                    </p>
                  )}
                </div>
              </div>

              {/* IBP Form */}
              <div className={`sdp-form-card ${forms_status.ibp.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.ibp.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>IBP Form</h3>
                  <p className="sdp-form-status">
                    {forms_status.ibp.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.ibp.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.ibp.submitted_at)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Activities Tab */}
        {activeTab === 'activities' && (
          <div className="sdp-section sdp-activities-section">
            <h2 className="sdp-section-title">
              <FaTasks /> Activities Overview
            </h2>
            
            {/* Activity Summary Stats */}
            <div className="sdp-activity-stats">
              <div className="sdp-activity-stat-card total">
                <div className="sdp-activity-stat-icon"><FaTasks /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">{activities.length}</span>
                  <span className="sdp-activity-stat-label">Total Activities</span>
                </div>
              </div>
              <div className="sdp-activity-stat-card approved">
                <div className="sdp-activity-stat-icon"><FaCheck /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">
                    {activities.filter(a => (a.status || '').toLowerCase() === 'approved').length}
                  </span>
                  <span className="sdp-activity-stat-label">Approved</span>
                </div>
              </div>
              <div className="sdp-activity-stat-card pending">
                <div className="sdp-activity-stat-icon"><FaClock /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">
                    {activities.filter(a => (a.status || '').toLowerCase() === 'pending' || !a.status).length}
                  </span>
                  <span className="sdp-activity-stat-label">Pending</span>
                </div>
              </div>
              <div className="sdp-activity-stat-card rejected">
                <div className="sdp-activity-stat-icon"><FaTimes /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">
                    {activities.filter(a => (a.status || '').toLowerCase() === 'rejected').length}
                  </span>
                  <span className="sdp-activity-stat-label">Rejected</span>
                </div>
              </div>
            </div>

            {activities.length > 0 ? (
              <div className="sdp-activities-table-container">
                <table className="sdp-activities-table">
                  <thead>
                    <tr>
                      <th className="th-id">Activity ID</th>
                      <th className="th-activity">Activity</th>
                      <th className="th-term">Term Type</th>
                      <th className="th-deadline">Deadline</th>
                      <th className="th-progress">Progress</th>
                      <th className="th-status">Status</th>
                      <th className="th-actions">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activities.map((activity, index) => (
                      <tr 
                        key={activity.id} 
                        className={`${index % 2 === 0 ? 'row-even' : 'row-odd'} ${
                          (activity.status || '').toLowerCase() === 'rejected' ? 'row-rejected' : ''
                        }`}
                      >
                        <td className="td-id">
                          <span className="activity-id-badge">{activity.id}</span>
                        </td>
                        <td className="td-activity">
                          <div className="activity-info">
                            <span className="activity-name">{activity.activity}</span>
                            {activity.requested_by && (
                              <span className="activity-requested-by">
                                Requested by: <strong>{activity.requested_by}</strong>
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="td-term">
                          <span className={`term-badge ${(activity.duration_type || '').toLowerCase().replace(' ', '-')}`}>
                            {activity.duration_type || 'N/A'}
                          </span>
                        </td>
                        <td className="td-deadline">
                          <div className="deadline-info">
                            <FaCalendarAlt className="deadline-icon" />
                            <span>{formatDate(activity.deadline)}</span>
                          </div>
                        </td>
                        <td className="td-progress">
                          {activity.percentage !== null ? (
                            <div className="progress-container">
                              <div className="progress-bar-wrapper">
                                <div 
                                  className={`progress-bar-fill ${
                                    activity.percentage >= 100 ? 'complete' : 
                                    activity.percentage >= 50 ? 'half' : 'low'
                                  }`}
                                  style={{ width: `${Math.min(activity.percentage, 100)}%` }}
                                ></div>
                              </div>
                              <span className="progress-text">{activity.percentage}%</span>
                            </div>
                          ) : (
                            <span className="no-progress">—</span>
                          )}
                        </td>
                        <td className="td-status">
                          <span className={`status-pill ${(activity.status || 'pending').toLowerCase()}`}>
                            {activity.status === 'Approved' && <FaCheck />}
                            {activity.status === 'Rejected' && <FaTimes />}
                            {(!activity.status || activity.status === 'Pending') && <FaClock />}
                            {activity.status || 'Pending'}
                          </span>
                        </td>
                        <td className="td-actions">
                          <div className="action-buttons">
                            {activity.proof_url && (
                              <a 
                                href={activity.proof_url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="action-btn view-proof"
                                title="View Proof"
                              >
                                <FaEye />
                              </a>
                            )}
                            {activity.remarks && (
                              <button 
                                className="action-btn view-remarks"
                                title={activity.remarks}
                                onClick={() => alert(`Remarks: ${activity.remarks}`)}
                              >
                                💬
                              </button>
                            )}
                            {activity.rejection_reason && (
                              <button 
                                className="action-btn view-rejection"
                                title={`Rejection Reason: ${activity.rejection_reason}`}
                                onClick={() => alert(`Rejection Reason: ${activity.rejection_reason}`)}
                              >
                                ⚠️
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaTasks className="sdp-empty-icon" />
                <p>No activities assigned yet.</p>
              </div>
            )}
          </div>
        )}

        {/* Counseling Tab */}
        {activeTab === 'counseling' && (
          <div className="sdp-section sdp-counseling-section">
            <div className="sdp-counseling-header">
              <h2 className="sdp-section-title">
                <FaComments /> Student Support Sessions ({counseling_sessions.length})
              </h2>
              <div className="sdp-view-toggle">
                <button 
                  className={`sdp-toggle-btn ${showTimeline ? 'active' : ''}`}
                  onClick={() => setShowTimeline(true)}
                >
                  <FaHistory /> Timeline
                </button>
                <button 
                  className={`sdp-toggle-btn ${!showTimeline ? 'active' : ''}`}
                  onClick={() => setShowTimeline(false)}
                >
                  <FaLink /> Session Chains
                </button>
              </div>
            </div>

            {/* Session Summary Stats */}
            {counseling_sessions.length > 0 && (
              <div className="sdp-support-stats">
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon total"><FaComments /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">{counseling_sessions.length}</span>
                    <span className="sdp-support-stat-label">Total Sessions</span>
                  </div>
                </div>
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon completed"><FaCheck /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">
                      {counseling_sessions.filter(s => s.status === 'completed').length}
                    </span>
                    <span className="sdp-support-stat-label">Completed</span>
                  </div>
                </div>
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon scheduled"><FaCalendarAlt /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">
                      {counseling_sessions.filter(s => s.status === 'scheduled').length}
                    </span>
                    <span className="sdp-support-stat-label">Scheduled</span>
                  </div>
                </div>
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon followup"><FaLink /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">
                      {sessionChains?.chains?.length || 0}
                    </span>
                    <span className="sdp-support-stat-label">Session Chains</span>
                  </div>
                </div>
              </div>
            )}

            {counseling_sessions.length > 0 ? (
              <>
                {/* Timeline View */}
                {showTimeline && (
                  <div className="sdp-timeline">
                    {counseling_sessions.map((session) => (
                      <div key={session.id} className={`sdp-timeline-item ${session.parent_session_id ? 'is-followup' : ''}`}>
                        <div className={`sdp-timeline-marker ${session.outcome_status ? getOutcomeStatusClass(session.outcome_status) : ''}`}></div>
                        <div className="sdp-timeline-content">
                          <div className="sdp-session-header">
                            <div className="sdp-session-header-left">
                              <span className="sdp-session-id">#{session.counseling_id || session.id}</span>
                              <span className="sdp-session-date">
                                <FaCalendarAlt /> {formatDateTime(session.session_date)}
                              </span>
                            </div>
                            <div className="sdp-session-badges">
                              <span className={`sdp-status-badge ${getStatusColor(session.status)}`}>
                                {session.status}
                              </span>
                              {session.is_urgent && (
                                <span className="sdp-urgent-badge">Urgent</span>
                              )}
                              {session.parent_session_id && (
                                <span className="sdp-followup-badge">
                                  <FaLink /> Follow-up
                                </span>
                              )}
                              {session.outcome_status && (
                                <span className={`sdp-outcome-badge ${getOutcomeStatusClass(session.outcome_status)}`}>
                                  {getOutcomeStatusLabel(session.outcome_status)}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="sdp-session-details">
                            <div className="sdp-session-item">
                              <label><FaMapMarkerAlt /> Venue</label>
                              <span>{session.venue || 'N/A'}</span>
                            </div>
                            {session.parent_session_id && (
                              <div className="sdp-session-item chain-link">
                                <label><FaLink /> Parent Session</label>
                                <span>#{session.parent_session_id}</span>
                              </div>
                            )}
                            {session.reason && (
                              <div className="sdp-session-item full-width">
                                <label>Reason</label>
                                <span>{session.reason}</span>
                              </div>
                            )}
                            {session.outcome_notes && (
                              <div className="sdp-session-item full-width outcome-notes">
                                <label><FaChartLine /> Outcome Notes</label>
                                <span>{session.outcome_notes}</span>
                              </div>
                            )}
                            {session.followup_date && (
                              <div className="sdp-session-item followup-info">
                                <label><FaCalendarAlt /> Follow-up Date</label>
                                <span>
                                  {formatDate(session.followup_date)}
                                  {session.followup_scheduled && <span className="scheduled-badge"> ✓ Scheduled</span>}
                                </span>
                              </div>
                            )}
                            {session.notes && (
                              <div className="sdp-session-item full-width">
                                <label>Notes</label>
                                <span>{session.notes}</span>
                              </div>
                            )}
                            {session.feedback && (
                              <div className="sdp-session-item full-width">
                                <label>Feedback</label>
                                <span>{session.feedback}</span>
                              </div>
                            )}
                            {(session.student_rating || session.mentor_rating) && (
                              <div className="sdp-ratings">
                                {session.student_rating && (
                                  <span>Student Rating: {'⭐'.repeat(session.student_rating)}</span>
                                )}
                                {session.mentor_rating && (
                                  <span>Mentor Rating: {'⭐'.repeat(session.mentor_rating)}</span>
                                )}
                              </div>
                            )}
                            {session.referred_to_name && (
                              <div className="sdp-referral">
                                <label>Referred To</label>
                                <span>{session.referred_to_name} ({session.referred_to_contact || 'No contact'})</span>
                              </div>
                            )}
                            {session.google_meet_link && (
                              <a 
                                href={session.google_meet_link} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="sdp-meet-link"
                              >
                                Join Google Meet <FaExternalLinkAlt />
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Session Chains View */}
                {!showTimeline && (
                  <div className="sdp-chains-container">
                    {chainsLoading ? (
                      <div className="sdp-chains-loading">Loading session chains...</div>
                    ) : sessionChains && sessionChains.chains && sessionChains.chains.length > 0 ? (
                      sessionChains.chains.map((chain, chainIdx) => (
                        <div key={chain.original_session_id} className="sdp-chain-card">
                          <div className="sdp-chain-header">
                            <h3><FaLink /> Session Chain #{chainIdx + 1}</h3>
                            <span className="sdp-chain-info">
                              {chain.total_in_chain} {chain.total_in_chain === 1 ? 'session' : 'sessions'}
                            </span>
                          </div>
                          <div className="sdp-chain-timeline">
                            {chain.sessions.map((session, sessionIdx) => (
                              <div 
                                key={session.counseling_id} 
                                className={`sdp-chain-node ${session.is_followup ? 'is-followup' : 'is-original'}`}
                              >
                                <div className="sdp-chain-connector">
                                  <div className={`sdp-chain-dot ${getOutcomeStatusClass(session.outcome_status)}`}></div>
                                  {sessionIdx < chain.sessions.length - 1 && <div className="sdp-chain-line"></div>}
                                </div>
                                <div className="sdp-chain-content">
                                  <div className="sdp-chain-session-header">
                                    <span className="sdp-chain-session-id">
                                      {session.is_followup && <FaLink className="followup-icon" />}
                                      #{session.counseling_id}
                                    </span>
                                    <span className={`sdp-mini-badge ${getStatusColor(session.status)}`}>
                                      {session.status}
                                    </span>
                                  </div>
                                  <div className="sdp-chain-session-details">
                                    <span className="sdp-chain-date">
                                      <FaCalendarAlt /> {formatDateTime(session.session_date)}
                                    </span>
                                    <span className="sdp-chain-venue">
                                      <FaMapMarkerAlt /> {session.venue}
                                    </span>
                                    {session.outcome_status && (
                                      <span className={`sdp-chain-outcome ${getOutcomeStatusClass(session.outcome_status)}`}>
                                        {getOutcomeStatusLabel(session.outcome_status)}
                                      </span>
                                    )}
                                  </div>
                                  {session.reason && (
                                    <p className="sdp-chain-reason">{session.reason}</p>
                                  )}
                                  {session.outcome_notes && (
                                    <p className="sdp-chain-notes"><strong>Notes:</strong> {session.outcome_notes}</p>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="sdp-empty-chains">
                        <FaLink className="sdp-empty-icon" />
                        <p>No session chains found.</p>
                        <span>Sessions with follow-ups will appear here as chains.</span>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="sdp-empty-state">
                <FaComments className="sdp-empty-icon" />
                <p>No student support sessions recorded.</p>
              </div>
            )}
          </div>
        )}

        {/* Meetings Tab */}
        {activeTab === 'meetings' && (
          <div className="sdp-section sdp-meetings-section">
            <h2 className="sdp-section-title">
              <FaCalendarAlt /> Meetings ({meetings.length})
            </h2>
            {meetings.length > 0 ? (
              <div className="sdp-meetings-list">
                {meetings.map((meeting) => (
                  <div key={meeting.id} className="sdp-meeting-card">
                    <div className="sdp-meeting-header">
                      <span className="sdp-meeting-date">
                        <FaCalendarAlt /> {formatDateTime(meeting.meeting_date)}
                      </span>
                      <div className="sdp-meeting-badges">
                        <span className={`sdp-status-badge ${getStatusColor(meeting.status)}`}>
                          {meeting.status || 'Scheduled'}
                        </span>
                        {meeting.attendance && (
                          <span className={`sdp-attendance-badge ${getStatusColor(meeting.attendance)}`}>
                            {meeting.attendance}
                          </span>
                        )}
                        <span className="sdp-mode-badge">
                          {meeting.meeting_mode === 'online' ? '🌐 Online' : '🏢 Offline'}
                        </span>
                      </div>
                    </div>
                    <div className="sdp-meeting-details">
                      <div className="sdp-meeting-item">
                        <label><FaMapMarkerAlt /> Venue</label>
                        <span>{meeting.venue || 'N/A'}</span>
                      </div>
                      {meeting.duration && (
                        <div className="sdp-meeting-item">
                          <label><FaClock /> Duration</label>
                          <span>{meeting.duration} minutes</span>
                        </div>
                      )}
                      {meeting.agenda && (
                        <div className="sdp-meeting-item full-width">
                          <label>Agenda</label>
                          <span>{meeting.agenda}</span>
                        </div>
                      )}
                      {meeting.progress_notes && (
                        <div className="sdp-meeting-item full-width">
                          <label>Progress Notes</label>
                          <span>{meeting.progress_notes}</span>
                        </div>
                      )}
                      {meeting.google_meet_link && (
                        <a 
                          href={meeting.google_meet_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="sdp-meet-link"
                        >
                          Join Google Meet <FaExternalLinkAlt />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaCalendarAlt className="sdp-empty-icon" />
                <p>No meetings scheduled yet.</p>
              </div>
            )}
          </div>
        )}

        {/* Attendance Tab */}
        {activeTab === 'attendance' && (
          <div className="sdp-section sdp-attendance-section">
            <h2 className="sdp-section-title">
              <FaClipboardCheck /> Attendance Statistics
            </h2>
            
            {/* Attendance Summary Cards */}
            {attendance && attendance.summary && (
              <div className="sdp-attendance-summary">
                <div className="sdp-stat-card sdp-stat-total">
                  <div className="sdp-stat-value">{attendance.summary.total_sessions}</div>
                  <div className="sdp-stat-label">Total Sessions</div>
                </div>
                <div className="sdp-stat-card sdp-stat-present">
                  <div className="sdp-stat-value">{attendance.summary.present}</div>
                  <div className="sdp-stat-label">Present</div>
                </div>
                <div className="sdp-stat-card sdp-stat-late">
                  <div className="sdp-stat-value">{attendance.summary.late}</div>
                  <div className="sdp-stat-label">Late</div>
                </div>
                <div className="sdp-stat-card sdp-stat-absent">
                  <div className="sdp-stat-value">{attendance.summary.absent}</div>
                  <div className="sdp-stat-label">Absent</div>
                </div>
                <div className="sdp-stat-card sdp-stat-percentage">
                  <div className="sdp-stat-value">{attendance.summary.attendance_percentage}%</div>
                  <div className="sdp-stat-label">Attendance Rate</div>
                  <div className="sdp-progress-ring">
                    <svg viewBox="0 0 36 36">
                      <path
                        className="sdp-progress-bg"
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="sdp-progress-bar"
                        strokeDasharray={`${attendance.summary.attendance_percentage}, 100`}
                        d="M18 2.0845
                          a 15.9155 15.9155 0 0 1 0 31.831
                          a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            )}

            {/* Attendance Records */}
            <h3 className="sdp-subsection-title">Attendance History</h3>
            {attendance && attendance.records && attendance.records.length > 0 ? (
              <div className="sdp-attendance-list">
                {attendance.records.map((record) => (
                  <div key={record.id} className="sdp-attendance-card">
                    <div className="sdp-attendance-header">
                      <span className="sdp-attendance-session">{record.session_name}</span>
                      <span className={`sdp-status-badge ${
                        record.status === 'present' ? 'status-success' : 
                        record.status === 'late' ? 'status-warning' : 'status-danger'
                      }`}>
                        {record.status === 'present' ? '✓ Present' : 
                         record.status === 'late' ? '⏰ Late' : '✗ Absent'}
                      </span>
                    </div>
                    <div className="sdp-attendance-details">
                      <div className="sdp-attendance-item">
                        <label><FaCalendarAlt /> Date</label>
                        <span>{formatDateTime(record.session_date)}</span>
                      </div>
                      {record.location && (
                        <div className="sdp-attendance-item">
                          <label><FaMapMarkerAlt /> Location</label>
                          <span>{record.location}</span>
                        </div>
                      )}
                      <div className="sdp-attendance-item">
                        <label><FaClock /> Marked At</label>
                        <span>{formatDateTime(record.marked_at)}</span>
                      </div>
                      {record.notes && (
                        <div className="sdp-attendance-item full-width">
                          <label>Notes</label>
                          <span>{record.notes}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaClipboardCheck className="sdp-empty-icon" />
                <p>No attendance records found.</p>
              </div>
            )}
          </div>
        )}

        {/* Experiential Learning Tab */}
        {activeTab === 'experiential' && (
          <div className="sdp-section sdp-experiential-section">
            <h2 className="sdp-section-title">
              <FaLightbulb /> Experiential Learning ({experiential_learning?.length || 0})
            </h2>
            
            {/* Summary Card */}
            <div className="sdp-exp-summary">
              <div className="sdp-exp-summary-card">
                <div className="sdp-exp-summary-icon">
                  <FaLightbulb />
                </div>
                <div className="sdp-exp-summary-info">
                  <span className="sdp-exp-summary-value">{experiential_learning?.length || 0}</span>
                  <span className="sdp-exp-summary-label">Total Learning Experiences</span>
                </div>
              </div>
            </div>

            {experiential_learning && experiential_learning.length > 0 ? (
              <div className="sdp-exp-grid">
                {experiential_learning.map((entry) => (
                  <div key={entry.id} className="sdp-exp-card">
                    <div className="sdp-exp-card-header">
                      <div className="sdp-exp-card-icon">
                        <FaLightbulb />
                      </div>
                      <div className="sdp-exp-card-title">
                        <h3>{entry.title}</h3>
                        <span className="sdp-exp-date">
                          <FaCalendarAlt /> {formatDate(entry.created_at)}
                        </span>
                      </div>
                    </div>
                    <div className="sdp-exp-card-body">
                      <div className="sdp-exp-description">
                        <label>Experience Details</label>
                        <p>{entry.detailed_explanation}</p>
                      </div>
                      {entry.proof_url && (
                        <div className="sdp-exp-proof">
                          <a 
                            href={entry.proof_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="sdp-exp-proof-btn"
                          >
                            <FaEye /> View Proof/Certificate
                          </a>
                        </div>
                      )}
                    </div>
                    {entry.updated_at && entry.updated_at !== entry.created_at && (
                      <div className="sdp-exp-card-footer">
                        <span className="sdp-exp-updated">
                          Last updated: {formatDate(entry.updated_at)}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaLightbulb className="sdp-empty-icon" />
                <p>No experiential learning entries recorded yet.</p>
                <span className="sdp-empty-subtext">
                  The student hasn't added any learning experiences.
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* PDF Export: continuous stacked layout (hidden) */}
      <div className="sdp-export-root" ref={exportRef} aria-hidden="true">
        <div className="sdp-content">
          <div className="sdp-pdf-cover" aria-hidden="true">
            <div className="sdp-pdf-header-image">
              <img src={pdfHeaderImage} alt="" />
            </div>
          </div>
          <div className="sdp-pdf-intro" aria-hidden="true">
            <div className="sdp-pdf-intro-card">
              <div className="sdp-pdf-intro-header">
                <div className="sdp-pdf-intro-brand">
                  <img className="sdp-pdf-intro-logo" src={MENTEE_TRACKER_LOGO_URL} alt="" />
                  <div className="sdp-pdf-intro-brandtext">
                    <div className="sdp-pdf-intro-university">JAIN (Deemed-to-be University)</div>
                    <div className="sdp-pdf-intro-sub">Mentoring Process</div>
                  </div>
                </div>
                <div className="sdp-pdf-intro-badge">Student Mentoring System</div>
              </div>

              <div className="sdp-pdf-intro-body">
                <p>
                  The University has a well-defined Student Mentoring system in place, where each faculty is in-charge of around 18 to 20 (approximately) students.
                  The University believes in a systematic process for mentoring.
                </p>
                <p>
                  Each student is made to fill a form which contains all the personal and academic details. The mentor counsels the students on academics, personal issues,
                  career and emotional issues which help in their overall development.
                </p>
                <p>
                  Participation in activities and prizes won are documented. General health condition and major health issues if any are noted and medical assistance is referred to.
                </p>
                <p>
                  The mentor also discusses the curricular, co-curricular and extra-curricular activities participated by the student. Performance in academics and attendance are given primary importance.
                </p>
                <p>
                  Suggestions are given for improvement. A comparative analysis is made in the next meeting to measure the performance of the student.
                </p>
                <p className="sdp-pdf-intro-highlight">
                  There has been a remarkable improvement in the academic performance of the students.
                </p>
              </div>
            </div>
          </div>
          <div className="sdp-pdf-intro-2" aria-hidden="true">
            <div className="sdp-pdf-intro-card">
              <div className="sdp-pdf-intro-header">
                <div className="sdp-pdf-intro-brand">
                  <img className="sdp-pdf-intro-logo" src={MENTEE_TRACKER_LOGO_URL} alt="" />
                  <div className="sdp-pdf-intro-brandtext">
                    <div className="sdp-pdf-intro-university">JAIN (Deemed-to-be University)</div>
                    <div className="sdp-pdf-intro-sub">Mentoring Outcomes & Objectives</div>
                  </div>
                </div>
                <div className="sdp-pdf-intro-badge">JAIN</div>
              </div>

              <div className="sdp-pdf-intro-body">
                <p>
                  As a result of these measures to improve academic performance, there is an incremental growth from entry to completion of the course.
                  Management students are mentored by the faculty to develop case studies of incubated companies. Similarly, students from other streams
                  are mentored to enhance creativity, develop research attitude, attain technical skills and many other skills needed for career and higher education.
                </p>
                <p>
                  Overall, it has been found that the students have gained confidence, personal insights, better understanding of concepts and improved their communication skills.
                </p>

                <h3>Objectives</h3>
                <ul className="sdp-pdf-intro-list">
                  <li>To monitor students regularly and discipline in all aspects</li>
                  <li>To improve Teacher-Student Relationship</li>
                  <li>To provide holistic outlook to life</li>
                  <li>To give guidance to choose career, progress to higher education and lead quality life</li>
                  <li>To improve stakeholder participation by arranging Parent Teacher meetings</li>
                </ul>

                <h3>The Context that initiated mentorship</h3>
                <p>
                  The University established a robust mentor-mentee program with the goal of instilling discipline, punctuality, and motivation in students
                  to help them align with their career aspirations. The university also utilizes a Counselling and Mentorship Record (CMR) to track student progress.
                  The mentorship system is designed to tackle conflicting attitudes and unhealthy habits while promoting improved student learning methods.
                </p>
              </div>
            </div>
          </div>
          <div className="sdp-pdf-intro-3" aria-hidden="true">
            <div className="sdp-pdf-intro-card">
              <div className="sdp-pdf-intro-header">
                <div className="sdp-pdf-intro-brand">
                  <img className="sdp-pdf-intro-logo" src={MENTEE_TRACKER_LOGO_URL} alt="" />
                  <div className="sdp-pdf-intro-brandtext">
                    <div className="sdp-pdf-intro-university">JAIN (Deemed-to-be University)</div>
                    <div className="sdp-pdf-intro-sub">Guidelines & Impact</div>
                  </div>
                </div>
                <div className="sdp-pdf-intro-badge">JAIN</div>
              </div>

              <div className="sdp-pdf-intro-body">
                <h3>Guidelines</h3>
                <ul className="sdp-pdf-intro-list">
                  <li>Each faculty member is a mentor for a group of 18 to 20 students.</li>
                  <li>Each student is made to fill a form which contains all the personal and academic details.</li>
                  <li>
                    The mentor undertakes counseling for the students with respect to academics, personal issues, career and emotional issues and helps in their
                    overall development.
                  </li>
                  <li>
                    Participation in activities and prizes won are documented. General health condition and major health issues if any are also discussed and
                    feedback on improvement across parameters is taken in the next meeting.
                  </li>
                  <li>
                    The mentor discusses with the student curricular, co-curricular and extra-curricular activities. Performance in academics and attendance
                    are given major focus and suggestions are given for improvement.
                  </li>
                  <li>A comparative analysis is made in the next meeting to note the progress.</li>
                </ul>

                <h3>Impact</h3>
                <ul className="sdp-pdf-intro-list">
                  <li>The percentage of attendance of students has increased considerably.</li>
                  <li>Marked improvement in student-teacher relationship.</li>
                  <li>Improvement in academic performance of students.</li>
                </ul>
              </div>
            </div>
          </div>
          <div className="sdp-pdf-outcome" aria-hidden="true">
            <div className="sdp-pdf-intro-card">
              <div className="sdp-pdf-intro-header">
                <div className="sdp-pdf-intro-brand">
                  <img className="sdp-pdf-intro-logo" src={MENTEE_TRACKER_LOGO_URL} alt="" />
                  <div className="sdp-pdf-intro-brandtext">
                    <div className="sdp-pdf-intro-university">JAIN (Deemed-to-be University)</div>
                    <div className="sdp-pdf-intro-sub">Outcome & Self-Reflection</div>
                  </div>
                </div>
              </div>

              <div className="sdp-pdf-intro-body">
                <h3>Outcome of the Mentoring Process</h3>
                <p>Outcome of the mentoring process:</p>
                <div className="sdp-pdf-outcome-box sdp-pdf-outcome-large"></div>

                <h3>Self-Reflection</h3>
                <p>Self-reflection on personal and academic growth throughout the mentorship:</p>
                <div className="sdp-pdf-outcome-box sdp-pdf-outcome-large"></div>

                <div className="sdp-pdf-outcome-row">
                  <div className="sdp-pdf-outcome-field">
                    <span>Date:</span>
                    <div className="sdp-pdf-outcome-line"></div>
                  </div>
                </div>

                <div className="sdp-pdf-outcome-row sdp-pdf-outcome-row--sign">
                  <div className="sdp-pdf-outcome-field">
                    <span>Signature of the Mentor:</span>
                    <div className="sdp-pdf-outcome-line"></div>
                  </div>
                  <div className="sdp-pdf-outcome-field">
                    <span>Signature of the Mentee:</span>
                    <div className="sdp-pdf-outcome-line"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="sdp-pdf-body">
            {ProfileSection}
          {/* Student Report (same as student side) */}
          <div className="sdp-section">
            <h2 className="sdp-section-title">
              <FaChartLine /> Student Analysis Report
            </h2>
            {swotLoading && (
              <div className="report-loading">
                <div className="loading-spinner"></div>
                <p>Loading report...</p>
              </div>
            )}
            {!swotLoading && !swotError && (!swotReport || Object.keys(swotReport).length === 0) && (
              <div className="report-empty">
                <div className="empty-icon">📊</div>
                <h3>No Report Available</h3>
                <p>SWOT analysis report is not available yet for this student.</p>
              </div>
            )}
            {!swotLoading && !swotError && swotReport && Object.keys(swotReport).length > 0 && (
              <div className="report-page" style={{ padding: 0, minHeight: 'auto' }}>
                <div className="swot-section">
                  <h2 className="section-title">SWOT Analysis</h2>
                  <div className="swot-grid">
                    <div className="swot-card strengths">
                      <div className="card-header">
                        <div className="card-icon">💪</div>
                        <h3>Strengths</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.strengths || 'No strengths identified yet.'}</p>
                      </div>
                    </div>
                    <div className="swot-card opportunities">
                      <div className="card-header">
                        <div className="card-icon">🎯</div>
                        <h3>Opportunities</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.opportunities || 'No opportunities identified yet.'}</p>
                      </div>
                    </div>
                    <div className="swot-card weaknesses">
                      <div className="card-header">
                        <div className="card-icon">⚠️</div>
                        <h3>Weaknesses</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.weaknesses || 'No weaknesses identified yet.'}</p>
                      </div>
                    </div>
                    <div className="swot-card threats">
                      <div className="card-header">
                        <div className="card-icon">🚨</div>
                        <h3>Threats</h3>
                      </div>
                      <div className="card-content">
                        <p>{swotReport.threats || 'No threats identified yet.'}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="additional-section">
                  <h2 className="section-title">Personal Insights</h2>
                  <div className="insights-grid">
                    {swotReport.professional_aspirations && (
                      <div className="insight-card">
                        <div className="insight-header">
                          <div className="insight-icon">🎯</div>
                          <h3>Professional Aspirations</h3>
                        </div>
                        <p>{swotReport.professional_aspirations}</p>
                      </div>
                    )}
                    {swotReport['hobbies/interests'] && (
                      <div className="insight-card">
                        <div className="insight-header">
                          <div className="insight-icon">🎨</div>
                          <h3>Hobbies & Interests</h3>
                        </div>
                        <p>{swotReport['hobbies/interests']}</p>
                      </div>
                    )}
                    {swotReport.detailed_analysis && (
                      <div className="insight-card">
                        <div className="insight-header">
                          <div className="insight-icon">📊</div>
                          <h3>Detailed Analysis</h3>
                        </div>
                        <p>{swotReport.detailed_analysis}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="sdp-section sdp-academic-section">
            <h2 className="sdp-section-title">
              <FaGraduationCap /> Academic Performance
            </h2>
            {academic_performance.secondary_marksheets &&
              Object.keys(academic_performance.secondary_marksheets).length > 0 && (
                <div className="sdp-secondary-marksheets">
                  <h3>10th & 12th Marksheets</h3>
                  <div className="sdp-marksheet-list">
                    {[10, 12].map((std) => {
                      const info = academic_performance.secondary_marksheets[std];
                      if (!info) return null;
                      return (
                        <div key={std} className="sdp-marksheet-item">
                          <span className="sdp-marksheet-label">{std}th Standard</span>
                          {info.uploaded_at && (
                            <span className="sdp-marksheet-date">
                              Uploaded: {formatDate(info.uploaded_at)}
                            </span>
                          )}
                          {info.marksheet_view_url && (
                            <button
                              className="sdp-view-btn"
                              onClick={() => window.open(info.marksheet_view_url, '_blank')}
                            >
                              <FaEye /> View
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            {academic_performance.semesters &&
              Object.keys(academic_performance.semesters).length > 0 ? (
                <div className="sdp-semesters">
                  {Object.entries(academic_performance.semesters)
                    .sort(([a], [b]) => Number(a) - Number(b))
                    .map(([sem, data]) => {
                      const hasRows = data.rows && data.rows.length > 0;
                      const hasMarksheet = data.marksheet && data.marksheet.marksheet_url;
                      if (!hasRows && !hasMarksheet) return null;
                      return (
                        <div key={sem} className="sdp-semester-card">
                          <div className="sdp-semester-header">
                            <span className="sdp-semester-badge">
                              {SEM_LABELS[Number(sem) - 1] || `Semester ${sem}`}
                            </span>
                            {hasRows && (
                              <span className="sdp-course-count">
                                {data.rows.length} {data.rows.length === 1 ? 'course' : 'courses'}
                              </span>
                            )}
                          </div>
                          {hasRows && (
                            <table className="sdp-grades-table">
                              <thead>
                                <tr>
                                  <th>Course</th>
                                  <th>Grade</th>
                                  <th>Attendance</th>
                                </tr>
                              </thead>
                              <tbody>
                                {data.rows.map((row, idx) => (
                                  <tr key={row.id || idx}>
                                    <td>{row.course}</td>
                                    <td>
                                      <span className={`sdp-grade sdp-grade-${(row.grade || '').charAt(0).toUpperCase()}`}>
                                        {row.grade || 'N/A'}
                                      </span>
                                    </td>
                                    <td>{row.overall_attendance || 'N/A'}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          )}
                          {hasMarksheet && (
                            <div className="sdp-semester-marksheet">
                              <FaFilePdf className="sdp-pdf-icon" />
                              <span>Marksheet Available</span>
                              {data.marksheet.uploaded_at && (
                                <span className="sdp-marksheet-date">
                                  ({formatDate(data.marksheet.uploaded_at)})
                                </span>
                              )}
                              <button
                                className="sdp-view-btn"
                                onClick={() => window.open(data.marksheet.marksheet_view_url, '_blank')}
                              >
                                <FaEye /> View
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                </div>
              ) : (
                <div className="sdp-empty-state">
                  <FaGraduationCap className="sdp-empty-icon" />
                  <p>No academic performance data available yet.</p>
                </div>
              )}
          </div>

          {/* Forms */}
          <div className="sdp-section sdp-forms-section">
            <h2 className="sdp-section-title">
              <FaClipboardList /> Forms Status
            </h2>
            <div className="sdp-forms-grid">
              <div className={`sdp-form-card ${forms_status.psychometric.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.psychometric.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>Psychometric Form</h3>
                  <p className="sdp-form-status">
                    {forms_status.psychometric.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.psychometric.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.psychometric.submitted_at)}
                    </p>
                  )}
                </div>
              </div>
              <div className={`sdp-form-card ${forms_status.swot.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.swot.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>SWOT Analysis</h3>
                  <p className="sdp-form-status">
                    {forms_status.swot.completed
                      ? (forms_status.swot.has_analysis ? 'Generated' : 'Completed')
                      : 'Not Generated'}
                  </p>
                </div>
              </div>
              <div className={`sdp-form-card ${forms_status.mca.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.mca.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>MCA Assessment</h3>
                  <p className="sdp-form-status">
                    {forms_status.mca.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.mca.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.mca.submitted_at)}
                    </p>
                  )}
                </div>
              </div>
              <div className={`sdp-form-card ${forms_status.pf16.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.pf16.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>16PF Form</h3>
                  <p className="sdp-form-status">
                    {forms_status.pf16.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.pf16.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.pf16.submitted_at)}
                    </p>
                  )}
                </div>
              </div>
              <div className={`sdp-form-card ${forms_status.ibp.completed ? 'completed' : 'pending'}`}>
                <div className="sdp-form-icon">
                  {forms_status.ibp.completed ? <FaCheck /> : <FaTimes />}
                </div>
                <div className="sdp-form-info">
                  <h3>IBP Form</h3>
                  <p className="sdp-form-status">
                    {forms_status.ibp.completed ? 'Completed' : 'Not Submitted'}
                  </p>
                  {forms_status.ibp.submitted_at && (
                    <p className="sdp-form-date">
                      Submitted: {formatDate(forms_status.ibp.submitted_at)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Activities */}
          <div className="sdp-section sdp-activities-section">
            <h2 className="sdp-section-title">
              <FaTasks /> Activities Overview
            </h2>
            <div className="sdp-activity-stats">
              <div className="sdp-activity-stat-card total">
                <div className="sdp-activity-stat-icon"><FaTasks /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">{activities.length}</span>
                  <span className="sdp-activity-stat-label">Total Activities</span>
                </div>
              </div>
              <div className="sdp-activity-stat-card approved">
                <div className="sdp-activity-stat-icon"><FaCheck /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">
                    {activities.filter(a => (a.status || '').toLowerCase() === 'approved').length}
                  </span>
                  <span className="sdp-activity-stat-label">Approved</span>
                </div>
              </div>
              <div className="sdp-activity-stat-card pending">
                <div className="sdp-activity-stat-icon"><FaClock /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">
                    {activities.filter(a => (a.status || '').toLowerCase() === 'pending' || !a.status).length}
                  </span>
                  <span className="sdp-activity-stat-label">Pending</span>
                </div>
              </div>
              <div className="sdp-activity-stat-card rejected">
                <div className="sdp-activity-stat-icon"><FaTimes /></div>
                <div className="sdp-activity-stat-info">
                  <span className="sdp-activity-stat-value">
                    {activities.filter(a => (a.status || '').toLowerCase() === 'rejected').length}
                  </span>
                  <span className="sdp-activity-stat-label">Rejected</span>
                </div>
              </div>
            </div>
            {activities.length > 0 ? (
              <div className="sdp-activities-table-container">
                <table className="sdp-activities-table">
                  <thead>
                    <tr>
                      <th className="th-id">Activity ID</th>
                      <th className="th-activity">Activity</th>
                      <th className="th-term">Term Type</th>
                      <th className="th-deadline">Deadline</th>
                      <th className="th-progress">Progress</th>
                      <th className="th-status">Status</th>
                      <th className="th-actions">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activities.map((activity, index) => (
                      <tr
                        key={activity.id}
                        className={`${index % 2 === 0 ? 'row-even' : 'row-odd'} ${
                          (activity.status || '').toLowerCase() === 'rejected' ? 'row-rejected' : ''
                        }`}
                      >
                        <td className="td-id">
                          <span className="activity-id-badge">{activity.id}</span>
                        </td>
                        <td className="td-activity">
                          <div className="activity-info">
                            <span className="activity-name">{activity.activity}</span>
                            {activity.requested_by && (
                              <span className="activity-requested-by">
                                Requested by: <strong>{activity.requested_by}</strong>
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="td-term">
                          <span className={`term-badge ${(activity.duration_type || '').toLowerCase().replace(' ', '-')}`}>
                            {activity.duration_type || 'N/A'}
                          </span>
                        </td>
                        <td className="td-deadline">
                          <div className="deadline-info">
                            <FaCalendarAlt className="deadline-icon" />
                            <span>{formatDate(activity.deadline)}</span>
                          </div>
                        </td>
                        <td className="td-progress">
                          {activity.percentage !== null ? (
                            <div className="progress-container">
                              <div className="progress-bar-wrapper">
                                <div
                                  className={`progress-bar-fill ${
                                    activity.percentage >= 100 ? 'complete' :
                                    activity.percentage >= 50 ? 'half' : 'low'
                                  }`}
                                  style={{ width: `${Math.min(activity.percentage, 100)}%` }}
                                ></div>
                              </div>
                              <span className="progress-text">{activity.percentage}%</span>
                            </div>
                          ) : (
                            <span className="no-progress">—</span>
                          )}
                        </td>
                        <td className="td-status">
                          <span className={`status-pill ${(activity.status || 'pending').toLowerCase()}`}>
                            {activity.status === 'Approved' && <FaCheck />}
                            {activity.status === 'Rejected' && <FaTimes />}
                            {(!activity.status || activity.status === 'Pending') && <FaClock />}
                            {activity.status || 'Pending'}
                          </span>
                        </td>
                        <td className="td-actions">
                          <div className="action-buttons">
                            {activity.proof_url && (
                              <a
                                href={activity.proof_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="action-btn view-proof"
                                title="View Proof"
                              >
                                <FaEye />
                              </a>
                            )}
                            {activity.remarks && (
                              <button
                                className="action-btn view-remarks"
                                title={activity.remarks}
                                onClick={() => alert(`Remarks: ${activity.remarks}`)}
                              >
                                💬
                              </button>
                            )}
                            {activity.rejection_reason && (
                              <button
                                className="action-btn view-rejection"
                                title={`Rejection Reason: ${activity.rejection_reason}`}
                                onClick={() => alert(`Rejection Reason: ${activity.rejection_reason}`)}
                              >
                                ⚠️
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaTasks className="sdp-empty-icon" />
                <p>No activities assigned yet.</p>
              </div>
            )}
          </div>

          {/* Student Support (PDF: include both Timeline + Session Chains like tabs) */}
          <div className="sdp-section sdp-counseling-section">
            <div className="sdp-counseling-header">
              <h2 className="sdp-section-title">
                <FaComments /> Student Support Sessions ({counseling_sessions.length})
              </h2>
            </div>

            {/* Session Summary Stats */}
            {counseling_sessions.length > 0 && (
              <div className="sdp-support-stats">
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon total"><FaComments /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">{counseling_sessions.length}</span>
                    <span className="sdp-support-stat-label">Total Sessions</span>
                  </div>
                </div>
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon completed"><FaCheck /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">
                      {counseling_sessions.filter(s => s.status === 'completed').length}
                    </span>
                    <span className="sdp-support-stat-label">Completed</span>
                  </div>
                </div>
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon scheduled"><FaCalendarAlt /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">
                      {counseling_sessions.filter(s => s.status === 'scheduled').length}
                    </span>
                    <span className="sdp-support-stat-label">Scheduled</span>
                  </div>
                </div>
                <div className="sdp-support-stat-card">
                  <div className="sdp-support-stat-icon followup"><FaLink /></div>
                  <div className="sdp-support-stat-info">
                    <span className="sdp-support-stat-value">
                      {sessionChains?.chains?.length || 0}
                    </span>
                    <span className="sdp-support-stat-label">Session Chains</span>
                  </div>
                </div>
              </div>
            )}

            {counseling_sessions.length > 0 ? (
              <>
                {/* Timeline (always included in PDF) */}
                <div className="sdp-timeline">
                  {counseling_sessions.map((session) => (
                    <div
                      key={session.id}
                      className={`sdp-timeline-item ${session.parent_session_id ? 'is-followup' : ''}`}
                    >
                      <div
                        className={`sdp-timeline-marker ${session.outcome_status ? getOutcomeStatusClass(session.outcome_status) : ''}`}
                      ></div>
                      <div className="sdp-timeline-content">
                        <div className="sdp-session-header">
                          <div className="sdp-session-header-left">
                            <span className="sdp-session-id">#{session.counseling_id || session.id}</span>
                            <span className="sdp-session-date">
                              <FaCalendarAlt /> {formatDateTime(session.session_date)}
                            </span>
                          </div>
                          <div className="sdp-session-badges">
                            <span className={`sdp-status-badge ${getStatusColor(session.status)}`}>
                              {session.status}
                            </span>
                            {session.is_urgent && (
                              <span className="sdp-urgent-badge">Urgent</span>
                            )}
                            {session.parent_session_id && (
                              <span className="sdp-followup-badge">
                                <FaLink /> Follow-up
                              </span>
                            )}
                            {session.outcome_status && (
                              <span className={`sdp-outcome-badge ${getOutcomeStatusClass(session.outcome_status)}`}>
                                {getOutcomeStatusLabel(session.outcome_status)}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="sdp-session-details">
                          <div className="sdp-session-item">
                            <label><FaMapMarkerAlt /> Venue</label>
                            <span>{session.venue || 'N/A'}</span>
                          </div>
                          {session.parent_session_id && (
                            <div className="sdp-session-item chain-link">
                              <label><FaLink /> Parent Session</label>
                              <span>#{session.parent_session_id}</span>
                            </div>
                          )}
                          {session.reason && (
                            <div className="sdp-session-item full-width">
                              <label>Reason</label>
                              <span>{session.reason}</span>
                            </div>
                          )}
                          {session.outcome_notes && (
                            <div className="sdp-session-item full-width outcome-notes">
                              <label><FaChartLine /> Outcome Notes</label>
                              <span>{session.outcome_notes}</span>
                            </div>
                          )}
                          {session.followup_date && (
                            <div className="sdp-session-item followup-info">
                              <label><FaCalendarAlt /> Follow-up Date</label>
                              <span>
                                {formatDate(session.followup_date)}
                                {session.followup_scheduled && <span className="scheduled-badge"> ✓ Scheduled</span>}
                              </span>
                            </div>
                          )}
                          {session.notes && (
                            <div className="sdp-session-item full-width">
                              <label>Notes</label>
                              <span>{session.notes}</span>
                            </div>
                          )}
                          {session.feedback && (
                            <div className="sdp-session-item full-width">
                              <label>Feedback</label>
                              <span>{session.feedback}</span>
                            </div>
                          )}
                          {(session.student_rating || session.mentor_rating) && (
                            <div className="sdp-ratings">
                              {session.student_rating && (
                                <span>Student Rating: {'⭐'.repeat(session.student_rating)}</span>
                              )}
                              {session.mentor_rating && (
                                <span>Mentor Rating: {'⭐'.repeat(session.mentor_rating)}</span>
                              )}
                            </div>
                          )}
                          {session.referred_to_name && (
                            <div className="sdp-referral">
                              <label>Referred To</label>
                              <span>{session.referred_to_name} ({session.referred_to_contact || 'No contact'})</span>
                            </div>
                          )}
                          {session.google_meet_link && (
                            <a
                              href={session.google_meet_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="sdp-meet-link"
                            >
                              Join Google Meet <FaExternalLinkAlt />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Session Chains (also included in PDF) */}
                <div className="sdp-chains-container" style={{ marginTop: '1.5rem' }}>
                  {sessionChains && sessionChains.chains && sessionChains.chains.length > 0 ? (
                    sessionChains.chains.map((chain, chainIdx) => (
                      <div key={chain.original_session_id} className="sdp-chain-card">
                        <div className="sdp-chain-header">
                          <h3><FaLink /> Session Chain #{chainIdx + 1}</h3>
                          <span className="sdp-chain-info">
                            {chain.total_in_chain} {chain.total_in_chain === 1 ? 'session' : 'sessions'}
                          </span>
                        </div>
                        <div className="sdp-chain-timeline">
                          {chain.sessions.map((session, sessionIdx) => (
                            <div
                              key={session.counseling_id}
                              className={`sdp-chain-node ${session.is_followup ? 'is-followup' : 'is-original'}`}
                            >
                              <div className="sdp-chain-connector">
                                <div className={`sdp-chain-dot ${getOutcomeStatusClass(session.outcome_status)}`}></div>
                                {sessionIdx < chain.sessions.length - 1 && <div className="sdp-chain-line"></div>}
                              </div>
                              <div className="sdp-chain-content">
                                <div className="sdp-chain-session-header">
                                  <span className="sdp-chain-session-id">
                                    {session.is_followup && <FaLink className="followup-icon" />}
                                    #{session.counseling_id}
                                  </span>
                                  <span className={`sdp-mini-badge ${getStatusColor(session.status)}`}>
                                    {session.status}
                                  </span>
                                </div>
                                <div className="sdp-chain-session-details">
                                  <span className="sdp-chain-date">
                                    <FaCalendarAlt /> {formatDateTime(session.session_date)}
                                  </span>
                                  <span className="sdp-chain-venue">
                                    <FaMapMarkerAlt /> {session.venue}
                                  </span>
                                  {session.outcome_status && (
                                    <span className={`sdp-chain-outcome ${getOutcomeStatusClass(session.outcome_status)}`}>
                                      {getOutcomeStatusLabel(session.outcome_status)}
                                    </span>
                                  )}
                                </div>
                                {session.reason && (
                                  <p className="sdp-chain-reason">{session.reason}</p>
                                )}
                                {session.outcome_notes && (
                                  <p className="sdp-chain-notes"><strong>Notes:</strong> {session.outcome_notes}</p>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="sdp-empty-chains">
                      <FaLink className="sdp-empty-icon" />
                      <p>No session chains found.</p>
                      <span>Sessions with follow-ups will appear here as chains.</span>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="sdp-empty-state">
                <FaComments className="sdp-empty-icon" />
                <p>No student support sessions recorded.</p>
              </div>
            )}
          </div>

          {/* Meetings */}
          <div className="sdp-section sdp-meetings-section">
            <h2 className="sdp-section-title">
              <FaCalendarAlt /> Meetings ({meetings.length})
            </h2>
            {meetings.length > 0 ? (
              <div className="sdp-meetings-list">
                {meetings.map((meeting) => (
                  <div key={meeting.id} className="sdp-meeting-card">
                    <div className="sdp-meeting-header">
                      <span className="sdp-meeting-date">
                        <FaCalendarAlt /> {formatDateTime(meeting.meeting_date)}
                      </span>
                      <div className="sdp-meeting-badges">
                        <span className={`sdp-status-badge ${getStatusColor(meeting.status)}`}>
                          {meeting.status || 'Scheduled'}
                        </span>
                        {meeting.attendance && (
                          <span className={`sdp-attendance-badge ${getStatusColor(meeting.attendance)}`}>
                            {meeting.attendance}
                          </span>
                        )}
                        <span className="sdp-mode-badge">
                          {meeting.meeting_mode === 'online' ? '🌐 Online' : '🏢 Offline'}
                        </span>
                      </div>
                    </div>
                    <div className="sdp-meeting-details">
                      <div className="sdp-meeting-item">
                        <label><FaMapMarkerAlt /> Venue</label>
                        <span>{meeting.venue || 'N/A'}</span>
                      </div>
                      {meeting.duration && (
                        <div className="sdp-meeting-item">
                          <label><FaClock /> Duration</label>
                          <span>{meeting.duration} minutes</span>
                        </div>
                      )}
                      {meeting.agenda && (
                        <div className="sdp-meeting-item full-width">
                          <label>Agenda</label>
                          <span>{meeting.agenda}</span>
                        </div>
                      )}
                      {meeting.progress_notes && (
                        <div className="sdp-meeting-item full-width">
                          <label>Progress Notes</label>
                          <span>{meeting.progress_notes}</span>
                        </div>
                      )}
                      {meeting.google_meet_link && (
                        <a
                          href={meeting.google_meet_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="sdp-meet-link"
                        >
                          Join Google Meet <FaExternalLinkAlt />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaCalendarAlt className="sdp-empty-icon" />
                <p>No meetings scheduled yet.</p>
              </div>
            )}
          </div>

          {/* Attendance */}
          <div className="sdp-section sdp-attendance-section">
            <h2 className="sdp-section-title">
              <FaClipboardCheck /> Attendance Statistics
            </h2>
            {attendance && attendance.summary && (
              <div className="sdp-attendance-summary">
                <div className="sdp-stat-card sdp-stat-total">
                  <div className="sdp-stat-value">{attendance.summary.total_sessions}</div>
                  <div className="sdp-stat-label">Total Sessions</div>
                </div>
                <div className="sdp-stat-card sdp-stat-present">
                  <div className="sdp-stat-value">{attendance.summary.present}</div>
                  <div className="sdp-stat-label">Present</div>
                </div>
                <div className="sdp-stat-card sdp-stat-late">
                  <div className="sdp-stat-value">{attendance.summary.late}</div>
                  <div className="sdp-stat-label">Late</div>
                </div>
                <div className="sdp-stat-card sdp-stat-absent">
                  <div className="sdp-stat-value">{attendance.summary.absent}</div>
                  <div className="sdp-stat-label">Absent</div>
                </div>
                <div className="sdp-stat-card sdp-stat-percentage">
                  <div className="sdp-stat-value">{attendance.summary.attendance_percentage}%</div>
                  <div className="sdp-stat-label">Attendance Rate</div>
                </div>
              </div>
            )}
            <h3 className="sdp-subsection-title">Attendance History</h3>
            {attendance && attendance.records && attendance.records.length > 0 ? (
              <div className="sdp-attendance-list">
                {attendance.records.map((record) => (
                  <div key={record.id} className="sdp-attendance-card">
                    <div className="sdp-attendance-header">
                      <span className="sdp-attendance-session">{record.session_name}</span>
                      <span className={`sdp-status-badge ${
                        record.status === 'present' ? 'status-success' :
                        record.status === 'late' ? 'status-warning' : 'status-danger'
                      }`}>
                        {record.status === 'present' ? '✓ Present' :
                         record.status === 'late' ? '⏰ Late' : '✗ Absent'}
                      </span>
                    </div>
                    <div className="sdp-attendance-details">
                      <div className="sdp-attendance-item">
                        <label><FaCalendarAlt /> Date</label>
                        <span>{formatDateTime(record.session_date)}</span>
                      </div>
                      {record.location && (
                        <div className="sdp-attendance-item">
                          <label><FaMapMarkerAlt /> Location</label>
                          <span>{record.location}</span>
                        </div>
                      )}
                      <div className="sdp-attendance-item">
                        <label><FaClock /> Marked At</label>
                        <span>{formatDateTime(record.marked_at)}</span>
                      </div>
                      {record.notes && (
                        <div className="sdp-attendance-item full-width">
                          <label>Notes</label>
                          <span>{record.notes}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaClipboardCheck className="sdp-empty-icon" />
                <p>No attendance records found.</p>
              </div>
            )}
          </div>

          {/* Experiential Learning */}
          <div className="sdp-section sdp-experiential-section">
            <h2 className="sdp-section-title">
              <FaLightbulb /> Experiential Learning ({experiential_learning?.length || 0})
            </h2>
            <div className="sdp-exp-summary">
              <div className="sdp-exp-summary-card">
                <div className="sdp-exp-summary-icon">
                  <FaLightbulb />
                </div>
                <div className="sdp-exp-summary-info">
                  <span className="sdp-exp-summary-value">{experiential_learning?.length || 0}</span>
                  <span className="sdp-exp-summary-label">Total Learning Experiences</span>
                </div>
              </div>
            </div>
            {experiential_learning && experiential_learning.length > 0 ? (
              <div className="sdp-exp-grid">
                {experiential_learning.map((entry) => (
                  <div key={entry.id} className="sdp-exp-card">
                    <div className="sdp-exp-card-header">
                      <div className="sdp-exp-card-icon">
                        <FaLightbulb />
                      </div>
                      <div className="sdp-exp-card-title">
                        <h3>{entry.title}</h3>
                        <span className="sdp-exp-date">
                          <FaCalendarAlt /> {formatDate(entry.created_at)}
                        </span>
                      </div>
                    </div>
                    <div className="sdp-exp-card-body">
                      <div className="sdp-exp-description">
                        <label>Experience Details</label>
                        <p>{entry.detailed_explanation}</p>
                      </div>
                      {entry.proof_url && (
                        <div className="sdp-exp-proof">
                          <a
                            href={entry.proof_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="sdp-exp-proof-btn"
                          >
                            <FaEye /> View Proof/Certificate
                          </a>
                        </div>
                      )}
                    </div>
                    {entry.updated_at && entry.updated_at !== entry.created_at && (
                      <div className="sdp-exp-card-footer">
                        <span className="sdp-exp-updated">
                          Last updated: {formatDate(entry.updated_at)}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="sdp-empty-state">
                <FaLightbulb className="sdp-empty-icon" />
                <p>No experiential learning entries recorded yet.</p>
                <span className="sdp-empty-subtext">
                  The student hasn't added any learning experiences.
                </span>
              </div>
            )}
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDetailPage;
