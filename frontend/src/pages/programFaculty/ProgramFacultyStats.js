import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../api';
import '../../assets/css/AdminDashboard.css';
import '../../assets/css/LeaderDashboard.css';

const ProgramFacultyStats = () => {
  const { member_id } = useParams();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/program-faculty/${member_id}/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText || 'Failed to load stats');
        return res.json();
      })
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [member_id]);

  if (loading) {
    return (
      <div className="admin-dashboard__main-content leader-dashboard">
        <div className="leader-loading">
          <div className="leader-loading__spinner" aria-hidden />
          <span className="leader-loading__text">Loading dashboard…</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard__main-content leader-dashboard">
        <div className="leader-error" role="alert">{error}</div>
      </div>
    );
  }

  if (!stats) return null;

  const cards = [
    { label: 'Total Students', value: stats.total_students },
    { label: 'Total Mentors', value: stats.total_mentors },
    { label: 'Signed Up', value: stats.signed_up },
    { label: 'Profile Created', value: stats.profile_created },
    { label: 'Form Filled', value: stats.form_filled },
    { label: 'SWOT Generated', value: stats.swot_generated },
    { label: 'Activities', value: stats.activities_generated },
    { label: 'MCA Filled', value: stats.mca_filled },
  ];

  return (
    <div className="admin-dashboard__main-content leader-dashboard">
      <header className="leader-stats__header">
        <h1 className="leader-stats__title">Program Dashboard</h1>
        <p className="leader-stats__subtitle">
          {stats.programs && stats.programs.length > 0 
            ? stats.programs.join(', ') 
            : 'No programs allocated'}
        </p>
      </header>
      <div className="leader-stats-grid">
        {cards.map((c) => (
          <div key={c.label} className="leader-stat-card">
            <div className="leader-stat-card__label">{c.label}</div>
            <div className="leader-stat-card__value">{c.value}</div>
          </div>
        ))}
      </div>
      
      {stats.by_program && stats.by_program.length > 0 && (
        <div className="leader-table-card" style={{ marginTop: '2rem' }}>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: 600 }}>By Program</h2>
          <div className="leader-table-wrapper">
            <table className="leader-table">
              <thead>
                <tr>
                  <th>Program</th>
                  <th>Students</th>
                </tr>
              </thead>
              <tbody>
                {stats.by_program.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.program || '—'}</td>
                    <td>{item.student_count || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgramFacultyStats;
