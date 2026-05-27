import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../api';
import '../../assets/css/AdminDashboard.css';
import '../../assets/css/LeaderDashboard.css';

const HODStudents = () => {
  const { member_id } = useParams();
  const [students, setStudents] = useState([]);
  const [filters, setFilters] = useState({ mentors: [] });
  const [mentorId, setMentorId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mentorModal, setMentorModal] = useState({ open: false, student: null, selectedMentorId: '' });
  const [patchLoading, setPatchLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/hod/${member_id}/filters`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText || 'Failed to load filters');
        return res.json();
      })
      .then(setFilters)
      .catch((e) => setError(e.message));
  }, [member_id]);

  const fetchStudents = () => {
    setLoading(true);
    const token = sessionStorage.getItem('access_token');
    const params = new URLSearchParams();
    if (mentorId) params.set('mentor_id', mentorId);
    const url = `${API_BASE_URL}/hod/${member_id}/students${params.toString() ? '?' + params.toString() : ''}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText || 'Failed to load students');
        return res.json();
      })
      .then(setStudents)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStudents();
  }, [member_id, mentorId]);

  const openMentorModal = (student) => {
    setMentorModal({
      open: true,
      student: { usn: student.student_usn, name: student.student_name },
      selectedMentorId: student.assigned_mentor || '',
    });
    setSuccessMessage('');
  };

  const closeMentorModal = () => {
    setMentorModal({ open: false, student: null, selectedMentorId: '' });
    setPatchLoading(false);
  };

  const submitAssignMentor = () => {
    const { student, selectedMentorId } = mentorModal;
    if (!student) return;
    setPatchLoading(true);
    const token = sessionStorage.getItem('access_token');
    const body = { mentor_id: selectedMentorId && selectedMentorId.trim() ? selectedMentorId.trim() : null };
    fetch(`${API_BASE_URL}/hod/${member_id}/students/${student.usn}/mentor`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((j) => Promise.reject(new Error(j.detail || res.statusText)));
        return res.json();
      })
      .then(() => {
        setSuccessMessage('Mentor updated successfully.');
        closeMentorModal();
        fetchStudents();
      })
      .catch((e) => setError(e.message))
      .finally(() => setPatchLoading(false));
  };

  const renderCell = (value) => (value ? value : <span className="cell-muted">—</span>);

  return (
    <div className="admin-dashboard__main-content leader-dashboard">
      <header className="leader-dashboard__header">
        <h1 className="leader-dashboard__title">Department Students</h1>
        <p className="leader-dashboard__subtitle">All students in your department. Use filters to narrow by mentor.</p>
      </header>

      <div className="leader-filters">
        <div className="leader-filters__group">
          <span className="leader-filters__label">Mentor</span>
          <select
            className="leader-filters__select"
            value={mentorId}
            onChange={(e) => setMentorId(e.target.value)}
            aria-label="Filter by mentor"
          >
            <option value="">All mentors</option>
            {(filters.mentors || []).map((m) => (
              <option key={m.mentor_id} value={m.mentor_id}>
                {m.mentor_name} {m.department ? `(${m.department})` : ''}
              </option>
            ))}
          </select>
        </div>
        {mentorId && (
          <button
            type="button"
            className="leader-filters__btn-clear"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setMentorId('');
            }}
            aria-label="Clear mentor filter"
          >
            Clear filter
          </button>
        )}
      </div>

      {error && !students.length && (
        <div className="leader-error" role="alert">
          {error}
        </div>
      )}

      <div className="leader-count">
        <span className="leader-count__number">{loading ? '…' : students.length}</span>
        <span>student{students.length !== 1 ? 's' : ''} shown</span>
      </div>

      {loading ? (
        <div className="leader-loading">
          <div className="leader-loading__spinner" aria-hidden />
          <span className="leader-loading__text">Loading students…</span>
        </div>
      ) : (
        <div className="leader-table-card">
          <div className="leader-table-wrapper">
            {students.length === 0 ? (
              <div className="leader-empty">
                <p className="leader-empty__title">No students found</p>
                <p>No students are currently assigned to mentors in this department.</p>
              </div>
            ) : (
              <table className="leader-table">
                <thead>
                  <tr>
                    <th>USN</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Program</th>
                    <th>Semester</th>
                    <th>Mentor</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s) => (
                    <tr key={s.student_usn}>
                      <td>{renderCell(s.student_usn)}</td>
                      <td>{renderCell(s.student_name)}</td>
                      <td>{renderCell(s.email)}</td>
                      <td>{renderCell(s.phone)}</td>
                      <td>{renderCell(s.program)}</td>
                      <td>{renderCell(s.semester)}</td>
                      <td>{renderCell(s.ass_mentor)}</td>
                      <td className="status-cell">{renderCell(s.status)}</td>
                      <td>
                        <button
                          type="button"
                          className="leader-table__action-btn"
                          onClick={() => openMentorModal(s)}
                          aria-label={s.ass_mentor === 'No mentor assigned' ? 'Assign mentor' : 'Edit mentor'}
                        >
                          {s.ass_mentor === 'No mentor assigned' ? 'Assign mentor' : 'Edit mentor'}
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

      {successMessage && (
        <div className="leader-success" role="status">
          {successMessage}
        </div>
      )}

      {mentorModal.open && mentorModal.student && (
        <div className="leader-modal-overlay" onClick={closeMentorModal} role="dialog" aria-modal="true" aria-labelledby="hod-assign-mentor-title">
          <div className="leader-modal" onClick={(e) => e.stopPropagation()}>
            <h2 id="hod-assign-mentor-title">Assign mentor – {mentorModal.student.name} ({mentorModal.student.usn})</h2>
            <div className="leader-modal__field">
              <label htmlFor="hod-mentor-select">Mentor</label>
              <select
                id="hod-mentor-select"
                value={mentorModal.selectedMentorId}
                onChange={(e) => setMentorModal((m) => ({ ...m, selectedMentorId: e.target.value }))}
              >
                <option value="">No mentor (unassign)</option>
                {(filters.mentors || []).map((m) => (
                  <option key={m.mentor_id} value={m.mentor_id}>
                    {m.mentor_name} {m.department ? `(${m.department})` : ''}
                  </option>
                ))}
              </select>
            </div>
            <div className="leader-modal__actions">
              <button type="button" className="leader-modal__btn-cancel" onClick={closeMentorModal} disabled={patchLoading}>
                Cancel
              </button>
              <button type="button" className="leader-modal__btn-submit" onClick={submitAssignMentor} disabled={patchLoading}>
                {patchLoading ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HODStudents;
