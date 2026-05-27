import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../api';
import { FaTrash, FaPlus } from 'react-icons/fa';
import '../../assets/css/AdminStudents.css';
import '../../assets/css/LeaderDashboard.css';

const LeaderMentors = () => {
    const { leader_id } = useParams();
    const [mentors, setMentors] = useState([]);
    const [filters, setFilters] = useState({ departments: [] });
    const [department, setDepartment] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [saving, setSaving] = useState(false);
    const [newMentor, setNewMentor] = useState({
        mentor_id: '',
        mentor_name: '',
        mentor_department: '',
        mentor_email: '',
        mentor_phoneno: '',
        mentor_password: ''
    });

    const fetchFilters = () => {
        const token = sessionStorage.getItem('access_token');
        fetch(`${API_BASE_URL}/leader/${leader_id}/filters`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => {
                if (!res.ok) throw new Error(res.statusText || 'Failed to load filters');
                return res.json();
            })
            .then(setFilters)
            .catch((e) => setError(e.message));
    };

    const fetchMentors = () => {
        setLoading(true);
        const token = sessionStorage.getItem('access_token');
        const params = new URLSearchParams();
        if (department) {
            params.set('department', department);
        }
        const url = `${API_BASE_URL}/leader/${leader_id}/mentors${params.toString() ? '?' + params.toString() : ''}`;
        fetch(url, { headers: { Authorization: `Bearer ${token}` } })
            .then((res) => {
                if (!res.ok) throw new Error(res.statusText || 'Failed to load mentors');
                return res.json();
            })
            .then(setMentors)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchFilters();
    }, [leader_id]);

    useEffect(() => {
        fetchMentors();
    }, [leader_id, department]);

    const handleDelete = (mentorId) => {
        if (!window.confirm(`Are you sure you want to delete mentor ${mentorId}?`)) return;

        const token = sessionStorage.getItem('access_token');
        fetch(`${API_BASE_URL}/leader/${leader_id}/mentors/${mentorId}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => {
                if (!res.ok) throw new Error('Failed to delete mentor');
                return res.json();
            })
            .then(() => {
                fetchMentors();
                fetchFilters();
            })
            .catch((e) => alert(e.message));
    };

    const handleCreateMentor = (e) => {
        e.preventDefault();
        setSaving(true);
        const token = sessionStorage.getItem('access_token');
        fetch(`${API_BASE_URL}/leader/${leader_id}/mentors`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newMentor)
        })
            .then((res) => {
                if (!res.ok) {
                    return res.json().then(err => {
                        throw new Error(err.detail || 'Failed to create mentor');
                    });
                }
                return res.json();
            })
            .then(() => {
                setIsModalOpen(false);
                setNewMentor({
                    mentor_id: '',
                    mentor_name: '',
                    mentor_department: '',
                    mentor_email: '',
                    mentor_phoneno: '',
                    mentor_password: ''
                });
                fetchMentors();
                fetchFilters();
            })
            .catch((e) => alert(e.message))
            .finally(() => setSaving(false));
    };

    const renderCell = (value) => (value ? value : <span className="cell-muted">—</span>);

    return (
        <div className="admin-dashboard__main-content leader-dashboard">
            <header className="leader-dashboard__header">
                <h1 className="leader-dashboard__title">All Mentors</h1>
                <p className="leader-dashboard__subtitle">System-wide mentors list. Use filters to narrow by department.</p>
            </header>

            <div className="leader-filters">
                <button
                    type="button"
                    onClick={() => setIsModalOpen(true)}
                    style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 15px', background: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                    <FaPlus /> Create Mentor
                </button>
                <div style={{ borderLeft: '1px solid #ddd', height: '30px', margin: '0 15px' }}></div>
                <div className="leader-filters__group">
                    <span className="leader-filters__label">Department</span>
                    <select
                        className="leader-filters__select"
                        value={department}
                        onChange={(e) => setDepartment(e.target.value)}
                        aria-label="Filter by department"
                    >
                        <option value="">All departments</option>
                        {(filters.departments || []).map((d) => (
                            <option key={d} value={d}>{d}</option>
                        ))}
                    </select>
                </div>

                {department && (
                    <button
                        type="button"
                        className="leader-filters__btn-clear"
                        onClick={(e) => {
                            e.preventDefault();
                            setDepartment('');
                        }}
                        aria-label="Clear filter"
                    >
                        Clear filter
                    </button>
                )}
            </div>

            {error && !mentors.length && (
                <div className="leader-error" role="alert">
                    {error}
                </div>
            )}

            <div className="leader-count">
                <span className="leader-count__number">{loading ? '…' : mentors.length}</span>
                <span>mentor{mentors.length !== 1 ? 's' : ''} shown</span>
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
                                <p>Try changing or clearing the filters.</p>
                            </div>
                        ) : (
                            <table className="leader-table">
                                <thead>
                                    <tr>
                                        <th>Mentor ID</th>
                                        <th>Name</th>
                                        <th>Department</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {mentors.map((m) => (
                                        <tr key={m.mentor_id}>
                                            <td>{renderCell(m.mentor_id)}</td>
                                            <td>{renderCell(m.mentor_name)}</td>
                                            <td>{renderCell(m.mentor_department)}</td>
                                            <td>{renderCell(m.mentor_email)}</td>
                                            <td>{renderCell(m.mentor_phoneno)}</td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className="leader-table__action-btn"
                                                    onClick={() => handleDelete(m.mentor_id)}
                                                    aria-label="Delete mentor"
                                                    style={{ color: '#f44336' }}
                                                >
                                                    <FaTrash />
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

            {/* Modal for Creating Mentor */}
            {isModalOpen && (
                <div className="leader-modal-overlay" onClick={() => setIsModalOpen(false)} role="dialog" aria-modal="true">
                    <div className="leader-modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Create New Mentor</h2>
                        <form onSubmit={handleCreateMentor} style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '15px' }}>
                            <div className="leader-modal__field">
                                <label>Mentor ID *</label>
                                <input type="text" required value={newMentor.mentor_id} onChange={(e) => setNewMentor({ ...newMentor, mentor_id: e.target.value })} />
                            </div>
                            <div className="leader-modal__field">
                                <label>Name *</label>
                                <input type="text" required value={newMentor.mentor_name} onChange={(e) => setNewMentor({ ...newMentor, mentor_name: e.target.value })} />
                            </div>
                            <div className="leader-modal__field">
                                <label>Department *</label>
                                <input type="text" required value={newMentor.mentor_department} onChange={(e) => setNewMentor({ ...newMentor, mentor_department: e.target.value })} />
                            </div>
                            <div className="leader-modal__field">
                                <label>Email *</label>
                                <input type="email" required value={newMentor.mentor_email} onChange={(e) => setNewMentor({ ...newMentor, mentor_email: e.target.value })} />
                            </div>
                            <div className="leader-modal__field">
                                <label>Phone Number *</label>
                                <input type="text" required value={newMentor.mentor_phoneno} onChange={(e) => setNewMentor({ ...newMentor, mentor_phoneno: e.target.value })} />
                            </div>
                            <div className="leader-modal__field">
                                <label>Password *</label>
                                <input type="password" required value={newMentor.mentor_password} onChange={(e) => setNewMentor({ ...newMentor, mentor_password: e.target.value })} />
                                <small style={{ color: '#666' }}>Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char</small>
                            </div>
                            <div className="leader-modal__actions" style={{ marginTop: '20px' }}>
                                <button type="button" className="leader-modal__btn-cancel" onClick={() => setIsModalOpen(false)} disabled={saving}>Cancel</button>
                                <button type="submit" className="leader-modal__btn-submit" disabled={saving}>{saving ? 'Saving...' : 'Create'}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LeaderMentors;
