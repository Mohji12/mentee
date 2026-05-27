import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../api';
import '../../assets/css/AdminDashboard.css';
import '../../assets/css/LeaderDashboard.css';

const ProgramFacultyStudents = () => {
  const { member_id } = useParams();
  const [students, setStudents] = useState([]);
  const [filters, setFilters] = useState({ programs: [], mentors: [] });
  const [program, setProgram] = useState('');
  const [mentorId, setMentorId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/program-faculty/${member_id}/filters`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText || 'Failed to load filters');
        return res.json();
      })
      .then(setFilters)
      .catch((e) => setError(e.message));
  }, [member_id]);

  useEffect(() => {
    setLoading(true);
    const token = sessionStorage.getItem('access_token');
    const params = new URLSearchParams();
    if (program) params.set('program', program);
    if (mentorId) params.set('mentor_id', mentorId);
    const url = `${API_BASE_URL}/program-faculty/${member_id}/students${params.toString() ? '?' + params.toString() : ''}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText || 'Failed to load students');
        return res.json();
      })
      .then(setStudents)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [member_id, program, mentorId]);

  const renderCell = (value) => (value ? value : <span className="cell-muted">—</span>);

  return (
    <div className="admin-dashboard__main-content leader-dashboard">
      <header className="leader-dashboard__header">
        <h1 className="leader-dashboard__title">Program Students</h1>
        <p className="leader-dashboard__subtitle">All students in your allocated programs. Use filters to narrow by program or mentor.</p>
      </header>

      <div className="leader-filters">
        <div className="leader-filters__group">
          <span className="leader-filters__label">Program</span>
          <select
            className="leader-filters__select"
            value={program}
            onChange={(e) => setProgram(e.target.value)}
            aria-label="Filter by program"
          >
            <option value="">All programs</option>
            {(filters.programs || []).map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
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
        {(program || mentorId) && (
          <button
            type="button"
            className="leader-filters__btn-clear"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setProgram('');
              setMentorId('');
            }}
            aria-label="Clear all filters"
          >
            Clear filters
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
                <p>No students are currently enrolled in your allocated programs.</p>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgramFacultyStudents;
