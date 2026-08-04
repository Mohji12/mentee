import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/StudentDashboardHome.css';
import {
  FaBell,
  FaCalendarAlt,
  FaChartLine,
  FaClipboardCheck,
  FaComments,
  FaGraduationCap,
  FaTasks,
  FaUser,
  FaVideo,
} from 'react-icons/fa';

function toInt(n, fallback = 0) {
  const x = Number(n);
  return Number.isFinite(x) ? x : fallback;
}

function formatPercent(n) {
  if (n == null) return '—';
  const x = Number(n);
  if (!Number.isFinite(x)) return '—';
  return `${x.toFixed(1)}%`;
}

function formatDate(d) {
  if (!d) return '—';
  try {
    return new Date(d).toLocaleString(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  } catch {
    return '—';
  }
}

const ACTIVITY_PIE_COLORS = ['#22c55e', '#f59e0b', '#ef4444'];

const StudentDashboardHome = () => {
  const { student_usn } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);

  const fetchSummary = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const token = sessionStorage.getItem('access_token');
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/dashboard-summary`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(json?.detail || 'Failed to load dashboard summary');
      setData(json);
    } catch (e) {
      setError(e?.message || 'Failed to load dashboard summary');
    } finally {
      setLoading(false);
    }
  }, [student_usn]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  const markRead = async (id) => {
    const token = sessionStorage.getItem('access_token');
    await fetch(`${API_BASE_URL}/student/${student_usn}/notifications/${id}/read`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchSummary();
  };

  const markAllRead = async () => {
    const token = sessionStorage.getItem('access_token');
    await fetch(`${API_BASE_URL}/student/${student_usn}/notifications/read-all`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchSummary();
  };

  const activityPieData = useMemo(() => {
    if (!data?.activities) return [];
    const a = data.activities;
    return [
      { name: 'Completed', value: toInt(a.approved) },
      { name: 'Pending', value: toInt(a.pending) },
      { name: 'Rejected', value: toInt(a.rejected) },
    ].filter((x) => x.value > 0);
  }, [data]);

  const academicBarData = useMemo(() => {
    const scores = data?.academic_performance?.semester_scores || [];
    return scores.map((s) => ({
      name: `Sem ${s.semester}`,
      score: s.average_grade_score != null ? Number(s.average_grade_score) * 10 : 0,
    }));
  }, [data]);

  const attendanceTrend = data?.attendance?.trend || [];
  const joinMeetingLink = data?.meetings?.upcoming_list?.[0]?.google_meet_link;

  if (loading) {
    return (
      <div className="sdh-container">
        <div className="sdh-loading">Loading dashboard…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sdh-container">
        <div className="sdh-error">{error}</div>
      </div>
    );
  }

  const profile = data?.profile || {};
  const cards = data?.summary_cards || [];

  return (
    <div className="sdh-container sdh-enhanced">
      <div className="sdh-header">
        <div className="sdh-title">
          <h2>
            <FaChartLine /> Dashboard
          </h2>
          <div className="sdh-subtitle">
            {profile.profile_photo_url ? (
              <img src={profile.profile_photo_url} alt="Profile" className="sdh-profile-photo" />
            ) : (
              <div className="sdh-profile-photo-placeholder">
                <FaUser />
              </div>
            )}
            {profile.student_name && <span className="sdh-pill">{profile.student_name}</span>}
            <span className="sdh-pill">{profile.student_usn || student_usn}</span>
            {profile.semester != null && (
              <span className="sdh-pill sdh-pill-muted">Semester {profile.semester}</span>
            )}
            {profile.assigned_mentor_name && (
              <span className="sdh-pill sdh-pill-muted">Mentor: {profile.assigned_mentor_name}</span>
            )}
          </div>
        </div>
      </div>

      <div className="sdh-quick-actions">
        {joinMeetingLink ? (
          <a href={joinMeetingLink} target="_blank" rel="noopener noreferrer" className="sdh-quick-btn">
            <FaVideo /> Join Meeting
          </a>
        ) : (
          <Link to={`/student/${student_usn}/scheduled_meetings`} className="sdh-quick-btn">
            <FaVideo /> Meetings
          </Link>
        )}
        <Link to={`/student/${student_usn}/attendance`} className="sdh-quick-btn">
          <FaClipboardCheck /> View Attendance
        </Link>
        <Link to={`/student/${student_usn}/academic-performance`} className="sdh-quick-btn">
          <FaGraduationCap /> Upload Documents
        </Link>
        <Link to={`/student/${student_usn}/activities`} className="sdh-quick-btn">
          <FaTasks /> View Activities
        </Link>
        <Link to={`/student/${student_usn}/psychometric`} className="sdh-quick-btn">
          <FaChartLine /> Complete Assessment
        </Link>
        <Link to={`/student/${student_usn}/counseling`} className="sdh-quick-btn">
          <FaComments /> Contact Mentor
        </Link>
      </div>

      <div className="sdh-summary-row">
        {cards.map((c) => (
          <div key={c.key} className="sdh-summary-card">
            <div className="sdh-summary-card-title">{c.title}</div>
            <div className="sdh-summary-card-value">{c.current_value}</div>
            <div className="sdh-summary-card-status">{c.status}</div>
            <div className="sdh-summary-card-updated">Updated: {formatDate(c.last_updated)}</div>
          </div>
        ))}
      </div>

      <div className="sdh-widgets-row sdh-widgets-row-2">
        <section className="sdh-widget">
          <h3>Attendance Trend</h3>
          <p className="sdh-widget-meta">
            Overall {formatPercent(data?.attendance?.overall_attendance_percentage)} · Monthly & semester views
          </p>
          <div className="sdh-chart-wrap">
            {attendanceTrend.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={attendanceTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(v) => `${v}%`} />
                  <Line type="monotone" dataKey="percentage" stroke="#6366f1" strokeWidth={2} dot />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="sdh-empty-chart">No attendance history yet.</p>
            )}
          </div>
          <ul className="sdh-mini-stats">
            <li>Present: {toInt(data?.attendance?.present_count)}</li>
            <li>Late: {toInt(data?.attendance?.late_count)}</li>
            <li>Absent: {toInt(data?.attendance?.absent_count)}</li>
          </ul>
        </section>

        <section className="sdh-widget">
          <h3>Activity Completion</h3>
          <p className="sdh-widget-meta">
            {formatPercent(data?.activities?.completion_percentage)} complete ·{' '}
            <Link to={`/student/${student_usn}/activities`}>View details</Link>
          </p>
          <div className="sdh-chart-wrap">
            {activityPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={activityPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {activityPieData.map((_, i) => (
                      <Cell key={i} fill={ACTIVITY_PIE_COLORS[i % ACTIVITY_PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="sdh-empty-chart">No activities assigned.</p>
            )}
          </div>
        </section>
      </div>

      <div className="sdh-widgets-row sdh-widgets-row-3">
        <section className="sdh-widget">
          <h3>Semester Progress</h3>
          <p className="sdh-widget-meta">{data?.semester_progress?.remaining_duration_label}</p>
          <div className="sdh-progress-bar">
            <div
              className="sdh-progress-fill"
              style={{ width: `${Math.min(100, toInt(data?.semester_progress?.completion_percentage))}%` }}
            />
          </div>
          <p className="sdh-progress-label">
            Semester {data?.semester_progress?.current_semester ?? '—'} of{' '}
            {data?.semester_progress?.max_semesters ?? '—'} (
            {formatPercent(data?.semester_progress?.completion_percentage)})
          </p>
        </section>

        <section className="sdh-widget">
          <h3>Employability Score</h3>
          <div className="sdh-score-display">
            {data?.employability?.latest_score ?? '—'}
          </div>
          <p className="sdh-widget-meta">
            Level: {data?.employability?.performance_level || 'Not assessed'}
          </p>
          {data?.employability?.score_improvement != null && (
            <p className="sdh-widget-meta">
              Change vs previous: {data.employability.score_improvement > 0 ? '+' : ''}
              {data.employability.score_improvement}
            </p>
          )}
        </section>

        <section className="sdh-widget">
          <h3>Academic Performance</h3>
          <p className="sdh-widget-meta">
            Overall {formatPercent(data?.academic_performance?.overall_percentage)}
            {data?.academic_performance?.internal_marks_summary
              ? ` · ${data.academic_performance.internal_marks_summary}`
              : ''}
          </p>
          <div className="sdh-chart-wrap sdh-chart-sm">
            {academicBarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={academicBarData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="score" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="sdh-empty-chart">No academic records yet.</p>
            )}
          </div>
        </section>
      </div>

      <div className="sdh-widgets-row sdh-widgets-row-3">
        <section className="sdh-widget">
          <h3>Mentoring Sessions</h3>
          <ul className="sdh-stat-list">
            <li>Total: {toInt(data?.meetings?.total)}</li>
            <li>Upcoming: {toInt(data?.meetings?.upcoming)}</li>
            <li>Completed: {toInt(data?.meetings?.completed)}</li>
            <li>Missed: {toInt(data?.meetings?.missed)}</li>
          </ul>
          <ul className="sdh-meeting-list">
            {(data?.meetings?.upcoming_list || []).map((m) => (
              <li key={m.meeting_id}>
                <strong>{formatDate(m.meeting_date)}</strong>
                <span>{m.mentor_name || 'Mentor'}</span>
                <span className="sdh-tag">{m.status || 'scheduled'}</span>
              </li>
            ))}
          </ul>
          <Link to={`/student/${student_usn}/scheduled_meetings`} className="sdh-widget-link">
            All meetings
          </Link>
        </section>

        <section className="sdh-widget">
          <h3>Alumni Sessions</h3>
          <ul className="sdh-stat-list">
            <li>Total: {toInt(data?.alumni_sessions?.total)}</li>
            <li>Attended: {toInt(data?.alumni_sessions?.attended)}</li>
            <li>Missed: {toInt(data?.alumni_sessions?.missed)}</li>
            <li>Upcoming: {toInt(data?.alumni_sessions?.upcoming)}</li>
          </ul>
        </section>

        <section className="sdh-widget">
          <h3>Expert Sessions</h3>
          <ul className="sdh-stat-list">
            <li>Industry: {toInt(data?.expert_sessions?.industry_total)}</li>
            <li>Foreign: {toInt(data?.expert_sessions?.foreign_total)}</li>
            <li>Attended: {toInt(data?.expert_sessions?.attended)}</li>
            <li>Upcoming: {toInt(data?.expert_sessions?.upcoming)}</li>
            <li>Completed: {toInt(data?.expert_sessions?.completed)}</li>
          </ul>
        </section>
      </div>

      <div className="sdh-widgets-row sdh-widgets-row-2">
        <section className="sdh-widget">
          <div className="sdh-widget-head">
            <h3>
              <FaBell /> Notifications
            </h3>
            {toInt(data?.notifications?.unread_count) > 0 && (
              <button type="button" className="sdh-text-btn" onClick={markAllRead}>
                Mark all read
              </button>
            )}
          </div>
          <ul className="sdh-notif-list">
            {(data?.notifications?.items || []).length === 0 && (
              <li className="sdh-notif-empty">No notifications yet.</li>
            )}
            {(data?.notifications?.items || []).map((n) => (
              <li
                key={n.id}
                className={n.is_read ? 'sdh-notif sdh-notif-read' : 'sdh-notif sdh-notif-unread'}
              >
                <div className="sdh-notif-title">{n.title}</div>
                <div className="sdh-notif-msg">{n.message}</div>
                <div className="sdh-notif-meta">
                  <span>{n.category}</span>
                  <span>{formatDate(n.created_at)}</span>
                  {!n.is_read && (
                    <button type="button" className="sdh-text-btn" onClick={() => markRead(n.id)}>
                      Mark read
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="sdh-widget">
          <h3>
            <FaCalendarAlt /> Upcoming Events
          </h3>
          <ul className="sdh-events-list">
            {(data?.upcoming_events || []).length === 0 && (
              <li className="sdh-notif-empty">No upcoming events.</li>
            )}
            {(data?.upcoming_events || []).map((ev, idx) => (
              <li key={`${ev.event_type}-${idx}`} className="sdh-event-item">
                <span className="sdh-tag">{ev.event_type.replace('_', ' ')}</span>
                <strong>{ev.title}</strong>
                <span>{formatDate(ev.event_date)}</span>
                {ev.status && <span className="sdh-event-status">{ev.status}</span>}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="sdh-widget sdh-widget-wide">
        <h3>Academic Records</h3>
        <ul className="sdh-stat-list">
          <li>Total uploaded: {toInt(data?.academic_records?.total_uploaded)}</li>
          <li>Missing: {toInt(data?.academic_records?.missing_count)}</li>
          <li>Pending verification: {toInt(data?.academic_records?.pending_verification)}</li>
          <li>Verified: {toInt(data?.academic_records?.verified)}</li>
          <li>Rejected: {toInt(data?.academic_records?.rejected)}</li>
        </ul>
        <Link to={`/student/${student_usn}/academic-performance`} className="sdh-widget-link">
          Manage academic records
        </Link>
      </section>

      <section className="sdh-widget sdh-widget-wide">
        <h3>Psychometric Assessment</h3>
        <p>
          Status: <strong>{data?.psychometric?.status}</strong>
          {data?.psychometric?.last_assessment_date && (
            <> · Last: {formatDate(data.psychometric.last_assessment_date)}</>
          )}
        </p>
        <Link to={`/student/${student_usn}/psychometric`} className="sdh-widget-link">
          Open assessment
        </Link>
      </section>

      <div className="sdh-legacy-grid">
        <p className="sdh-legacy-title">Quick links</p>
        <div className="sdh-grid">
          {[
            { key: 'profile', title: 'Profile', to: `/student/${student_usn}/profile` },
            { key: 'forms', title: 'Forms & Reports', to: `/student/${student_usn}/report` },
            { key: 'support', title: 'Student Support', to: `/student/${student_usn}/counseling` },
            {
              key: 'experiential',
              title: 'Experiential Learning',
              to: `/student/${student_usn}/experiential-learning`,
            },
          ].map((item) => (
            <Link key={item.key} to={item.to} className="sdh-legacy-link">
              {item.title}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StudentDashboardHome;
