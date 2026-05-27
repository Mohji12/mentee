import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/StudentDashboardHome.css';
import {
  FaChartLine,
  FaClipboardCheck,
  FaClipboardList,
  FaComments,
  FaGraduationCap,
  FaLightbulb,
  FaRegClock,
  FaTasks,
  FaUser,
} from 'react-icons/fa';

function toInt(n, fallback = 0) {
  const x = Number(n);
  return Number.isFinite(x) ? x : fallback;
}

function formatPercent(n) {
  if (n == null) return '—';
  const x = Number(n);
  if (!Number.isFinite(x)) return '—';
  return `${x.toFixed(2)}%`;
}

const StudentDashboardHome = () => {
  const { student_usn } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchSummary = async () => {
      try {
        setLoading(true);
        setError('');
        const token = sessionStorage.getItem('access_token');
        const res = await fetch(`${API_BASE_URL}/student/${student_usn}/dashboard-summary`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const json = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(json?.detail || 'Failed to load dashboard summary');
        if (!cancelled) setData(json);
      } catch (e) {
        if (!cancelled) setError(e?.message || 'Failed to load dashboard summary');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchSummary();
    return () => {
      cancelled = true;
    };
  }, [student_usn]);

  const cards = useMemo(() => {
    if (!data) return [];

    const attendance = data.attendance || {};
    const academics = data.academics || {};
    const forms = data.forms || {};
    const activities = data.activities || {};
    const meetings = data.meetings || {};
    const counseling = data.counseling || {};
    const experiential = data.experiential || {};

    return [
      {
        key: 'profile',
        title: 'Profile',
        icon: <FaUser />,
        to: `/student/${student_usn}/profile`,
        lines: [
          `Name: ${data.profile?.student_name || '—'}`,
          `USN: ${data.profile?.student_usn || student_usn}`,
          `Program: ${data.profile?.student_program || '—'}`,
          `Semester: ${data.profile?.semester ?? '—'}`,
        ],
      },
      {
        key: 'attendance',
        title: 'Attendance',
        icon: <FaRegClock />,
        to: `/student/${student_usn}/attendance`,
        lines: [
          `Rate: ${formatPercent(attendance.attendance_percentage)}`,
          `Total: ${toInt(attendance.total_records)}`,
          `Present: ${toInt(attendance.present_count)}`,
          `Late: ${toInt(attendance.late_count)}`,
          `Absent: ${toInt(attendance.absent_count)}`,
        ],
      },
      {
        key: 'academics',
        title: 'Academics',
        icon: <FaGraduationCap />,
        to: `/student/${student_usn}/academic-performance`,
        lines: [
          `Semesters filled: ${toInt(academics.semesters_filled)} / ${toInt(academics.max_semesters) || '—'}`,
          `Secondary marksheets: ${academics.has_secondary_marksheets ? 'Uploaded' : 'Pending'}`,
        ],
      },
      {
        key: 'forms',
        title: 'Forms',
        icon: <FaClipboardList />,
        to: `/student/${student_usn}/psychometric`,
        lines: [
          `Psychometric: ${forms.psychometric_completed ? 'Completed' : 'Pending'}`,
          `SWOT/Report: ${forms.swot_completed ? 'Generated' : 'Pending'}`,
          `MCA: ${forms.mca_locked ? 'Submitted (locked)' : 'Not locked'}`,
          `16PF: ${forms.pf16_locked ? 'Submitted (locked)' : 'Not locked'}`,
          `IBP: ${forms.ibp_locked ? 'Submitted (locked)' : 'Not locked'}`,
        ],
        footerLinks: [
          { label: 'MCA', to: `/student/${student_usn}/mca_form` },
          { label: '16PF', to: `/student/${student_usn}/pf16-form` },
          { label: 'IBP', to: `/student/${student_usn}/ibp-form` },
          { label: 'Report', to: `/student/${student_usn}/report` },
        ],
      },
      {
        key: 'activities',
        title: 'Activities',
        icon: <FaTasks />,
        to: `/student/${student_usn}/activities`,
        lines: [
          `Total: ${toInt(activities.total)}`,
          `Approved: ${toInt(activities.approved)}`,
          `Pending: ${toInt(activities.pending)}`,
          `Rejected: ${toInt(activities.rejected)}`,
        ],
        latest: Array.isArray(activities.latest) ? activities.latest : [],
      },
      {
        key: 'meetings',
        title: 'Meetings',
        icon: <FaClipboardCheck />,
        to: `/student/${student_usn}/scheduled_meetings`,
        lines: [
          `Total: ${toInt(meetings.total)}`,
          `Upcoming: ${toInt(meetings.upcoming)}`,
          `Pending: ${toInt(meetings.pending)}`,
        ],
      },
      {
        key: 'support',
        title: 'Student Support',
        icon: <FaComments />,
        to: `/student/${student_usn}/counseling`,
        lines: [
          `Total sessions: ${toInt(counseling.total_sessions)}`,
          `Upcoming: ${toInt(counseling.upcoming_sessions)}`,
          `Urgent: ${toInt(counseling.urgent_sessions)}`,
        ],
      },
      {
        key: 'experiential',
        title: 'Experiential Learning',
        icon: <FaLightbulb />,
        to: `/student/${student_usn}/experiential-learning`,
        lines: [`Total entries: ${toInt(experiential.total)}`],
        latest: Array.isArray(experiential.latest) ? experiential.latest : [],
      },
    ];
  }, [data, student_usn]);

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

  return (
    <div className="sdh-container">
      <div className="sdh-header">
        <div className="sdh-title">
          <h2>
            <FaChartLine /> Dashboard
          </h2>
          <div className="sdh-subtitle">
            {data?.profile?.student_name ? (
              <>
                <span className="sdh-pill">{data.profile.student_name}</span>
                <span className="sdh-pill">{data.profile.student_usn}</span>
              </>
            ) : (
              <span className="sdh-pill">{student_usn}</span>
            )}
          </div>
        </div>
      </div>

      <div className="sdh-grid">
        {cards.map((c) => (
          <div key={c.key} className="sdh-card">
            <div className="sdh-card-header">
              <div className="sdh-card-icon">{c.icon}</div>
              <div className="sdh-card-title">{c.title}</div>
              <Link className="sdh-card-link" to={c.to}>
                View
              </Link>
            </div>

            <div className="sdh-card-body">
              <ul className="sdh-lines">
                {c.lines.map((line, idx) => (
                  <li key={idx}>{line}</li>
                ))}
              </ul>

              {Array.isArray(c.latest) && c.latest.length > 0 && (
                <div className="sdh-latest">
                  <div className="sdh-latest-title">Latest</div>
                  <ul className="sdh-latest-list">
                    {c.latest.slice(0, 3).map((item) => (
                      <li key={item.id} className="sdh-latest-item">
                        <span className="sdh-latest-main">{item.title || item.activity || item.id}</span>
                        {item.status && <span className="sdh-tag">{item.status}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {Array.isArray(c.footerLinks) && c.footerLinks.length > 0 && (
                <div className="sdh-footer-links">
                  {c.footerLinks.map((l) => (
                    <Link key={l.to} to={l.to} className="sdh-mini-link">
                      {l.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StudentDashboardHome;

