import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../api';
import '../../assets/css/AdminDashboard.css';
import '../../assets/css/LeaderDashboard.css';

const WorkingCommitteeDepartments = () => {
  const { member_id } = useParams();
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/working-committee/${member_id}/departments`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText || 'Failed to load departments');
        return res.json();
      })
      .then((data) => setDepartments(data.departments || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [member_id]);

  if (loading) {
    return (
      <div className="admin-dashboard__main-content leader-dashboard">
        <div className="leader-loading">
          <div className="leader-loading__spinner" aria-hidden />
          <span className="leader-loading__text">Loading departments…</span>
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

  return (
    <div className="admin-dashboard__main-content leader-dashboard">
      <header className="leader-stats__header">
        <h1 className="leader-stats__title">My Allocated Departments</h1>
        <p className="leader-stats__subtitle">
          Departments assigned to you for student oversight and management.
        </p>
      </header>

      {departments.length === 0 ? (
        <div className="leader-empty">
          <p className="leader-empty__title">No departments allocated</p>
          <p>Please contact the administrator to assign departments to your account.</p>
        </div>
      ) : (
        <section className="leader-dept-section">
          <div className="leader-count" style={{ marginBottom: '1rem' }}>
            <span className="leader-count__number">{departments.length}</span>
            <span>department{departments.length !== 1 ? 's' : ''} allocated</span>
          </div>
          <div className="leader-table-card">
            <table className="leader-dept-table">
              <thead>
                <tr>
                  <th>Department</th>
                  <th style={{ width: '120px' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((dept, index) => (
                  <tr key={dept || index}>
                    <td>{dept || '—'}</td>
                    <td>
                      <span
                        style={{
                          display: 'inline-block',
                          padding: '0.25rem 0.6rem',
                          borderRadius: '6px',
                          fontSize: '0.8125rem',
                          fontWeight: 600,
                          backgroundColor: '#eff6ff',
                          color: '#1e40af',
                        }}
                      >
                        Active
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
};

export default WorkingCommitteeDepartments;
