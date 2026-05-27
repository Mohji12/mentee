import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/AdminCounselingDashboard.css';
import { FaComments, FaUserMd, FaExclamationTriangle, FaCalendarCheck, FaChartLine, FaUsers, FaCheck, FaClock, FaBell, FaFilter, FaSearch, FaEye } from 'react-icons/fa';

const AdminCounselingDashboard = () => {
  const { admin_id } = useParams();
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [mentorStats, setMentorStats] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [urgentPending, setUrgentPending] = useState(null);
  const [escalations, setEscalations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
  
  const [filters, setFilters] = useState({
    status: '',
    mentor_id: '',
    is_urgent: '',
    outcome_status: ''
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchOverview();
    fetchMentorStats();
    fetchUrgentPending();
    fetchEscalations();
  }, [admin_id]);

  useEffect(() => {
    if (activeTab === 'sessions') {
      fetchSessions();
    }
  }, [activeTab, filters]);

  const fetchOverview = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/counseling/overview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setOverview(data);
      }
    } catch (err) {
      console.error('Error fetching overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMentorStats = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/counseling/mentor-stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMentorStats(data);
      }
    } catch (err) {
      console.error('Error fetching mentor stats:', err);
    }
  };

  const fetchSessions = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.mentor_id) params.append('mentor_id', filters.mentor_id);
      if (filters.is_urgent) params.append('is_urgent', filters.is_urgent);
      if (filters.outcome_status) params.append('outcome_status', filters.outcome_status);
      
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/counseling/sessions?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error('Error fetching sessions:', err);
    }
  };

  const fetchUrgentPending = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/counseling/urgent-pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUrgentPending(data);
      }
    } catch (err) {
      console.error('Error fetching urgent pending:', err);
    }
  };

  const fetchEscalations = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/counseling/escalations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setEscalations(data);
      }
    } catch (err) {
      console.error('Error fetching escalations:', err);
    }
  };

  const updateEscalation = async (escalationId, status) => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/counseling/escalations/${escalationId}`, {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      });
      if (response.ok) {
        setMessage(`Escalation ${status} successfully`);
        fetchEscalations();
        fetchOverview();
      }
    } catch (err) {
      setMessage('Failed to update escalation');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      'scheduled': '#17a2b8',
      'completed': '#28a745',
      'cancelled': '#dc3545',
      'rescheduled': '#ffc107',
      'referred': '#9c27b0'
    };
    return colors[status] || '#6c757d';
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

  if (loading) {
    return (
      <div className="acd-loading">
        <div className="acd-spinner"></div>
        <p>Loading counseling oversight...</p>
      </div>
    );
  }

  return (
    <div className="acd-container">
      <div className="acd-header">
        <h1><FaComments /> Student Support Oversight</h1>
        <p>Monitor and manage counseling sessions across all mentors</p>
      </div>

      {message && (
        <div className={`acd-message ${message.includes('Failed') ? 'error' : 'success'}`}>
          {message}
          <button onClick={() => setMessage('')}>×</button>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="acd-tabs">
        <button
          className={`acd-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <FaChartLine /> Overview
        </button>
        <button
          className={`acd-tab ${activeTab === 'mentors' ? 'active' : ''}`}
          onClick={() => setActiveTab('mentors')}
        >
          <FaUserMd /> Mentor Stats
        </button>
        <button
          className={`acd-tab ${activeTab === 'sessions' ? 'active' : ''}`}
          onClick={() => setActiveTab('sessions')}
        >
          <FaCalendarCheck /> All Sessions
        </button>
        <button
          className={`acd-tab ${activeTab === 'urgent' ? 'active' : ''}`}
          onClick={() => setActiveTab('urgent')}
        >
          <FaExclamationTriangle /> Urgent
          {urgentPending && (urgentPending.urgent_sessions.length + urgentPending.overdue_followups.length) > 0 && (
            <span className="acd-tab-badge">
              {urgentPending.urgent_sessions.length + urgentPending.overdue_followups.length}
            </span>
          )}
        </button>
        <button
          className={`acd-tab ${activeTab === 'escalations' ? 'active' : ''}`}
          onClick={() => setActiveTab('escalations')}
        >
          <FaBell /> Escalations
          {escalations.filter(e => e.status === 'open').length > 0 && (
            <span className="acd-tab-badge">{escalations.filter(e => e.status === 'open').length}</span>
          )}
        </button>
      </div>

      <div className="acd-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && overview && (
          <div className="acd-overview">
            <div className="acd-stats-grid">
              <div className="acd-stat-card total">
                <div className="acd-stat-icon"><FaComments /></div>
                <div className="acd-stat-info">
                  <span className="acd-stat-value">{overview.total_sessions}</span>
                  <span className="acd-stat-label">Total Sessions</span>
                </div>
              </div>
              <div className="acd-stat-card success">
                <div className="acd-stat-icon"><FaCheck /></div>
                <div className="acd-stat-info">
                  <span className="acd-stat-value">{overview.completed_sessions}</span>
                  <span className="acd-stat-label">Completed</span>
                </div>
              </div>
              <div className="acd-stat-card info">
                <div className="acd-stat-icon"><FaClock /></div>
                <div className="acd-stat-info">
                  <span className="acd-stat-value">{overview.scheduled_sessions}</span>
                  <span className="acd-stat-label">Scheduled</span>
                </div>
              </div>
              <div className="acd-stat-card warning">
                <div className="acd-stat-icon"><FaExclamationTriangle /></div>
                <div className="acd-stat-info">
                  <span className="acd-stat-value">{overview.urgent_pending}</span>
                  <span className="acd-stat-label">Urgent Pending</span>
                </div>
              </div>
              <div className="acd-stat-card danger">
                <div className="acd-stat-icon"><FaBell /></div>
                <div className="acd-stat-info">
                  <span className="acd-stat-value">{overview.overdue_followups}</span>
                  <span className="acd-stat-label">Overdue Follow-ups</span>
                </div>
              </div>
              <div className="acd-stat-card purple">
                <div className="acd-stat-icon"><FaUsers /></div>
                <div className="acd-stat-info">
                  <span className="acd-stat-value">{overview.active_mentors}</span>
                  <span className="acd-stat-label">Active Mentors</span>
                </div>
              </div>
            </div>

            <div className="acd-overview-cards">
              <div className="acd-overview-card">
                <h3>Completion Rate</h3>
                <div className="acd-completion-rate">
                  <div className="acd-rate-circle">
                    <svg viewBox="0 0 36 36">
                      <path
                        className="acd-rate-bg"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className="acd-rate-fill"
                        strokeDasharray={`${overview.completion_rate}, 100`}
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <span className="acd-rate-value">{overview.completion_rate}%</span>
                  </div>
                </div>
              </div>
              <div className="acd-overview-card">
                <h3>Sessions Summary</h3>
                <div className="acd-summary-list">
                  <div className="acd-summary-item">
                    <span>Referred</span>
                    <span className="acd-summary-value">{overview.referred_sessions}</span>
                  </div>
                  <div className="acd-summary-item">
                    <span>Cancelled</span>
                    <span className="acd-summary-value">{overview.cancelled_sessions}</span>
                  </div>
                  <div className="acd-summary-item">
                    <span>Needs Follow-up</span>
                    <span className="acd-summary-value">{overview.needs_followup}</span>
                  </div>
                  <div className="acd-summary-item">
                    <span>Students Engaged</span>
                    <span className="acd-summary-value">{overview.students_with_sessions}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mentor Stats Tab */}
        {activeTab === 'mentors' && (
          <div className="acd-mentors">
            <h2><FaUserMd /> Mentor-wise Statistics</h2>
            {mentorStats.length > 0 ? (
              <div className="acd-mentors-table-container">
                <table className="acd-mentors-table">
                  <thead>
                    <tr>
                      <th>Mentor</th>
                      <th>Department</th>
                      <th>Total</th>
                      <th>Completed</th>
                      <th>Scheduled</th>
                      <th>Urgent</th>
                      <th>Pending F/U</th>
                      <th>Students</th>
                      <th>Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mentorStats.map((mentor) => (
                      <tr key={mentor.mentor_id}>
                        <td>
                          <div className="acd-mentor-info">
                            <span className="acd-mentor-name">{mentor.mentor_name}</span>
                            <span className="acd-mentor-email">{mentor.mentor_email}</span>
                          </div>
                        </td>
                        <td>{mentor.department || 'N/A'}</td>
                        <td><strong>{mentor.total_sessions}</strong></td>
                        <td className="text-success">{mentor.completed_sessions}</td>
                        <td className="text-info">{mentor.scheduled_sessions}</td>
                        <td className="text-warning">{mentor.urgent_pending}</td>
                        <td className="text-danger">{mentor.pending_followups}</td>
                        <td>{mentor.unique_students}</td>
                        <td>
                          <span className={`acd-rate-badge ${mentor.completion_rate >= 80 ? 'high' : mentor.completion_rate >= 50 ? 'medium' : 'low'}`}>
                            {mentor.completion_rate}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="acd-empty">No mentor statistics available.</p>
            )}
          </div>
        )}

        {/* All Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="acd-sessions">
            <div className="acd-sessions-header">
              <h2><FaCalendarCheck /> All Sessions</h2>
              <button className="acd-filter-btn" onClick={() => setShowFilters(!showFilters)}>
                <FaFilter /> Filters
              </button>
            </div>
            
            {showFilters && (
              <div className="acd-filters">
                <div className="acd-filter-group">
                  <label>Status</label>
                  <select value={filters.status} onChange={e => setFilters({...filters, status: e.target.value})}>
                    <option value="">All</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                    <option value="referred">Referred</option>
                  </select>
                </div>
                <div className="acd-filter-group">
                  <label>Outcome</label>
                  <select value={filters.outcome_status} onChange={e => setFilters({...filters, outcome_status: e.target.value})}>
                    <option value="">All</option>
                    <option value="fully_resolved">Fully Resolved</option>
                    <option value="partially_resolved">Partially Resolved</option>
                    <option value="unresolved">Unresolved</option>
                    <option value="needs_followup">Needs Follow-up</option>
                  </select>
                </div>
                <div className="acd-filter-group">
                  <label>Urgent Only</label>
                  <select value={filters.is_urgent} onChange={e => setFilters({...filters, is_urgent: e.target.value})}>
                    <option value="">All</option>
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                  </select>
                </div>
              </div>
            )}

            {sessions.length > 0 ? (
              <div className="acd-sessions-list">
                {sessions.map((session) => (
                  <div key={session.id} className="acd-session-card">
                    <div className="acd-session-header">
                      <div className="acd-session-id">#{session.counseling_id}</div>
                      <div className="acd-session-badges">
                        <span className="acd-status-badge" style={{ backgroundColor: getStatusColor(session.status) }}>
                          {session.status}
                        </span>
                        {session.is_urgent && <span className="acd-urgent-badge">URGENT</span>}
                        {session.parent_session_id && <span className="acd-followup-badge">Follow-up</span>}
                      </div>
                    </div>
                    <div className="acd-session-details">
                      <div className="acd-session-row">
                        <span><strong>Student:</strong> {session.student_name} ({session.student_usn})</span>
                        <span><strong>Mentor:</strong> {session.mentor_name}</span>
                      </div>
                      <div className="acd-session-row">
                        <span><strong>Date:</strong> {formatDate(session.session_date)}</span>
                        <span><strong>Venue:</strong> {session.venue}</span>
                      </div>
                      {session.outcome_status && (
                        <div className="acd-session-outcome">
                          <strong>Outcome:</strong> {getOutcomeStatusLabel(session.outcome_status)}
                          {session.outcome_notes && <span className="acd-outcome-notes"> — {session.outcome_notes}</span>}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="acd-empty">No sessions found matching the filters.</p>
            )}
          </div>
        )}

        {/* Urgent Tab */}
        {activeTab === 'urgent' && urgentPending && (
          <div className="acd-urgent">
            <h2><FaExclamationTriangle /> Urgent & Attention Required</h2>
            
            {urgentPending.urgent_sessions.length > 0 && (
              <div className="acd-urgent-section">
                <h3>🚨 Urgent Sessions ({urgentPending.urgent_sessions.length})</h3>
                <div className="acd-urgent-list">
                  {urgentPending.urgent_sessions.map((session) => (
                    <div key={session.counseling_id} className="acd-urgent-card urgent">
                      <div className="acd-urgent-header">
                        <span className="acd-urgent-id">#{session.counseling_id}</span>
                        <span className="acd-urgent-badge">URGENT</span>
                      </div>
                      <div className="acd-urgent-details">
                        <p><strong>Student:</strong> {session.student_name} ({session.student_usn})</p>
                        <p><strong>Mentor:</strong> {session.mentor_name}</p>
                        <p><strong>Date:</strong> {formatDate(session.session_date)}</p>
                        <p><strong>Reason:</strong> {session.reason}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {urgentPending.overdue_followups.length > 0 && (
              <div className="acd-urgent-section">
                <h3>⏰ Overdue Follow-ups ({urgentPending.overdue_followups.length})</h3>
                <div className="acd-urgent-list">
                  {urgentPending.overdue_followups.map((session) => (
                    <div key={session.counseling_id} className="acd-urgent-card overdue">
                      <div className="acd-urgent-header">
                        <span className="acd-urgent-id">#{session.counseling_id}</span>
                        <span className="acd-overdue-badge">Overdue by {session.days_overdue} days</span>
                      </div>
                      <div className="acd-urgent-details">
                        <p><strong>Student:</strong> {session.student_name} ({session.student_usn})</p>
                        <p><strong>Mentor:</strong> {session.mentor_name}</p>
                        <p><strong>Follow-up Date:</strong> {formatDate(session.followup_date)}</p>
                        {session.outcome_notes && <p><strong>Notes:</strong> {session.outcome_notes}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {urgentPending.urgent_sessions.length === 0 && urgentPending.overdue_followups.length === 0 && (
              <div className="acd-all-clear">
                <FaCheck className="acd-all-clear-icon" />
                <p>All clear! No urgent items or overdue follow-ups.</p>
              </div>
            )}
          </div>
        )}

        {/* Escalations Tab */}
        {activeTab === 'escalations' && (
          <div className="acd-escalations">
            <h2><FaBell /> Escalation Management</h2>
            
            {escalations.length > 0 ? (
              <div className="acd-escalations-list">
                {escalations.map((escalation) => (
                  <div key={escalation.id} className={`acd-escalation-card ${escalation.status}`}>
                    <div className="acd-escalation-header">
                      <div className="acd-escalation-info">
                        <span className="acd-escalation-id">Session #{escalation.session_id}</span>
                        <span className={`acd-escalation-status ${escalation.status}`}>{escalation.status}</span>
                        <span className={`acd-escalation-priority ${escalation.priority}`}>{escalation.priority}</span>
                      </div>
                      <span className="acd-escalation-date">{formatDate(escalation.created_at)}</span>
                    </div>
                    <div className="acd-escalation-details">
                      <p><strong>Student:</strong> {escalation.student_name}</p>
                      <p><strong>Mentor:</strong> {escalation.mentor_name}</p>
                      <p><strong>Escalated By:</strong> {escalation.escalated_by}</p>
                      <p><strong>Escalated To:</strong> {escalation.escalated_to}</p>
                      {escalation.reason && <p><strong>Reason:</strong> {escalation.reason}</p>}
                      {escalation.resolution_notes && <p><strong>Resolution:</strong> {escalation.resolution_notes}</p>}
                    </div>
                    {escalation.status !== 'resolved' && (
                      <div className="acd-escalation-actions">
                        {escalation.status === 'open' && (
                          <button 
                            className="acd-action-btn acknowledge"
                            onClick={() => updateEscalation(escalation.id, 'acknowledged')}
                          >
                            Acknowledge
                          </button>
                        )}
                        <button 
                          className="acd-action-btn resolve"
                          onClick={() => updateEscalation(escalation.id, 'resolved')}
                        >
                          Mark Resolved
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="acd-all-clear">
                <FaCheck className="acd-all-clear-icon" />
                <p>No escalations found.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminCounselingDashboard;
