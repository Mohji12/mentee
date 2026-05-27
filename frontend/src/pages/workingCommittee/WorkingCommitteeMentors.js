import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../api';
import '../../assets/css/AdminDashboard.css';
import '../../assets/css/LeaderDashboard.css';

const WorkingCommitteeMentors = () => {
  const { member_id } = useParams();
  const [mentors, setMentors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    mentor_id: '',
    mentor_name: '',
    mentor_email: '',
    mentor_phoneno: '',
    mentor_department: '',
  });
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState('');
  const [createSuccess, setCreateSuccess] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    // Fetch departments for dropdown
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/working-committee/${member_id}/filters`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setDepartments(data.departments || []))
      .catch(() => setDepartments([]));
  }, [member_id]);

  const fetchMentors = () => {
    setLoading(true);
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/working-committee/${member_id}/mentors`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(res.statusText || 'Failed to load mentors');
        }
        return res.json();
      })
      .then(setMentors)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMentors();
  }, [member_id]);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setCreateLoading(true);
    setCreateError('');
    setCreateSuccess('');

    if (!createForm.mentor_id || !createForm.mentor_name || !createForm.mentor_email || !createForm.mentor_phoneno || !createForm.mentor_department) {
      setCreateError('Please fill in all required fields.');
      setCreateLoading(false);
      return;
    }

    const token = sessionStorage.getItem('access_token');
    if (!token) {
      setCreateError('Authentication token not found. Please log in again.');
      setCreateLoading(false);
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/working-committee/${member_id}/mentors`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(createForm),
      });

      let data;
      try {
        const text = await res.text();
        data = text ? JSON.parse(text) : {};
      } catch (jsonError) {
        throw new Error(`Server error (${res.status}): ${res.statusText}`);
      }

      if (!res.ok) {
        throw new Error(data.detail || data.message || `Failed to create mentor (${res.status})`);
      }

      setCreateSuccess(`Mentor created successfully! ${data.email_sent ? 'Email sent.' : 'Email failed to send.'}`);
      setCreateForm({ mentor_id: '', mentor_name: '', mentor_email: '', mentor_phoneno: '', mentor_department: '' });
      setTimeout(() => {
        setShowCreateModal(false);
        setCreateSuccess('');
        fetchMentors();
      }, 2000);
    } catch (e) {
      console.error('Create mentor error:', e);
      setCreateError(e.message || 'Failed to create mentor. Please try again.');
    } finally {
      setCreateLoading(false);
    }
  };

  const handleDelete = async (mentorId, studentCount) => {
    const message = studentCount > 0
      ? `Are you sure you want to delete mentor "${mentorId}"?\n\nThis mentor has ${studentCount} assigned student(s). They will be unassigned from this mentor.\n\nThis action cannot be undone.`
      : `Are you sure you want to delete mentor "${mentorId}"?\n\nThis action cannot be undone.`;

    if (!window.confirm(message)) {
      return;
    }
    setDeletingId(mentorId);
    const token = sessionStorage.getItem('access_token');
    try {
      const res = await fetch(`${API_BASE_URL}/working-committee/${member_id}/mentors/${mentorId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to delete mentor');
      }
      const successMsg = data.students_unassigned > 0
        ? `Mentor "${mentorId}" deleted successfully. ${data.students_unassigned} student(s) have been unassigned.`
        : `Mentor "${mentorId}" deleted successfully.`;
      alert(successMsg);
      fetchMentors();
    } catch (e) {
      alert(`Error: ${e.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const renderCell = (value) => (value ? value : <span className="cell-muted">—</span>);

  return (
    <div className="admin-dashboard__main-content leader-dashboard">
      <header className="leader-dashboard__header">
        <h1 className="leader-dashboard__title">All Mentors</h1>
        <p className="leader-dashboard__subtitle">Manage mentors in your allocated departments.</p>
      </header>

      {error && !mentors.length && (
        <div className="leader-error" role="alert">
          {error}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div className="leader-count">
          <span className="leader-count__number">{loading ? '…' : mentors.length}</span>
          <span>mentor{mentors.length !== 1 ? 's' : ''} total</span>
        </div>
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setShowCreateModal(true);
          }}
          disabled={loading}
          style={{
            padding: '0.625rem 1.25rem',
            fontSize: '0.875rem',
            fontWeight: 600,
            color: '#fff',
            backgroundColor: loading ? '#94a3b8' : '#3b82f6',
            border: '1px solid',
            borderColor: loading ? '#94a3b8' : '#3b82f6',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
            pointerEvents: loading ? 'none' : 'auto',
            zIndex: 10,
            position: 'relative',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          }}
        >
          + Create Mentor
        </button>
      </div>

      {loading ? (
        <div className="leader-loading">
          <div className="leader-loading__spinner" aria-hidden />
          <span className="leader-loading__text">Loading mentors…</span>
        </div>
      ) : (
        <div className="leader-table-card">
          <div className="leader-table-wrapper">
            {mentors.length === 0 ? (
              <div className="leader-empty">
                <p className="leader-empty__title">No mentors found</p>
                <p>No mentors are currently in the system.</p>
              </div>
            ) : (
              <table className="leader-table">
                <thead>
                  <tr>
                    <th>Mentor ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Department</th>
                    <th>Students Assigned</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {mentors.map((m) => (
                    <tr key={m.mentor_id}>
                      <td>{renderCell(m.mentor_id)}</td>
                      <td>{renderCell(m.mentor_name)}</td>
                      <td>{renderCell(m.mentor_email)}</td>
                      <td>{renderCell(m.mentor_phoneno)}</td>
                      <td>{renderCell(m.mentor_department)}</td>
                      <td>
                        <span
                          style={{
                            display: 'inline-block',
                            padding: '0.25rem 0.6rem',
                            borderRadius: '6px',
                            fontSize: '0.8125rem',
                            fontWeight: 600,
                            backgroundColor: m.student_count > 0 ? '#eff6ff' : '#f1f5f9',
                            color: m.student_count > 0 ? '#1e40af' : '#64748b',
                          }}
                        >
                          {m.student_count || 0}
                        </span>
                      </td>
                      <td>
                        <button
                          onClick={() => handleDelete(m.mentor_id, m.student_count)}
                          disabled={deletingId === m.mentor_id}
                          style={{
                            padding: '0.375rem 0.75rem',
                            fontSize: '0.8125rem',
                            backgroundColor: '#ef4444',
                            color: '#fff',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: deletingId === m.mentor_id ? 'not-allowed' : 'pointer',
                            opacity: deletingId === m.mentor_id ? 0.6 : 1,
                          }}
                          title="Delete mentor (students will be unassigned)"
                        >
                          {deletingId === m.mentor_id ? 'Deleting...' : 'Delete'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Create Mentor Modal */}
      {showCreateModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
          onClick={() => !createLoading && setShowCreateModal(false)}
        >
          <div
            className="leader-table-card"
            style={{
              maxWidth: '500px',
              width: '90%',
              maxHeight: '90vh',
              overflowY: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600 }}>Create New Mentor</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  disabled={createLoading}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '1.5rem',
                    cursor: 'pointer',
                    color: '#64748b',
                  }}
                >
                  ×
                </button>
              </div>
              <form onSubmit={handleCreateSubmit}>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.875rem' }}>
                    Mentor ID *
                  </label>
                  <input
                    type="text"
                    required
                    value={createForm.mentor_id}
                    onChange={(e) => setCreateForm({ ...createForm, mentor_id: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '0.875rem',
                    }}
                    placeholder="e.g., MENT001"
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.875rem' }}>
                    Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={createForm.mentor_name}
                    onChange={(e) => setCreateForm({ ...createForm, mentor_name: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '0.875rem',
                    }}
                    placeholder="Full name"
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.875rem' }}>
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={createForm.mentor_email}
                    onChange={(e) => setCreateForm({ ...createForm, mentor_email: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '0.875rem',
                    }}
                    placeholder="mentor@example.com"
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.875rem' }}>
                    Phone *
                  </label>
                  <input
                    type="tel"
                    required
                    value={createForm.mentor_phoneno}
                    onChange={(e) => setCreateForm({ ...createForm, mentor_phoneno: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '0.875rem',
                    }}
                    placeholder="+91XXXXXXXXXX"
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600, fontSize: '0.875rem' }}>
                    Department *
                  </label>
                  <select
                    required
                    value={createForm.mentor_department}
                    onChange={(e) => setCreateForm({ ...createForm, mentor_department: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      fontSize: '0.875rem',
                      backgroundColor: '#fff',
                    }}
                  >
                    <option value="">-- Select Department --</option>
                    {departments.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
                <div style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '8px', fontSize: '0.8125rem', color: '#475569' }}>
                  <strong>Note:</strong> Password will be auto-generated as <code>{createForm.mentor_id && createForm.mentor_name ? `${createForm.mentor_id}@${createForm.mentor_name.substring(0, 3).toUpperCase()}` : 'MENTOR_ID@FIRST3'}</code> and sent via email.
                </div>
                {createError && (
                  <div style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#fef2f2', color: '#dc2626', borderRadius: '8px', fontSize: '0.875rem' }}>
                    {createError}
                  </div>
                )}
                {createSuccess && (
                  <div style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#f0fdf4', color: '#16a34a', borderRadius: '8px', fontSize: '0.875rem' }}>
                    {createSuccess}
                  </div>
                )}
                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    disabled={createLoading}
                    className="leader-filters__btn-clear"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createLoading}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#3b82f6',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: createLoading ? 'not-allowed' : 'pointer',
                      opacity: createLoading ? 0.6 : 1,
                      fontWeight: 500,
                    }}
                  >
                    {createLoading ? 'Creating...' : 'Create Mentor'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkingCommitteeMentors;
