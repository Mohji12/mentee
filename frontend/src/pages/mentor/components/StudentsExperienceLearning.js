import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/ExperienceLearning.css';
import { FaFile, FaUser } from 'react-icons/fa';

const StudentsExperienceLearning = () => {
  const { mentor_id } = useParams();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterByStudent, setFilterByStudent] = useState('');
  const [uniqueStudents, setUniqueStudents] = useState([]);

  useEffect(() => {
    fetchEntries();
  }, [mentor_id]);

  useEffect(() => {
    // Extract unique students from entries
    const students = [...new Set(entries.map(entry => entry.student_usn))];
    const studentData = students.map(usn => {
      const entry = entries.find(e => e.student_usn === usn);
      return {
        usn: usn,
        name: entry?.student_name || usn
      };
    });
    setUniqueStudents(studentData);
  }, [entries]);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/students/experience-learning`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch experiential learning entries');
      }

      const data = await response.json();
      setEntries(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error('Error fetching entries:', err);
      setError(err.message);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewProof = (proofUrl) => {
    if (proofUrl) {
      window.open(proofUrl, '_blank');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const filteredEntries = filterByStudent
    ? entries.filter(entry => entry.student_usn === filterByStudent)
    : entries;

  if (loading) {
    return (
      <div className="el-loading">
        <div className="el-loading-spinner"></div>
        <p>Loading students' experiential learning entries...</p>
      </div>
    );
  }

  return (
    <div className="el-container">
      <div className="el-header">
        <h2 className="el-title">Student Experiential Learning</h2>
        {uniqueStudents.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <label htmlFor="student-filter" style={{ fontSize: '0.9rem', fontWeight: '500' }}>
              Filter by Student:
            </label>
            <select
              id="student-filter"
              value={filterByStudent}
              onChange={(e) => setFilterByStudent(e.target.value)}
              style={{
                padding: '0.5rem',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
                fontSize: '0.9rem',
                minWidth: '200px'
              }}
            >
              <option value="">All Students</option>
              {uniqueStudents.map(student => (
                <option key={student.usn} value={student.usn}>
                  {student.name} ({student.usn})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {error && (
        <div className="el-error">
          <p>Error: {error}</p>
        </div>
      )}

      {entries.length === 0 ? (
        <div className="el-empty">
          <p>No experiential learning entries from assigned students yet.</p>
        </div>
      ) : filteredEntries.length === 0 ? (
        <div className="el-empty">
          <p>No entries found for the selected student.</p>
        </div>
      ) : (
        <div className="el-entries-list">
          {filteredEntries.map((entry) => (
            <div key={entry.id} className="el-entry-card" style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.85rem',
                color: '#64748b',
                backgroundColor: '#f1f5f9',
                padding: '0.25rem 0.75rem',
                borderRadius: '6px'
              }}>
                <FaUser />
                <span><strong>{entry.student_name || entry.student_usn}</strong></span>
                <span>({entry.student_usn})</span>
              </div>
              <div className="el-entry-header">
                <h3 className="el-entry-title">{entry.title}</h3>
              </div>
              <div className="el-entry-content">
                <p className="el-entry-explanation">{entry.detailed_explanation}</p>
                {entry.proof_url && (
                  <div className="el-entry-proof">
                    <button
                      className="el-proof-btn"
                      onClick={() => handleViewProof(entry.proof_url)}
                    >
                      <FaFile /> View Proof
                    </button>
                  </div>
                )}
                <div className="el-entry-meta">
                  <span className="el-entry-date">
                    Created: {formatDate(entry.created_at)}
                  </span>
                  {entry.updated_at !== entry.created_at && (
                    <span className="el-entry-date">
                      Updated: {formatDate(entry.updated_at)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StudentsExperienceLearning;
