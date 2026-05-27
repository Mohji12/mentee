import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import './CounselingDashboard.css';
import FeedbackForm from './FeedbackForm';

const CounselingDashboard = () => {
    const { mentor_id } = useParams();
    const [activeTab, setActiveTab] = useState('upcoming');
    const [sessions, setSessions] = useState([]);
    const [filteredSessions, setFilteredSessions] = useState([]);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [studentFilter, setStudentFilter] = useState('');
    const [showFilter, setShowFilter] = useState(false);
    const [showFeedbackForm, setShowFeedbackForm] = useState(false);
    const [selectedSessionId, setSelectedSessionId] = useState(null);
    const [showReferModal, setShowReferModal] = useState(false);
    const [referSession, setReferSession] = useState(null);
    const [referName, setReferName] = useState('');
    const [referContact, setReferContact] = useState('');
    const [referSubmitting, setReferSubmitting] = useState(false);
    const [showIssuesModal, setShowIssuesModal] = useState(false);
    const [issuesData, setIssuesData] = useState([]);
    const [issuesSessionId, setIssuesSessionId] = useState(null);
    const [issuesProofUrl, setIssuesProofUrl] = useState(null);
    const [issuesMentorResolutionProofUrl, setIssuesMentorResolutionProofUrl] = useState(null);
    const [issuesResolutionProofFile, setIssuesResolutionProofFile] = useState(null);
    const [issuesSaving, setIssuesSaving] = useState(false);
    const [showIssueResolutionFeedbackModal, setShowIssueResolutionFeedbackModal] = useState(false);
    const [issueResolutionFeedbackSession, setIssueResolutionFeedbackSession] = useState(null);
    const [issueResolutionFeedbackRows, setIssueResolutionFeedbackRows] = useState([]);
    const [issueResolutionFeedbackSaving, setIssueResolutionFeedbackSaving] = useState(false);
    const [issueResolutionFeedbackProofFile, setIssueResolutionFeedbackProofFile] = useState(null);
    
    // Outcome and Follow-up Tracking State
    const [showOutcomeModal, setShowOutcomeModal] = useState(false);
    const [outcomeSession, setOutcomeSession] = useState(null);
    const [outcomeStatus, setOutcomeStatus] = useState('');
    const [outcomeNotes, setOutcomeNotes] = useState('');
    const [followupDate, setFollowupDate] = useState('');
    const [outcomeSaving, setOutcomeSaving] = useState(false);
    
    const [showFollowupModal, setShowFollowupModal] = useState(false);
    const [followupParentSession, setFollowupParentSession] = useState(null);
    const [followupSessionDate, setFollowupSessionDate] = useState('');
    const [followupVenue, setFollowupVenue] = useState('');
    const [followupReason, setFollowupReason] = useState('');
    const [followupUrgent, setFollowupUrgent] = useState(false);
    const [followupSaving, setFollowupSaving] = useState(false);
    
    const [followupsDue, setFollowupsDue] = useState([]);
    const [followupsDueLoading, setFollowupsDueLoading] = useState(false);
    
    const [analytics, setAnalytics] = useState(null);
    const [analyticsLoading, setAnalyticsLoading] = useState(false);
    
    const [notifications, setNotifications] = useState([]);
    const [notificationCount, setNotificationCount] = useState(0);
    const [showNotifications, setShowNotifications] = useState(false);

    useEffect(() => {
        fetchNotifications();
        fetchSessions();
        fetchStats();
        if (activeTab === 'followups') {
            fetchFollowupsDue();
        }
        if (activeTab === 'analytics') {
            fetchAnalytics();
        }
    }, [activeTab]);

    useEffect(() => {
        // Filter sessions based on student USN
        if (studentFilter.trim() === '') {
            setFilteredSessions(sessions);
        } else {
            const filtered = sessions.filter(session => 
                session.student_usn.toLowerCase().includes(studentFilter.toLowerCase()) ||
                session.student_name.toLowerCase().includes(studentFilter.toLowerCase())
            );
            setFilteredSessions(filtered);
        }
    }, [sessions, studentFilter]);

    const fetchSessions = async () => {
        setLoading(true);
        try {
            const token = sessionStorage.getItem('access_token');
            let url = `${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions`;
            if (activeTab === 'upcoming') {
                url = `${API_BASE_URL}/mentor/${mentor_id}/counseling/upcoming`;
            } else if (activeTab !== 'all') {
                url += `?status=${activeTab}`;
            }
            
            const response = await fetch(url, {
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
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const token = sessionStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/stats`, {
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

    const fetchFollowupsDue = async () => {
        setFollowupsDueLoading(true);
        try {
            const token = sessionStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/followups-due?include_overdue=true&days_ahead=30`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setFollowupsDue(data);
            }
        } catch (error) {
            console.error('Error fetching follow-ups due:', error);
        } finally {
            setFollowupsDueLoading(false);
        }
    };

    const fetchAnalytics = async () => {
        setAnalyticsLoading(true);
        try {
            const token = sessionStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/analytics?months=6`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setAnalytics(data);
            }
        } catch (error) {
            console.error('Error fetching analytics:', error);
        } finally {
            setAnalyticsLoading(false);
        }
    };

    const fetchNotifications = async () => {
        try {
            const token = sessionStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/notifications?limit=10`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                setNotifications(data.notifications || []);
                setNotificationCount(data.unread_count || 0);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    };

    const markNotificationRead = async (notificationId) => {
        try {
            const token = sessionStorage.getItem('access_token');
            await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/notifications/${notificationId}/read`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            fetchNotifications();
        } catch (error) {
            console.error('Error marking notification read:', error);
        }
    };

    const markAllNotificationsRead = async () => {
        try {
            const token = sessionStorage.getItem('access_token');
            await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/notifications/read-all`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            fetchNotifications();
        } catch (error) {
            console.error('Error marking all notifications read:', error);
        }
    };

    const updateSessionStatus = async (counselingId, status, notes = '', feedback = '') => {
        try {
            const token = sessionStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions/${counselingId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    status,
                    notes,
                    feedback
                })
            });

            if (response.ok) {
                setMessage('Session updated successfully!');
                fetchSessions();
                fetchStats();
            } else {
                const error = await response.json();
                setMessage(`Error: ${error.detail}`);
            }
        } catch (error) {
            setMessage('Error updating session');
        }
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
            case 'cancelled': return '#F44336';
            case 'rescheduled': return '#FF9800';
            case 'referred': return '#9C27B0';
            default: return '#757575';
        }
    };

    const isUpcoming = (sessionDate) => {
        const d = parseUtc(sessionDate);
        return d && !isNaN(d.getTime()) && d > new Date();
    };

    const handleFeedbackClick = (sessionId) => {
        setSelectedSessionId(sessionId);
        setShowFeedbackForm(true);
    };

    const handleFeedbackClose = () => {
        setShowFeedbackForm(false);
        setSelectedSessionId(null);
    };

    const handleFeedbackSuccess = () => {
        fetchSessions();
        fetchStats();
    };

    const openReferModal = (session) => {
        setReferSession(session);
        setReferName('');
        setReferContact('');
        setShowReferModal(true);
    };

    const handleReferSubmit = async (e) => {
        e.preventDefault();
        if (!referSession || !referName.trim()) {
            setMessage('Specialist name is required.');
            return;
        }
        setReferSubmitting(true);
        setMessage('');
        try {
            const token = sessionStorage.getItem('access_token');
            const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions/${referSession.counseling_id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                    status: 'referred',
                    referred_to_name: referName.trim(),
                    referred_to_contact: referContact.trim() || undefined
                })
            });
            if (res.ok) {
                setShowReferModal(false);
                setReferSession(null);
                fetchSessions();
                fetchStats();
                setMessage('Student referred successfully. They will receive an email.');
            } else {
                const err = await res.json();
                setMessage(err.detail || 'Failed to refer.');
            }
        } catch (e) {
            setMessage('Failed to refer.');
        } finally {
            setReferSubmitting(false);
        }
    };

    const handleViewIssues = async (session) => {
        setIssuesSessionId(session.counseling_id);
        setIssuesData([]);
        setIssuesProofUrl(session.student_issues_proof_file_url || null);
        setIssuesMentorResolutionProofUrl(session.mentor_resolution_proof_file_url || null);
        setIssuesResolutionProofFile(null);
        setShowIssuesModal(true);
        try {
            const token = sessionStorage.getItem('access_token');
            const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions/${session.counseling_id}/issues-resolution`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setIssuesData(Array.isArray(data) ? data : []);
            }
        } catch (e) {
            console.error('Failed to load issues/resolution', e);
        }
    };

    const formatDateDDMMMYYYY = (dateStr) => {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        return `${d.getDate().toString().padStart(2,'0')}-${months[d.getMonth()]}-${d.getFullYear()}`;
    };

    const ISSUE_RESOLUTION_ROW_TYPES = [
        { row_type: 'issue_raised', label: 'Issue Raised by Mentor' },
        { row_type: 'details_of_resolution', label: 'Details of Resolution' },
        { row_type: 'resolution', label: 'Resolution' }
    ];
    const getIssueResolutionRowLabel = (rowType) => {
        const r = ISSUE_RESOLUTION_ROW_TYPES.find(x => x.row_type === rowType);
        return r ? r.label : rowType || '';
    };

    const openIssueResolutionFeedbackModal = (session) => {
        setIssueResolutionFeedbackSession(session);
        const existing = session.issue_resolution_feedback || [];
        const byType = {};
        existing.forEach(row => { byType[row.row_type] = row; });
        setIssueResolutionFeedbackRows(ISSUE_RESOLUTION_ROW_TYPES.map(({ row_type }) => ({
            row_type,
            description: byType[row_type]?.description ?? '',
            feedback_date: byType[row_type]?.feedback_date ?? '',
            status: byType[row_type]?.status ?? ''
        })));
        setShowIssueResolutionFeedbackModal(true);
    };

    const updateIssueResolutionFeedbackRow = (index, field, value) => {
        setIssueResolutionFeedbackRows(prev => prev.map((row, i) => i === index ? { ...row, [field]: value } : row));
    };

    const saveIssueResolutionFeedback = async () => {
        if (!issueResolutionFeedbackSession?.counseling_id) return;
        setIssueResolutionFeedbackSaving(true);
        setMessage('');
        try {
            const token = sessionStorage.getItem('access_token');
            const rows = issueResolutionFeedbackRows.map(r => ({
                row_type: r.row_type,
                description: r.description || null,
                feedback_date: r.feedback_date ? r.feedback_date : null,
                status: (r.status === 'WIP' || r.status === 'Close') ? r.status : null
            }));
            const formData = new FormData();
            formData.append('rows', JSON.stringify(rows));
            if (issueResolutionFeedbackProofFile) formData.append('file', issueResolutionFeedbackProofFile);
            const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions/${issueResolutionFeedbackSession.counseling_id}/issue-resolution-feedback`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            if (res.ok) {
                setShowIssueResolutionFeedbackModal(false);
                setIssueResolutionFeedbackSession(null);
                setIssueResolutionFeedbackProofFile(null);
                fetchSessions();
                setMessage('Feedback table saved.');
            } else {
                const err = await res.json();
                setMessage(err.detail || 'Failed to save feedback.');
            }
        } catch (e) {
            console.error('Failed to save issue resolution feedback', e);
            setMessage('Failed to save feedback.');
        } finally {
            setIssueResolutionFeedbackSaving(false);
        }
    };

    // Outcome Modal Handlers
    const openOutcomeModal = (session) => {
        setOutcomeSession(session);
        setOutcomeStatus(session.outcome_status || '');
        setOutcomeNotes(session.outcome_notes || '');
        setFollowupDate(session.followup_date || '');
        setShowOutcomeModal(true);
    };

    const handleOutcomeSubmit = async (e) => {
        e.preventDefault();
        if (!outcomeSession || !outcomeStatus) {
            setMessage('Please select an outcome status.');
            return;
        }
        setOutcomeSaving(true);
        setMessage('');
        try {
            const token = sessionStorage.getItem('access_token');
            const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions/${outcomeSession.counseling_id}/outcome`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                    outcome_status: outcomeStatus,
                    outcome_notes: outcomeNotes || null,
                    followup_date: followupDate || null
                })
            });
            if (res.ok) {
                setShowOutcomeModal(false);
                setOutcomeSession(null);
                fetchSessions();
                fetchStats();
                setMessage('Outcome set successfully.');
                if (outcomeStatus === 'needs_followup' && followupDate) {
                    fetchFollowupsDue();
                }
            } else {
                const err = await res.json();
                setMessage(err.detail || 'Failed to set outcome.');
            }
        } catch (e) {
            setMessage('Failed to set outcome.');
        } finally {
            setOutcomeSaving(false);
        }
    };

    // Follow-up Scheduling Modal Handlers
    const openFollowupModal = (session) => {
        setFollowupParentSession(session);
        setFollowupSessionDate('');
        setFollowupVenue(session.venue || '');
        setFollowupReason(`Follow-up for: ${session.reason}`);
        setFollowupUrgent(false);
        setShowFollowupModal(true);
    };

    const handleFollowupSubmit = async (e) => {
        e.preventDefault();
        if (!followupParentSession || !followupSessionDate || !followupVenue) {
            setMessage('Please fill all required fields.');
            return;
        }
        setFollowupSaving(true);
        setMessage('');
        try {
            const token = sessionStorage.getItem('access_token');
            const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions/${followupParentSession.counseling_id}/schedule-followup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({
                    session_date: followupSessionDate,
                    venue: followupVenue,
                    reason: followupReason || null,
                    is_urgent: followupUrgent
                })
            });
            if (res.ok) {
                setShowFollowupModal(false);
                setFollowupParentSession(null);
                fetchSessions();
                fetchStats();
                fetchFollowupsDue();
                setMessage('Follow-up session scheduled successfully. Student notified via email.');
            } else {
                const err = await res.json();
                setMessage(err.detail || 'Failed to schedule follow-up.');
            }
        } catch (e) {
            setMessage('Failed to schedule follow-up.');
        } finally {
            setFollowupSaving(false);
        }
    };

    const getOutcomeStatusLabel = (status) => {
        const labels = {
            'fully_resolved': 'Fully Resolved',
            'partially_resolved': 'Partially Resolved',
            'unresolved': 'Unresolved',
            'needs_followup': 'Needs Follow-up'
        };
        return labels[status] || status || 'Not Set';
    };

    const getOutcomeStatusColor = (status) => {
        const colors = {
            'fully_resolved': '#28a745',
            'partially_resolved': '#ffc107',
            'unresolved': '#dc3545',
            'needs_followup': '#17a2b8'
        };
        return colors[status] || '#6c757d';
    };

    const updateIssueResolution = (index, field, value) => {
        setIssuesData(prev => prev.map((row, i) => i === index ? { ...row, [field]: value } : row));
    };

    const handleSaveIssuesResolution = async () => {
        if (!issuesSessionId) return;
        setIssuesSaving(true);
        setMessage('');
        try {
            const token = sessionStorage.getItem('access_token');
            const formData = new FormData();
            formData.append('rows', JSON.stringify(issuesData.map(r => ({
                id: r.id,
                resolution_details: r.resolution_details || null,
                date_resolution_provided: r.date_resolution_provided || null
            }))));
            if (issuesResolutionProofFile) formData.append('file', issuesResolutionProofFile);
            const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/counseling/sessions/${issuesSessionId}/issues-resolution`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            if (res.ok) {
                const data = await res.json();
                setIssuesData(Array.isArray(data) ? data : []);
                setIssuesResolutionProofFile(null);
                fetchSessions();
                setMessage('Resolution details saved.');
            } else {
                const err = await res.json();
                setMessage(err.detail || 'Failed to save resolution.');
            }
        } catch (e) {
            console.error('Failed to save resolution', e);
            setMessage('Failed to save resolution.');
        } finally {
            setIssuesSaving(false);
        }
    };

    return (
        <div className="counseling-dashboard">
            <div className="dashboard-header">
                <div className="dashboard-title-row">
                    <h1>Student Support Dashboard</h1>
                    <div className="notification-bell-container">
                        <button 
                            className="notification-bell-btn"
                            onClick={() => setShowNotifications(!showNotifications)}
                        >
                            🔔
                            {notificationCount > 0 && (
                                <span className="notification-badge">{notificationCount}</span>
                            )}
                        </button>
                        {showNotifications && (
                            <div className="notification-dropdown">
                                <div className="notification-dropdown-header">
                                    <h4>Notifications</h4>
                                    {notificationCount > 0 && (
                                        <button 
                                            className="mark-all-read-btn"
                                            onClick={markAllNotificationsRead}
                                        >
                                            Mark all read
                                        </button>
                                    )}
                                </div>
                                <div className="notification-list">
                                    {notifications.length === 0 ? (
                                        <p className="no-notifications">No notifications</p>
                                    ) : (
                                        notifications.map((notif) => (
                                            <div 
                                                key={notif.id} 
                                                className={`notification-item ${notif.is_read ? 'read' : 'unread'}`}
                                                onClick={() => !notif.is_read && markNotificationRead(notif.id)}
                                            >
                                                <div className="notification-icon">
                                                    {notif.reminder_type === 'upcoming_session' && '📅'}
                                                    {notif.reminder_type === 'followup_due' && '⏰'}
                                                    {notif.reminder_type === 'overdue_followup' && '⚠️'}
                                                </div>
                                                <div className="notification-content">
                                                    <span className="notification-title">{notif.title}</span>
                                                    <span className="notification-message">{notif.message}</span>
                                                    <span className="notification-time">
                                                        {new Date(notif.scheduled_for).toLocaleDateString('en-IN', { 
                                                            month: 'short', 
                                                            day: 'numeric',
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })}
                                                    </span>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
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
                    <div className="stat-card urgent">
                        <h3>Urgent</h3>
                        <p>{stats.urgent_sessions || 0}</p>
                    </div>
                </div>
            </div>

            <div className="dashboard-tabs">
                <button 
                    className={`tab-button ${activeTab === 'upcoming' ? 'active' : ''}`}
                    onClick={() => setActiveTab('upcoming')}
                >
                    Upcoming Sessions
                </button>
                <button 
                    className={`tab-button ${activeTab === 'scheduled' ? 'active' : ''}`}
                    onClick={() => setActiveTab('scheduled')}
                >
                    All Scheduled
                </button>
                <button 
                    className={`tab-button ${activeTab === 'completed' ? 'active' : ''}`}
                    onClick={() => setActiveTab('completed')}
                >
                    Completed
                </button>
                <button 
                    className={`tab-button ${activeTab === 'followups' ? 'active' : ''}`}
                    onClick={() => setActiveTab('followups')}
                >
                    📅 Follow-ups Due
                    {followupsDue.length > 0 && <span className="tab-badge">{followupsDue.length}</span>}
                </button>
                <button 
                    className={`tab-button ${activeTab === 'all' ? 'active' : ''}`}
                    onClick={() => setActiveTab('all')}
                >
                    All Sessions
                </button>
                <button 
                    className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
                    onClick={() => setActiveTab('analytics')}
                >
                    📊 Analytics
                </button>
            </div>

            {/* Filter Section */}
            <div className="filter-section">
                <div className="filter-header">
                    <button 
                        className="filter-toggle"
                        onClick={() => setShowFilter(!showFilter)}
                    >
                        <span className="filter-icon">🔍</span>
                        Filter Sessions
                        <span className={`filter-arrow ${showFilter ? 'open' : ''}`}>▼</span>
                    </button>
                    {studentFilter && (
                        <div className="filter-info">
                            <span>Filtered by: "{studentFilter}"</span>
                            <button 
                                className="clear-filter"
                                onClick={() => setStudentFilter('')}
                            >
                                Clear Filter
                            </button>
                        </div>
                    )}
                </div>
                
                {showFilter && (
                    <div className="filter-content">
                        <div className="filter-group">
                            <label htmlFor="studentFilter">Filter by Student USN or Name:</label>
                            <input
                                type="text"
                                id="studentFilter"
                                placeholder="Enter student USN or name..."
                                value={studentFilter}
                                onChange={(e) => setStudentFilter(e.target.value)}
                                className="filter-input"
                            />
                        </div>
                        <div className="filter-stats">
                            <span>Showing {filteredSessions.length} of {sessions.length} sessions</span>
                        </div>
                    </div>
                )}
            </div>

            {message && (
                <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
                    {message}
                </div>
            )}

            {/* Follow-ups Due Tab Content */}
            {activeTab === 'followups' && (
                <div className="followups-due-container">
                    <div className="followups-due-header">
                        <h2>📅 Sessions Needing Follow-up</h2>
                        <p>Sessions marked as "Needs Follow-up" with scheduled follow-up dates</p>
                    </div>
                    {followupsDueLoading ? (
                        <div className="loading">Loading follow-ups...</div>
                    ) : followupsDue.length === 0 ? (
                        <div className="no-sessions">
                            <p>No follow-ups are currently due. Great job!</p>
                        </div>
                    ) : (
                        <div className="followups-due-list">
                            {followupsDue.map((item) => (
                                <div key={item.counseling_id} className={`followup-due-card ${item.is_overdue ? 'overdue' : ''}`}>
                                    <div className="followup-due-header">
                                        <h3>Session #{item.counseling_id}</h3>
                                        <div className="followup-due-badges">
                                            {item.is_overdue ? (
                                                <span className="overdue-badge">⚠️ OVERDUE by {Math.abs(item.days_until_followup)} days</span>
                                            ) : (
                                                <span className="due-badge">📅 Due in {item.days_until_followup} days</span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="followup-due-details">
                                        <div className="detail-row">
                                            <strong>Student:</strong>
                                            <span>{item.student_name} ({item.student_usn})</span>
                                        </div>
                                        <div className="detail-row">
                                            <strong>Original Session:</strong>
                                            <span>{formatDate(item.session_date)}</span>
                                        </div>
                                        <div className="detail-row">
                                            <strong>Follow-up Date:</strong>
                                            <span>{new Date(item.followup_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}</span>
                                        </div>
                                        {item.outcome_notes && (
                                            <div className="detail-row">
                                                <strong>Notes:</strong>
                                                <span>{item.outcome_notes}</span>
                                            </div>
                                        )}
                                    </div>
                                    <div className="followup-due-actions">
                                        <button 
                                            className="action-button complete"
                                            onClick={() => {
                                                const session = sessions.find(s => s.counseling_id === item.counseling_id);
                                                if (session) openFollowupModal(session);
                                                else {
                                                    openFollowupModal({
                                                        counseling_id: item.counseling_id,
                                                        venue: '',
                                                        reason: item.outcome_notes || 'Follow-up session'
                                                    });
                                                }
                                            }}
                                        >
                                            Schedule Follow-up Session
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Analytics Tab Content */}
            {activeTab === 'analytics' && (
                <div className="analytics-container">
                    <div className="analytics-header">
                        <h2>📊 Counseling Analytics</h2>
                        <p>Insights from the last 6 months of your counseling sessions</p>
                    </div>
                    {analyticsLoading ? (
                        <div className="loading">Loading analytics...</div>
                    ) : analytics ? (
                        <div className="analytics-content">
                            {/* Summary Stats */}
                            <div className="analytics-stats-grid">
                                <div className="analytics-stat-card total">
                                    <div className="analytics-stat-value">{analytics.summary.total_sessions}</div>
                                    <div className="analytics-stat-label">Total Sessions</div>
                                </div>
                                <div className="analytics-stat-card success">
                                    <div className="analytics-stat-value">{analytics.summary.completion_rate}%</div>
                                    <div className="analytics-stat-label">Completion Rate</div>
                                </div>
                                <div className="analytics-stat-card info">
                                    <div className="analytics-stat-value">{analytics.summary.unique_students}</div>
                                    <div className="analytics-stat-label">Unique Students</div>
                                </div>
                                <div className="analytics-stat-card warning">
                                    <div className="analytics-stat-value">{analytics.summary.followup_rate}%</div>
                                    <div className="analytics-stat-label">Follow-up Rate</div>
                                </div>
                            </div>

                            {/* Session Breakdown */}
                            <div className="analytics-section">
                                <h3>Session Breakdown</h3>
                                <div className="analytics-breakdown">
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">Completed</span>
                                        <span className="breakdown-value success">{analytics.summary.completed}</span>
                                    </div>
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">Scheduled</span>
                                        <span className="breakdown-value info">{analytics.summary.scheduled}</span>
                                    </div>
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">Cancelled</span>
                                        <span className="breakdown-value danger">{analytics.summary.cancelled}</span>
                                    </div>
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">Referred</span>
                                        <span className="breakdown-value purple">{analytics.summary.referred}</span>
                                    </div>
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">Urgent Sessions</span>
                                        <span className="breakdown-value warning">{analytics.summary.urgent_sessions}</span>
                                    </div>
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">Follow-up Sessions</span>
                                        <span className="breakdown-value">{analytics.summary.followup_sessions}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Outcomes Distribution */}
                            {analytics.outcomes.distribution.length > 0 && (
                                <div className="analytics-section">
                                    <h3>Outcome Distribution</h3>
                                    <div className="outcomes-grid">
                                        {analytics.outcomes.distribution.map((outcome) => (
                                            <div key={outcome.status} className={`outcome-card ${outcome.status}`}>
                                                <div className="outcome-value">{outcome.count}</div>
                                                <div className="outcome-label">{outcome.status.replace(/_/g, ' ')}</div>
                                            </div>
                                        ))}
                                    </div>
                                    {analytics.outcomes.avg_resolution_time_days > 0 && (
                                        <div className="resolution-time">
                                            <span>Average Resolution Time:</span>
                                            <strong>{analytics.outcomes.avg_resolution_time_days} days</strong>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Ratings */}
                            {analytics.ratings.total_rated_sessions > 0 && (
                                <div className="analytics-section">
                                    <h3>Session Ratings</h3>
                                    <div className="ratings-grid">
                                        <div className="rating-card">
                                            <div className="rating-value">
                                                {'⭐'.repeat(Math.round(analytics.ratings.avg_mentor_rating))}
                                            </div>
                                            <div className="rating-score">{analytics.ratings.avg_mentor_rating}/5</div>
                                            <div className="rating-label">Your Average Rating</div>
                                        </div>
                                        <div className="rating-card">
                                            <div className="rating-value">
                                                {'⭐'.repeat(Math.round(analytics.ratings.avg_student_rating))}
                                            </div>
                                            <div className="rating-score">{analytics.ratings.avg_student_rating}/5</div>
                                            <div className="rating-label">Student Average Rating</div>
                                        </div>
                                        <div className="rating-card">
                                            <div className="rating-value">{analytics.ratings.total_rated_sessions}</div>
                                            <div className="rating-label">Total Rated Sessions</div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Monthly Trend */}
                            {analytics.trends.sessions_by_month.length > 0 && (
                                <div className="analytics-section">
                                    <h3>Monthly Trend</h3>
                                    <div className="trend-chart">
                                        {analytics.trends.sessions_by_month.map((month) => (
                                            <div key={month.month} className="trend-bar-container">
                                                <div 
                                                    className="trend-bar" 
                                                    style={{ 
                                                        height: `${Math.max(10, (month.count / Math.max(...analytics.trends.sessions_by_month.map(m => m.count))) * 100)}%` 
                                                    }}
                                                >
                                                    <span className="trend-count">{month.count}</span>
                                                </div>
                                                <span className="trend-month">
                                                    {new Date(month.month + '-01').toLocaleDateString('en-IN', { month: 'short' })}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="no-sessions">
                            <p>No analytics data available.</p>
                        </div>
                    )}
                </div>
            )}

            <div className="sessions-container" style={{ display: (activeTab === 'followups' || activeTab === 'analytics') ? 'none' : 'block' }}>
                {loading ? (
                    <div className="loading">Loading sessions...</div>
                ) : filteredSessions.length === 0 ? (
                    <div className="no-sessions">
                        <p>{sessions.length === 0 ? 'No student support sessions found.' : 'No sessions match your filter criteria.'}</p>
                    </div>
                ) : (
                    <div className="sessions-list">
                        {filteredSessions.map((session) => (
                            <div key={session.id} className="session-card">
                                <div className="session-header">
                                    <div className="session-info">
                                        <h3>Session #{session.counseling_id}</h3>
                                        <p className="student-name">Student: {session.student_name}</p>
                                    </div>
                                    <div className="session-badges">
                                        <span 
                                            className="status-badge"
                                            style={{ backgroundColor: getStatusColor(session.status) }}
                                        >
                                            {session.status.toUpperCase()}
                                        </span>
                                        {session.is_urgent && (
                                            <span className="urgent-badge">URGENT</span>
                                        )}
                                        {session.parent_session_id && (
                                            <span className="followup-badge" title={`Follow-up of ${session.parent_session_id}`}>🔗 Follow-up</span>
                                        )}
                                        {session.outcome_status && (
                                            <span 
                                                className="outcome-badge"
                                                style={{ backgroundColor: getOutcomeStatusColor(session.outcome_status) }}
                                            >
                                                {getOutcomeStatusLabel(session.outcome_status)}
                                            </span>
                                        )}
                                    </div>
                                </div>
                                
                                <div className="session-details">
                                    <div className="detail-row">
                                        <strong>Date & Time:</strong>
                                        <span>{formatDate(session.session_date)}</span>
                                    </div>
                                    <div className="detail-row">
                                        <strong>Venue:</strong>
                                        <span>{session.venue}</span>
                                    </div>
                                    <div className="detail-row">
                                        <strong>Reason:</strong>
                                        <span>{session.reason}</span>
                                    </div>
                                    <div className="detail-row">
                                        <strong>Student Contact:</strong>
                                        <span>{session.student_email} | {session.student_phoneno}</span>
                                    </div>
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
                                                    Note: This is a generated link. If the meeting doesn't exist, please create it manually in Google Meet.
                                                </small>
                                            </div>
                                        </div>
                                    )}
                                    {session.notes && (
                                        <div className="detail-row">
                                            <strong>Notes:</strong>
                                            <span>{session.notes}</span>
                                        </div>
                                    )}
                                    {session.feedback && (
                                        <div className="detail-row">
                                            <strong>Feedback:</strong>
                                            <span>{session.feedback}</span>
                                        </div>
                                    )}
                                    {session.status === 'referred' && (session.referred_to_name || session.referred_to_contact) && (
                                        <div className="detail-row referred-info">
                                            <strong>Referred to:</strong>
                                            <span>{session.referred_to_name || ''}{session.referred_to_contact ? ` (${session.referred_to_contact})` : ''}</span>
                                        </div>
                                    )}
                                    {session.parent_session_id && (
                                        <div className="detail-row chain-info">
                                            <strong>Follow-up of:</strong>
                                            <span>Session #{session.parent_session_id}</span>
                                        </div>
                                    )}
                                    {session.outcome_status && (
                                        <div className="detail-row outcome-info">
                                            <strong>Outcome:</strong>
                                            <span style={{ color: getOutcomeStatusColor(session.outcome_status), fontWeight: 'bold' }}>
                                                {getOutcomeStatusLabel(session.outcome_status)}
                                            </span>
                                            {session.outcome_notes && <span className="outcome-notes"> — {session.outcome_notes}</span>}
                                        </div>
                                    )}
                                    {session.followup_date && (
                                        <div className="detail-row followup-date-info">
                                            <strong>Follow-up Date:</strong>
                                            <span>
                                                {new Date(session.followup_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                                                {session.followup_scheduled && <span className="followup-scheduled-badge"> ✓ Scheduled</span>}
                                            </span>
                                        </div>
                                    )}

                                    {/* Issue raised & resolution – tabular feedback (only for completed or referred sessions) */}
                                    {(session.status === 'completed' || session.status === 'referred') && (
                                        <div className="issue-resolution-feedback-section">
                                            <div className="detail-row" style={{ marginBottom: '0.5rem' }}>
                                                <strong>Issue raised & resolution</strong>
                                                <button
                                                    type="button"
                                                    className="action-button feedback"
                                                    style={{ marginLeft: 'auto', padding: '0.25rem 0.5rem', fontSize: '0.85rem' }}
                                                    onClick={() => openIssueResolutionFeedbackModal(session)}
                                                >
                                                    Edit feedback table
                                                </button>
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
                                                        {(session.issue_resolution_feedback || []).map((row, idx) => (
                                                            <tr key={row.row_type || idx}>
                                                                <td>
                                                                    <span className="feedback-row-label">{getIssueResolutionRowLabel(row.row_type)}</span>
                                                                    {row.description && <div className="feedback-row-desc">{row.description}</div>}
                                                                </td>
                                                                <td>{row.feedback_date ? formatDateDDMMMYYYY(row.feedback_date) : '–'}</td>
                                                                <td><span className="status-badge small" style={{ backgroundColor: row.status === 'Close' ? '#28a745' : '#ffc107', color: '#000' }}>{row.status || '–'}</span></td>
                                                            </tr>
                                                        ))}
                                                        {(!session.issue_resolution_feedback || session.issue_resolution_feedback.length === 0) && (
                                                            <tr><td colSpan={3} className="no-feedback-msg">No feedback yet. Use &quot;Edit feedback table&quot; to add.</td></tr>
                                                        )}
                                                    </tbody>
                                                </table>
                                            </div>
                                            {session.issue_resolution_feedback_proof_file_url && (
                                                <div style={{ marginTop: '8px', fontSize: '0.9rem' }}>
                                                    <span className="feedback-label">Proof: </span>
                                                    <a href={session.issue_resolution_feedback_proof_file_url} target="_blank" rel="noopener noreferrer" className="feedback-file-link">View / Download</a>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {session.status === 'scheduled' && isUpcoming(session.session_date) && (
                                    <div className="session-actions">
                                        <button 
                                            className="action-button complete"
                                            onClick={() => updateSessionStatus(session.counseling_id, 'completed')}
                                        >
                                            Mark Complete
                                        </button>
                                        <button 
                                            className="action-button refer"
                                            onClick={() => openReferModal(session)}
                                        >
                                            Refer to specialist
                                        </button>
                                        <button 
                                            className="action-button reschedule"
                                            onClick={() => {
                                                const notes = prompt('Add notes for rescheduling:');
                                                if (notes !== null) {
                                                    updateSessionStatus(session.counseling_id, 'rescheduled', notes);
                                                }
                                            }}
                                        >
                                            Reschedule
                                        </button>
                                        <button 
                                            className="action-button cancel"
                                            onClick={() => {
                                                const reason = prompt('Reason for cancellation:');
                                                if (reason !== null) {
                                                    updateSessionStatus(session.counseling_id, 'cancelled', reason);
                                                }
                                            }}
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                )}

                                {(session.status === 'completed' || session.status === 'referred') && (
                                    <div className="session-actions">
                                        <button 
                                            className="action-button feedback"
                                            onClick={() => handleFeedbackClick(session.counseling_id)}
                                        >
                                            {session.mentor_feedback ? 'View Feedback' : 'Submit Feedback'}
                                        </button>
                                        <button 
                                            className="action-button issues-view"
                                            onClick={() => handleViewIssues(session)}
                                        >
                                            View Issues & Resolution
                                        </button>
                                        {session.status === 'completed' && (
                                            <>
                                                <button 
                                                    className="action-button outcome"
                                                    onClick={() => openOutcomeModal(session)}
                                                >
                                                    {session.outcome_status ? '✏️ Edit Outcome' : '📋 Set Outcome'}
                                                </button>
                                                {session.outcome_status && !session.followup_scheduled && (
                                                    <button 
                                                        className="action-button followup"
                                                        onClick={() => openFollowupModal(session)}
                                                    >
                                                        📅 Schedule Follow-up
                                                    </button>
                                                )}
                                            </>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {showFeedbackForm && (
                <FeedbackForm
                    counselingId={selectedSessionId}
                    mentorId={mentor_id}
                    onClose={handleFeedbackClose}
                    onSuccess={handleFeedbackSuccess}
                />
            )}

            {showReferModal && referSession && (
                <div className="counseling-modal-overlay" onClick={() => setShowReferModal(false)}>
                    <div className="counseling-modal refer-modal" onClick={e => e.stopPropagation()}>
                        <div className="counseling-modal-header">
                            <h3>Refer to specialist</h3>
                            <button type="button" className="modal-close" onClick={() => setShowReferModal(false)} aria-label="Close">&times;</button>
                        </div>
                        <form onSubmit={handleReferSubmit}>
                            <p className="refer-modal-hint">Session #{referSession.counseling_id}. The student will receive an email with the specialist details.</p>
                            <div className="form-group">
                                <label>Specialist name (required)</label>
                                <input type="text" value={referName} onChange={e => setReferName(e.target.value)} placeholder="Name of the person" required />
                            </div>
                            <div className="form-group">
                                <label>Contact (optional)</label>
                                <input type="text" value={referContact} onChange={e => setReferContact(e.target.value)} placeholder="Phone or email" />
                            </div>
                            <div className="modal-actions">
                                <button type="submit" className="action-button complete" disabled={referSubmitting}>{referSubmitting ? 'Submitting...' : 'Refer student'}</button>
                                <button type="button" className="action-button cancel" onClick={() => setShowReferModal(false)}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showIssuesModal && (
                <div className="counseling-modal-overlay" onClick={() => setShowIssuesModal(false)}>
                    <div className="counseling-modal issues-view-modal" onClick={e => e.stopPropagation()}>
                        <div className="counseling-modal-header">
                            <h3>Details of Issues Raised & Resolved</h3>
                            <button type="button" className="modal-close" onClick={() => setShowIssuesModal(false)} aria-label="Close">&times;</button>
                        </div>
                        {issuesSessionId && <p className="issues-modal-session">Session #{issuesSessionId}</p>}
                        {issuesData.length === 0 ? (
                            <p className="no-issues-msg">No issues & resolution data submitted by the student yet.</p>
                        ) : (
                            <div className="issues-table-wrap">
                                <table className="issues-resolution-table">
                                    <thead>
                                        <tr>
                                            <th>S. No</th>
                                            <th>Issues Raised</th>
                                            <th>Date of Issue raised</th>
                                            <th>Details of Resolution Provided</th>
                                            <th>Date of Resolution provided</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {issuesData.map((row, idx) => (
                                            <tr key={row.id ?? idx}>
                                                <td>{row.serial_no}</td>
                                                <td>{row.issues_raised}</td>
                                                <td>{formatDateDDMMMYYYY(row.date_issue_raised)}</td>
                                                <td>
                                                    <input type="text" className="resolution-input" value={row.resolution_details || ''} onChange={e => updateIssueResolution(idx, 'resolution_details', e.target.value)} placeholder="Resolution details" />
                                                </td>
                                                <td>
                                                    <input type="date" className="resolution-date-input" value={row.date_resolution_provided || ''} onChange={e => updateIssueResolution(idx, 'date_resolution_provided', e.target.value)} />
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                        {issuesProofUrl && (
                            <div className="issues-proof-link" style={{ padding: '0 24px 12px' }}>
                                <span className="feedback-label">Mentee's proof: </span>
                                <a href={issuesProofUrl} target="_blank" rel="noopener noreferrer" className="feedback-file-link">View / Download</a>
                            </div>
                        )}
                        {issuesData.length > 0 && (
                            <div className="issues-resolution-proof-upload" style={{ padding: '0 24px 12px', borderTop: '1px solid #eee' }}>
                                <label className="proof-upload-label">Resolution proof (optional):</label>
                                {issuesMentorResolutionProofUrl && (
                                    <div style={{ marginBottom: '8px' }}>
                                        <a href={issuesMentorResolutionProofUrl} target="_blank" rel="noopener noreferrer" className="feedback-file-link">View / Download uploaded proof</a>
                                        <span className="proof-hint" style={{ marginLeft: '8px', fontSize: '0.85rem', color: '#666' }}>— Choose a new file to replace.</span>
                                    </div>
                                )}
                                <input type="file" accept=".pdf" onChange={e => { setIssuesResolutionProofFile(e.target.files?.[0] || null); setMessage(''); }} style={{ marginTop: '4px', fontSize: '0.9rem' }} />
                                {issuesResolutionProofFile && <span style={{ marginLeft: '8px', fontSize: '0.85rem', color: '#555' }}>{issuesResolutionProofFile.name}</span>}
                            </div>
                        )}
                        <div className="modal-actions">
                            {issuesData.length > 0 && (
                                <button type="button" className="action-button complete" onClick={handleSaveIssuesResolution} disabled={issuesSaving}>{issuesSaving ? 'Saving...' : 'Save resolution'}</button>
                            )}
                            <button type="button" className="action-button cancel" onClick={() => setShowIssuesModal(false)}>Close</button>
                        </div>
                    </div>
                </div>
            )}

            {showIssueResolutionFeedbackModal && issueResolutionFeedbackSession && (
                <div className="counseling-modal-overlay" onClick={() => setShowIssueResolutionFeedbackModal(false)}>
                    <div className="counseling-modal issues-view-modal" onClick={e => e.stopPropagation()}>
                        <div className="counseling-modal-header">
                            <h3>Issue raised & resolution feedback</h3>
                            <button type="button" className="modal-close" onClick={() => setShowIssueResolutionFeedbackModal(false)} aria-label="Close">&times;</button>
                        </div>
                        <p className="issues-modal-session">Session #{issueResolutionFeedbackSession.counseling_id}</p>
                        <div className="issue-resolution-feedback-table-wrap" style={{ margin: '0 24px' }}>
                            <table className="issues-resolution-table">
                                <thead>
                                    <tr>
                                        <th>Description</th>
                                        <th>Date</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {issueResolutionFeedbackRows.map((row, idx) => (
                                        <tr key={row.row_type}>
                                            <td>
                                                <strong className="feedback-row-label">{getIssueResolutionRowLabel(row.row_type)}</strong>
                                                <textarea
                                                    className="resolution-input"
                                                    rows={2}
                                                    value={row.description || ''}
                                                    onChange={e => updateIssueResolutionFeedbackRow(idx, 'description', e.target.value)}
                                                    placeholder="Description"
                                                    style={{ width: '100%', marginTop: '4px' }}
                                                />
                                            </td>
                                            <td>
                                                <input
                                                    type="date"
                                                    className="resolution-date-input"
                                                    value={row.feedback_date || ''}
                                                    onChange={e => updateIssueResolutionFeedbackRow(idx, 'feedback_date', e.target.value)}
                                                />
                                            </td>
                                            <td>
                                                <select
                                                    value={row.status || ''}
                                                    onChange={e => updateIssueResolutionFeedbackRow(idx, 'status', e.target.value)}
                                                    style={{ padding: '4px 8px', minWidth: '80px' }}
                                                >
                                                    <option value="">–</option>
                                                    <option value="WIP">WIP</option>
                                                    <option value="Close">Close</option>
                                                </select>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="issues-resolution-proof-upload" style={{ padding: '0 24px 12px', borderTop: '1px solid #eee' }}>
                            <label className="proof-upload-label">Proof (optional, PDF):</label>
                            {issueResolutionFeedbackSession.issue_resolution_feedback_proof_file_url && (
                                <div style={{ marginBottom: '8px' }}>
                                    <a href={issueResolutionFeedbackSession.issue_resolution_feedback_proof_file_url} target="_blank" rel="noopener noreferrer" className="feedback-file-link">View / Download uploaded proof</a>
                                    <span className="proof-hint" style={{ marginLeft: '8px', fontSize: '0.85rem', color: '#666' }}>— Choose a new file to replace.</span>
                                </div>
                            )}
                            <input
                                type="file"
                                accept=".pdf"
                                onChange={e => { setIssueResolutionFeedbackProofFile(e.target.files?.[0] || null); setMessage(''); }}
                                style={{ marginTop: '4px', fontSize: '0.9rem' }}
                            />
                            {issueResolutionFeedbackProofFile && <span style={{ marginLeft: '8px', fontSize: '0.85rem', color: '#555' }}>{issueResolutionFeedbackProofFile.name}</span>}
                        </div>
                        <div className="modal-actions">
                            <button type="button" className="action-button complete" onClick={saveIssueResolutionFeedback} disabled={issueResolutionFeedbackSaving}>
                                {issueResolutionFeedbackSaving ? 'Saving...' : 'Save'}
                            </button>
                            <button type="button" className="action-button cancel" onClick={() => { setShowIssueResolutionFeedbackModal(false); setIssueResolutionFeedbackProofFile(null); }}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Outcome Modal */}
            {showOutcomeModal && outcomeSession && (
                <div className="counseling-modal-overlay" onClick={() => setShowOutcomeModal(false)}>
                    <div className="counseling-modal outcome-modal" onClick={e => e.stopPropagation()}>
                        <div className="counseling-modal-header">
                            <h3>📋 Set Session Outcome</h3>
                            <button type="button" className="modal-close" onClick={() => setShowOutcomeModal(false)} aria-label="Close">&times;</button>
                        </div>
                        <form onSubmit={handleOutcomeSubmit}>
                            <p className="modal-session-info">Session #{outcomeSession.counseling_id} • {outcomeSession.student_name}</p>
                            <div className="form-group">
                                <label>Outcome Status *</label>
                                <select 
                                    value={outcomeStatus} 
                                    onChange={e => setOutcomeStatus(e.target.value)}
                                    required
                                    className="outcome-select"
                                >
                                    <option value="">Select outcome...</option>
                                    <option value="fully_resolved">✅ Fully Resolved</option>
                                    <option value="partially_resolved">🔶 Partially Resolved</option>
                                    <option value="unresolved">❌ Unresolved</option>
                                    <option value="needs_followup">📅 Needs Follow-up</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Outcome Notes</label>
                                <textarea
                                    value={outcomeNotes}
                                    onChange={e => setOutcomeNotes(e.target.value)}
                                    placeholder="Add notes about the outcome..."
                                    rows={3}
                                />
                            </div>
                            {outcomeStatus === 'needs_followup' && (
                                <div className="form-group">
                                    <label>Suggested Follow-up Date</label>
                                    <input
                                        type="date"
                                        value={followupDate}
                                        onChange={e => setFollowupDate(e.target.value)}
                                        min={new Date().toISOString().split('T')[0]}
                                    />
                                    <small className="form-hint">This will be added to your "Follow-ups Due" list</small>
                                </div>
                            )}
                            <div className="modal-actions">
                                <button type="submit" className="action-button complete" disabled={outcomeSaving}>
                                    {outcomeSaving ? 'Saving...' : 'Save Outcome'}
                                </button>
                                <button type="button" className="action-button cancel" onClick={() => setShowOutcomeModal(false)}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Follow-up Scheduling Modal */}
            {showFollowupModal && followupParentSession && (
                <div className="counseling-modal-overlay" onClick={() => setShowFollowupModal(false)}>
                    <div className="counseling-modal followup-modal" onClick={e => e.stopPropagation()}>
                        <div className="counseling-modal-header">
                            <h3>📅 Schedule Follow-up Session</h3>
                            <button type="button" className="modal-close" onClick={() => setShowFollowupModal(false)} aria-label="Close">&times;</button>
                        </div>
                        <form onSubmit={handleFollowupSubmit}>
                            <p className="modal-session-info">Follow-up for Session #{followupParentSession.counseling_id}</p>
                            <div className="form-group">
                                <label>Session Date & Time *</label>
                                <input
                                    type="datetime-local"
                                    value={followupSessionDate}
                                    onChange={e => setFollowupSessionDate(e.target.value)}
                                    required
                                    min={new Date().toISOString().slice(0, 16)}
                                />
                            </div>
                            <div className="form-group">
                                <label>Venue *</label>
                                <input
                                    type="text"
                                    value={followupVenue}
                                    onChange={e => setFollowupVenue(e.target.value)}
                                    placeholder="e.g., Room 101, Online"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Reason / Notes</label>
                                <textarea
                                    value={followupReason}
                                    onChange={e => setFollowupReason(e.target.value)}
                                    placeholder="Reason for follow-up..."
                                    rows={2}
                                />
                            </div>
                            <div className="form-group checkbox-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={followupUrgent}
                                        onChange={e => setFollowupUrgent(e.target.checked)}
                                    />
                                    <span>Mark as Urgent</span>
                                </label>
                            </div>
                            <div className="modal-actions">
                                <button type="submit" className="action-button complete" disabled={followupSaving}>
                                    {followupSaving ? 'Scheduling...' : 'Schedule Follow-up'}
                                </button>
                                <button type="button" className="action-button cancel" onClick={() => setShowFollowupModal(false)}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CounselingDashboard;
