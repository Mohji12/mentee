import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import './Counseling.css';
import FeedbackForm from './FeedbackForm';

// Hierarchical reason options: Category → Sub-reasons
const SUPPORT_REASON_HIERARCHY = {
    "Academic Support": [
        "Difficulty Understanding Subjects",
        "Poor Academic Performance",
        "Exam Preparation Guidance",
        "Project / Assignment Help",
        "Research Guidance",
        "Time Management for Studies"
    ],
    "Career & Professional Guidance": [
        "Career Confusion",
        "Higher Studies Planning",
        "Internship Guidance",
        "Resume Building",
        "Interview Preparation",
        "Skill Development Roadmap",
        "Industry Exposure"
    ],
    "Personal Development": [
        "Lack of Confidence",
        "Public Speaking Improvement",
        "Communication Skills",
        "Leadership Development",
        "Goal Setting Support",
        "Motivation Issues"
    ],
    "Emotional / Personal Challenges": [
        "Stress Management",
        "Anxiety About Future",
        "Work-Life Balance",
        "Family Pressure",
        "Relationship Issues",
        "Feeling Overwhelmed"
    ],
    "Skill & Growth Support": [
        "Technical Skill Improvement",
        "Soft Skill Development",
        "Entrepreneurship Guidance",
        "Innovation / Startup Ideas",
        "Networking Support"
    ],
    "Institutional / Administrative Help": [
        "Course Selection Confusion",
        "Academic Rules Clarification",
        "Scholarship Guidance",
        "Placement Process Queries"
    ],
    "General Mentorship": [
        "Need Regular Accountability",
        "Need Structured Growth Plan",
        "Need Long-Term Guidance",
        "Need Clarity & Direction"
    ],
    "Other": []  // Free text reason when selected
};

const SUPPORT_CATEGORIES = Object.keys(SUPPORT_REASON_HIERARCHY);
const OTHER_CATEGORY = 'Other';

const Counseling = () => {
    const { student_usn } = useParams();
    const [activeTab, setActiveTab] = useState('request');
    const [counselingData, setCounselingData] = useState({
        session_date: '',
        reason: '',
        is_urgent: false
    });
    const [reasonCategory, setReasonCategory] = useState('');
    const [reasonSub, setReasonSub] = useState('');
    const [reasonOtherText, setReasonOtherText] = useState('');
    const [sessions, setSessions] = useState([]);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [showFeedbackForm, setShowFeedbackForm] = useState(false);
    const [selectedSessionId, setSelectedSessionId] = useState(null);
    const [showIssuesModal, setShowIssuesModal] = useState(false);
    const [selectedSessionForIssues, setSelectedSessionForIssues] = useState(null);
    const getTodayDateStr = () => {
        const d = new Date();
        return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
    };
    const [issuesRows, setIssuesRows] = useState([{ issues_raised: '', date_issue_raised: '', resolution_details: '', date_resolution_provided: '' }]);
    const [issuesProofFile, setIssuesProofFile] = useState(null);
    const [issuesSubmitting, setIssuesSubmitting] = useState(false);

    useEffect(() => {
        fetchSessions();
        fetchStats();
    }, []);

    const fetchSessions = async () => {
        try {
            const token = sessionStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/student/${student_usn}/counseling/sessions`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setSessions(data);
            }
        } catch (error) {
            console.error('Error fetching sessions:', error);
        }
    };

    const fetchStats = async () => {
        try {
            const token = sessionStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/student/${student_usn}/counseling/stats`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        try {
            const token = sessionStorage.getItem('access_token');
            
            // Treat datetime-local value as Indian Standard Time (IST) and convert to UTC for storage
            let sessionDate;
            if (counselingData.session_date) {
                if (counselingData.session_date.includes('T') && counselingData.session_date.includes('Z')) {
                    sessionDate = counselingData.session_date;
                } else {
                    sessionDate = istToUtcISO(counselingData.session_date);
                }
            } else {
                throw new Error('Session date is required');
            }
            if (!reasonCategory) {
                setMessage('Please select a category for student support.');
                setLoading(false);
                return;
            }
            if (reasonCategory === OTHER_CATEGORY) {
                const trimmed = (reasonOtherText || '').trim();
                if (!trimmed) {
                    setMessage('Please enter the reason for student support.');
                    setLoading(false);
                    return;
                }
            } else if (!reasonSub) {
                setMessage('Please select a specific reason for student support.');
                setLoading(false);
                return;
            }
            const reasonText = reasonCategory === OTHER_CATEGORY
                ? `${OTHER_CATEGORY} → ${(reasonOtherText || '').trim()}`
                : `${reasonCategory} → ${reasonSub}`;
            const requestData = {
                ...counselingData,
                session_date: sessionDate,
                reason: reasonText
            };
            
            console.log('Sending request data:', requestData);
            
            const response = await fetch(`${API_BASE_URL}/student/${student_usn}/counseling/request`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const result = await response.json();
                setMessage('Student support session requested successfully!');
                setCounselingData({
                    session_date: '',
                    reason: '',
                    is_urgent: false
                });
                setReasonCategory('');
                setReasonSub('');
                setReasonOtherText('');
                fetchSessions();
                fetchStats();
            } else {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                setMessage(`Error: ${errorData.detail || 'Failed to request student support session'}`);
            }
        } catch (error) {
            setMessage('Error requesting student support session');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setCounselingData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    // Treat datetime-local value (YYYY-MM-DDTHH:mm) as IST and return ISO UTC string for API
    const istToUtcISO = (datetimeLocalStr) => {
        const s = String(datetimeLocalStr).trim();
        const [datePart, timePart] = s.split('T');
        if (!datePart || !timePart) return new Date(s).toISOString();
        const [y, m, d] = datePart.split('-').map(Number);
        const [hr, min] = timePart.split(':').map(Number);
        const istOffsetMs = (5 * 60 + 30) * 60 * 1000; // IST = UTC+5:30
        const asUtcMs = Date.UTC(y, m - 1, d, hr, min || 0, 0, 0);
        const utcMs = asUtcMs - istOffsetMs;
        return new Date(utcMs).toISOString();
    };

    // API returns session_date as UTC (naive, no Z) - parse as UTC then show in IST
    const parseUtc = (dateString) => {
        if (!dateString) return null;
        const s = String(dateString).trim();
        if (s.endsWith('Z') || /[+-]\d{2}:?\d{2}$/.test(s)) return new Date(s);
        return new Date(s + 'Z');
    };
    const formatDate = (dateString) => {
        const d = parseUtc(dateString);
        if (!d || isNaN(d.getTime())) return '';
        return d.toLocaleString('en-IN', {
            timeZone: 'Asia/Kolkata',
            dateStyle: 'medium',
            timeStyle: 'short',
            hour12: true
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'scheduled': return '#4CAF50';
            case 'completed': return '#2196F3';
      case 'referred': return '#9C27B0';
            case 'cancelled': return '#F44336';
            case 'rescheduled': return '#FF9800';
            default: return '#757575';
        }
    };

    const handleFeedbackClick = (sessionId) => {
        setSelectedSessionId(sessionId);
        setShowFeedbackForm(true);
    };

    const handleIssuesClick = async (session) => {
        setSelectedSessionForIssues(session);
        setShowIssuesModal(true);
        setIssuesProofFile(null);
        const today = getTodayDateStr();
        setIssuesRows([{ issues_raised: '', date_issue_raised: today, resolution_details: '', date_resolution_provided: '' }]);
        try {
            const token = sessionStorage.getItem('access_token');
            const res = await fetch(`${API_BASE_URL}/student/${student_usn}/counseling/sessions/${session.counseling_id}/issues-resolution`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                if (data && data.length > 0) {
                    setIssuesRows(data.map(r => ({
                        issues_raised: r.issues_raised || '',
                        date_issue_raised: r.date_issue_raised || today,
                        resolution_details: r.resolution_details || '',
                        date_resolution_provided: r.date_resolution_provided || ''
                    })));
                }
            }
        } catch (e) {
            console.error('Failed to load issues/resolution', e);
        }
    };

    const handleIssuesClose = () => {
        setShowIssuesModal(false);
        setSelectedSessionForIssues(null);
        setIssuesProofFile(null);
        fetchSessions();
    };

    const addIssuesRow = () => {
        setIssuesRows(prev => [...prev, { issues_raised: '', date_issue_raised: getTodayDateStr(), resolution_details: '', date_resolution_provided: '' }]);
    };

    const updateIssuesRow = (index, field, value) => {
        setIssuesRows(prev => prev.map((row, i) => i === index ? { ...row, [field]: value } : row));
    };

    const removeIssuesRow = (index) => {
        if (issuesRows.length <= 1) return;
        setIssuesRows(prev => prev.filter((_, i) => i !== index));
    };

    const handleIssuesSubmit = async (e) => {
        e.preventDefault();
        if (!selectedSessionForIssues) return;
        const valid = issuesRows.filter(r => r.issues_raised.trim() && r.date_issue_raised);
        if (valid.length === 0) {
            setMessage('Add at least one row with Issues Raised and Date of Issue raised.');
            return;
        }
        setIssuesSubmitting(true);
        setMessage('');
        try {
            const token = sessionStorage.getItem('access_token');
            const formData = new FormData();
            formData.append('rows', JSON.stringify(valid.map(r => ({
                issues_raised: r.issues_raised.trim(),
                date_issue_raised: r.date_issue_raised,
                resolution_details: null,
                date_resolution_provided: null
            }))));
            if (issuesProofFile) formData.append('file', issuesProofFile);
            const res = await fetch(`${API_BASE_URL}/student/${student_usn}/counseling/sessions/${selectedSessionForIssues.counseling_id}/issues-resolution`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            if (res.ok) {
                handleIssuesClose();
                setMessage('Issues & Resolution saved successfully.');
            } else {
                const err = await res.json();
                setMessage(Array.isArray(err.detail) ? (err.detail[0]?.msg || 'Failed to save.') : (err.detail || 'Failed to save.'));
            }
        } catch (e) {
            setMessage('Failed to save.');
        } finally {
            setIssuesSubmitting(false);
        }
    };

    const formatDateDDMMMYYYY = (dateStr) => {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const day = d.getDate();
        const month = months[d.getMonth()];
        const year = d.getFullYear();
        return `${day.toString().padStart(2,'0')}-${month}-${year}`;
    };

    const getIssueResolutionRowLabel = (rowType) => {
        const labels = { issue_raised: 'Issue Raised by Mentor', details_of_resolution: 'Details of Resolution', resolution: 'Resolution' };
        return labels[rowType] || rowType || '';
    };

    const handleFeedbackClose = () => {
        setShowFeedbackForm(false);
        setSelectedSessionId(null);
    };

    const handleFeedbackSuccess = () => {
        fetchSessions();
        fetchStats();
    };

    return (
        <div className="counseling-container">
            <div className="counseling-header">
                <h1>Student Support</h1>
                <div className="stats-grid">
                    <div className="stat-card">
                        <h3>Total Sessions</h3>
                        <p>{stats.total_sessions || 0}</p>
                    </div>
                    <div className="stat-card">
                        <h3>Scheduled</h3>
                        <p>{stats.scheduled_sessions || 0}</p>
                    </div>
                    <div className="stat-card">
                        <h3>Completed</h3>
                        <p>{stats.completed_sessions || 0}</p>
                    </div>
                    <div className="stat-card">
                        <h3>Upcoming</h3>
                        <p>{stats.upcoming_sessions || 0}</p>
                    </div>
                </div>
            </div>

            <div className="counseling-tabs">
                <button 
                    className={`tab-button ${activeTab === 'request' ? 'active' : ''}`}
                    onClick={() => setActiveTab('request')}
                >
                    Request Session
                </button>
                <button 
                    className={`tab-button ${activeTab === 'sessions' ? 'active' : ''}`}
                    onClick={() => setActiveTab('sessions')}
                >
                    My Sessions
                </button>
            </div>

            {activeTab === 'request' && (
                <div className="counseling-form-container">
                    <h2>Request Student Support Session</h2>
                    <form onSubmit={handleSubmit} className="counseling-form">
                        <div className="form-group">
                            <label htmlFor="session_date">Preferred Date & Time</label>
                            <input
                                type="datetime-local"
                                id="session_date"
                                name="session_date"
                                value={counselingData.session_date}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="reason_category">Reason for Student Support</label>
                            <select
                                id="reason_category"
                                value={reasonCategory}
                                onChange={(e) => {
                                    setReasonCategory(e.target.value);
                                    setReasonSub('');
                                    setReasonOtherText('');
                                }}
                                required
                            >
                                <option value="">Select category</option>
                                {SUPPORT_CATEGORIES.map((cat) => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                            {reasonCategory === OTHER_CATEGORY ? (
                                <div className="form-group" style={{ marginTop: '8px' }}>
                                    <label htmlFor="reason_other_text">Please specify the reason for student support</label>
                                    <input
                                        id="reason_other_text"
                                        type="text"
                                        value={reasonOtherText}
                                        onChange={(e) => setReasonOtherText(e.target.value)}
                                        placeholder="Enter your reason..."
                                        required
                                        className="reason-other-input"
                                    />
                                </div>
                            ) : reasonCategory && SUPPORT_REASON_HIERARCHY[reasonCategory].length > 0 && (
                                <select
                                    id="reason_sub"
                                    value={reasonSub}
                                    onChange={(e) => setReasonSub(e.target.value)}
                                    required
                                    style={{ marginTop: '8px' }}
                                >
                                    <option value="">Select specific reason</option>
                                    {SUPPORT_REASON_HIERARCHY[reasonCategory].map((sub) => (
                                        <option key={sub} value={sub}>{sub}</option>
                                    ))}
                                </select>
                            )}
                        </div>

                        <div className="form-group checkbox-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="is_urgent"
                                    checked={counselingData.is_urgent}
                                    onChange={handleInputChange}
                                />
                                <span className="checkmark"></span>
                                This is an urgent session
                            </label>
                        </div>

                        {message && (
                            <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
                                {message}
                            </div>
                        )}

                        <button type="submit" className={`submit-button ${loading ? 'loading' : ''}`} disabled={loading}>
                            {loading ? 'Requesting...' : 'Request Session'}
                        </button>
                    </form>
                </div>
            )}

            {activeTab === 'sessions' && (
                <div className="sessions-container">
                    <h2>My Student Support Sessions</h2>
                    {sessions.length === 0 ? (
                        <div className="no-sessions">
                            <p>No student support sessions found.</p>
                        </div>
                    ) : (
                        <div className="sessions-list">
                            {sessions.map((session) => (
                                <div key={session.id} className="session-card">
                                    <div className="session-header">
                                        <h3>Session #{session.counseling_id}</h3>
                                        <span 
                                            className="status-badge"
                                            style={{ backgroundColor: getStatusColor(session.status) }}
                                        >
                                            {session.status.toUpperCase()}
                                        </span>
                                        {session.is_urgent && (
                                            <span className="urgent-badge">URGENT</span>
                                        )}
                                    </div>
                                    
                                    <div className="session-details">
                                        <div className="detail-row">
                                            <strong>Date & Time:</strong>
                                            <span>{formatDate(session.session_date)}</span>
                                        </div>
                                        <div className="detail-row">
                                            <strong>Reason:</strong>
                                            <span>{session.reason}</span>
                                        </div>
                                        {session.mentor_name && (
                                            <div className="detail-row">
                                                <strong>Mentor:</strong>
                                                <span>{session.mentor_name}</span>
                                            </div>
                                        )}
                                        {session.status === 'referred' && (session.referred_to_name || session.referred_to_contact) && (
                                            <div className="detail-row referred-info">
                                                <strong>Referred to:</strong>
                                                <span>{session.referred_to_name || ''}{session.referred_to_contact ? ` (${session.referred_to_contact})` : ''}</span>
                                            </div>
                                        )}
                                        {session.google_meet_link && (
                                            <div className="detail-row">
                                                <strong>Meeting Link:</strong>
                                                <div className="meet-link-container">
                                                    <a 
                                                        href={session.google_meet_link} 
                                                        target="_blank" 
                                                        rel="noopener noreferrer"
                                                        className="meet-link"
                                                    >
                                                        Join Meeting
                                                    </a>
                                                    <small className="meet-note">
                                                        Note: This is a generated link. If the meeting doesn't exist, please contact your mentor.
                                                    </small>
                                                </div>
                                            </div>
                                        )}
                                        {session.notes && (
                                            <div className="detail-row">
                                                <strong>Mentor Notes:</strong>
                                                <span>{session.notes}</span>
                                            </div>
                                        )}
                                        {session.feedback && (
                                            <div className="detail-row">
                                                <strong>Feedback:</strong>
                                                <span>{session.feedback}</span>
                                            </div>
                                        )}
                                        {session.student_feedback && (
                                            <div className="detail-row">
                                                <strong>Your Feedback:</strong>
                                                <span>{session.student_feedback}</span>
                                                <div className="rating-display">
                                                    {'⭐'.repeat(session.student_rating || 0)} ({session.student_rating}/5)
                                                </div>
                                                {session.student_feedback_file_url && (
                                                    <div style={{ marginTop: '0.5rem' }}>
                                                        <a href={session.student_feedback_file_url} target="_blank" rel="noopener noreferrer">View / Download your file</a>
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* Issue raised & resolution – read-only tabular feedback */}
                                        {(session.issue_resolution_feedback && session.issue_resolution_feedback.length > 0) && (
                                            <div className="issue-resolution-feedback-section">
                                                <div className="detail-row" style={{ marginBottom: '0.5rem' }}>
                                                    <strong>Issue raised & resolution</strong>
                                                </div>
                                                <div className="issue-resolution-feedback-table-wrap">
                                                    <table className="issue-resolution-feedback-table">
                                                        <thead>
                                                            <tr>
                                                                <th>Description</th>
                                                                <th>Date</th>
                                                                <th>Status</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {session.issue_resolution_feedback.map((row, idx) => (
                                                                <tr key={row.row_type || idx}>
                                                                    <td>
                                                                        <span className="feedback-row-label">{getIssueResolutionRowLabel(row.row_type)}</span>
                                                                        {row.description && <div className="feedback-row-desc">{row.description}</div>}
                                                                    </td>
                                                                    <td>{row.feedback_date ? formatDateDDMMMYYYY(row.feedback_date) : '–'}</td>
                                                                    <td><span className="status-badge small" style={{ backgroundColor: row.status === 'Close' ? '#28a745' : '#ffc107', color: '#000' }}>{row.status || '–'}</span></td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {(session.status === 'completed' || session.status === 'referred') && (
                                        <div className="session-actions">
                                            <button 
                                                className="feedback-button"
                                                onClick={() => handleFeedbackClick(session.counseling_id)}
                                            >
                                                {session.student_feedback ? 'View Feedback' : 'Submit Feedback'}
                                            </button>
                                            <button 
                                                className="issues-resolution-button"
                                                onClick={() => handleIssuesClick(session)}
                                            >
                                                Details of Issues Raised & Resolved
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {showFeedbackForm && (
                <FeedbackForm
                    counselingId={selectedSessionId}
                    studentUsn={student_usn}
                    onClose={handleFeedbackClose}
                    onSuccess={handleFeedbackSuccess}
                />
            )}

            {showIssuesModal && selectedSessionForIssues && (
                <div className="counseling-modal-overlay" onClick={() => setShowIssuesModal(false)}>
                    <div className="counseling-modal issues-modal" onClick={e => e.stopPropagation()}>
                        <div className="counseling-modal-header">
                            <h3>Details of Issues Raised & Resolved</h3>
                            <button type="button" className="modal-close" onClick={handleIssuesClose} aria-label="Close">&times;</button>
                        </div>
                        <form onSubmit={handleIssuesSubmit}>
                            <p className="issues-modal-hint">
                                Session #{selectedSessionForIssues.counseling_id}. Add at least one row.
                                {selectedSessionForIssues.status === 'referred'
                                    ? ' Describe what happened in your counseling session and upload any proof if available.'
                                    : ' Date of issue is set automatically when you add a row. Resolution will be filled by your mentor.'}
                            </p>
                            <div className="issues-table-wrap">
                                <table className="issues-resolution-table">
                                    <thead>
                                        <tr>
                                            <th>S. No</th>
                                            <th>Issues Raised</th>
                                            <th>Date of Issue raised</th>
                                            <th>Details of Resolution Provided</th>
                                            <th>Date of Resolution provided</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {issuesRows.map((row, idx) => (
                                            <tr key={idx}>
                                                <td>{idx + 1}</td>
                                                <td>
                                                    <input type="text" value={row.issues_raised} onChange={e => updateIssuesRow(idx, 'issues_raised', e.target.value)} placeholder="Issues raised" />
                                                </td>
                                                <td>
                                                    <input type="date" value={row.date_issue_raised} onChange={e => updateIssuesRow(idx, 'date_issue_raised', e.target.value)} title="Auto-filled with today; you can change if needed" />
                                                </td>
                                                <td className="resolution-readonly">{row.resolution_details || '— To be filled by mentor'}</td>
                                                <td className="resolution-readonly">{row.date_resolution_provided ? formatDateDDMMMYYYY(row.date_resolution_provided) : '—'}</td>
                                                <td>
                                                    <button type="button" className="remove-row-btn" onClick={() => removeIssuesRow(idx)} disabled={issuesRows.length <= 1}>Remove</button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                            <button type="button" className="add-row-btn" onClick={addIssuesRow}>Add row</button>
                            <div className="issues-proof-upload">
                                <label className="proof-upload-label">Proof of work done after session (optional):</label>
                                {selectedSessionForIssues.student_issues_proof_file_url ? (
                                    <div className="proof-uploaded">
                                        <a href={selectedSessionForIssues.student_issues_proof_file_url} target="_blank" rel="noopener noreferrer" className="feedback-file-link">View / Download uploaded proof</a>
                                        <span className="proof-hint"> — Upload a new file below to replace.</span>
                                    </div>
                                ) : null}
                                <input type="file" accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.gif,.webp" onChange={e => { setIssuesProofFile(e.target.files?.[0] || null); setMessage(''); }} className="proof-file-input" />
                                {issuesProofFile && <span className="file-name">{issuesProofFile.name}</span>}
                            </div>
                            {selectedSessionForIssues.mentor_resolution_proof_file_url && (
                                <div className="issues-proof-upload" style={{ marginTop: '0' }}>
                                    <span className="proof-upload-label">Mentor's resolution proof: </span>
                                    <a href={selectedSessionForIssues.mentor_resolution_proof_file_url} target="_blank" rel="noopener noreferrer" className="feedback-file-link">View / Download</a>
                                </div>
                            )}
                            <div className="modal-actions">
                                <button type="submit" className="submit-button" disabled={issuesSubmitting}>{issuesSubmitting ? 'Saving...' : 'Save'}</button>
                                <button type="button" className="cancel-button" onClick={handleIssuesClose}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Counseling;
