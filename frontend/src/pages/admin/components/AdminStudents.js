import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import * as XLSX from 'xlsx';
import '../../../assets/css/AdminStudents.css';

const VIEW_TABS = [
  { id: 'active', label: 'Active Students' },
  { id: 'alumni', label: 'Alumni' },
  { id: 'all', label: 'All' },
];

const AdminStudents = () => {
  const { admin_id } = useParams();
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [batches, setBatches] = useState([]);
  const [mentorsByProgram, setMentorsByProgram] = useState({});
  const [statuses, setStatuses] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState('');
  const [selectedMentor, setSelectedMentor] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedBatch, setSelectedBatch] = useState('');
  const [studentView, setStudentView] = useState('active');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [alumniActionBusy, setAlumniActionBusy] = useState(false);

  const extractFilters = (data) => {
    const uniquePrograms = [...new Set(data.map((student) => student.program).filter(Boolean))];
    const uniqueBatches = [...new Set(data.map((student) => student.student_batch).filter(Boolean))].sort();

    const mentorsByDept = {};
    data.forEach((student) => {
      if (!student.program) return;
      if (!mentorsByDept[student.program]) {
        mentorsByDept[student.program] = new Set();
      }
      mentorsByDept[student.program].add(student.ass_mentor);
    });

    for (const program in mentorsByDept) {
      mentorsByDept[program] = [...mentorsByDept[program]];
    }

    let uniqueStatuses = [...new Set(data.map((student) => student.status))];
    const mcaPipeline =
      'Signed Up → Profile Created → Form Filled → SWOT Generated → Activities Generated → MCA Form Filled';
    if (!uniqueStatuses.includes(mcaPipeline)) {
      uniqueStatuses.push(mcaPipeline);
    }

    setPrograms(uniquePrograms);
    setBatches(uniqueBatches);
    setMentorsByProgram(mentorsByDept);
    setStatuses(uniqueStatuses);
  };

  const fetchStudents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/get_all_students?view=${studentView}`
      );
      if (!response.ok) {
        throw new Error('Error fetching students');
      }
      const data = await response.json();
      setStudents(data);
      setFilteredStudents(data);
      extractFilters(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [admin_id, studentView]);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  useEffect(() => {
    handleFilterChange();
  }, [selectedProgram, selectedMentor, selectedStatus, students]);

  const handleFilterChange = () => {
    let filtered = students;
    if (selectedProgram) {
      filtered = filtered.filter((student) => student.program === selectedProgram);
    }
    if (selectedMentor) {
      filtered = filtered.filter((student) => student.ass_mentor === selectedMentor);
    }
    if (selectedStatus) {
      filtered = filtered.filter((student) => student.status === selectedStatus);
    }
    setFilteredStudents(filtered);
  };

  const downloadExcel = () => {
    const sheetName = studentView === 'alumni' ? 'Alumni' : studentView === 'active' ? 'Active Students' : 'Students';
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(filteredStudents);
    XLSX.utils.book_append_sheet(wb, ws, sheetName);
    XLSX.writeFile(wb, `${sheetName.toLowerCase().replace(/\s+/g, '_')}.xlsx`);
  };

  const downloadPF16All = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/pf16-form/download-all`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        if (response.status === 404) {
          alert('No students have submitted 16PF forms yet.');
          return;
        }
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = '16PF_All_Students.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      alert('Failed to download 16PF ZIP file.');
    }
  };

  const downloadPF16Filtered = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const params = new URLSearchParams();
      if (selectedProgram) params.append('program', selectedProgram);
      if (selectedMentor) params.append('mentor', selectedMentor);
      if (selectedStatus) params.append('status', selectedStatus);

      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/pf16-form/download-filtered?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!response.ok) {
        if (response.status === 404) {
          alert('No students match the filter criteria or have submitted 16PF forms.');
          return;
        }
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const filename =
        response.headers.get('Content-Disposition')?.split('filename=')[1] || '16PF_Filtered.zip';
      a.download = filename.replace(/"/g, '');
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      alert('Failed to download filtered 16PF ZIP file.');
    }
  };

  const downloadIBPAll = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/ibp-form/download-all`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        if (response.status === 404) {
          alert('No students have submitted IBP forms yet.');
          return;
        }
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'IBP_All_Students.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      alert('Failed to download IBP ZIP file.');
    }
  };

  const downloadIBPFiltered = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const params = new URLSearchParams();
      if (selectedProgram) params.append('program', selectedProgram);
      if (selectedMentor) params.append('mentor', selectedMentor);
      if (selectedStatus) params.append('status', selectedStatus);

      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/ibp-form/download-filtered?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (!response.ok) {
        if (response.status === 404) {
          alert('No students match the filter criteria or have submitted IBP forms.');
          return;
        }
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const filename =
        response.headers.get('Content-Disposition')?.split('filename=')[1] || 'IBP_Filtered.zip';
      a.download = filename.replace(/"/g, '');
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download error:', err);
      alert('Failed to download filtered IBP ZIP file.');
    }
  };

  const fetchStats = async () => {
    setLoadingStats(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/student_stats`);
      if (!response.ok) {
        throw new Error('Error fetching statistics');
      }
      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingStats(false);
    }
  };

  const updateAlumniStatus = async (studentUsn, isAlumni) => {
    setAlumniActionBusy(true);
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/students/${encodeURIComponent(studentUsn)}/alumni-status`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ is_alumni: isAlumni }),
        }
      );
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to update alumni status');
      }
      await fetchStudents();
    } catch (err) {
      alert(err.message);
    } finally {
      setAlumniActionBusy(false);
    }
  };

  const markBatchAsAlumni = async () => {
    if (!selectedBatch) {
      alert('Select a batch first.');
      return;
    }
    if (!window.confirm(`Move all active students in batch ${selectedBatch} to Alumni?`)) {
      return;
    }
    setAlumniActionBusy(true);
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/students/mark-alumni-by-batch`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ student_batch: selectedBatch }),
        }
      );
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to mark batch as alumni');
      }
      alert(`Marked ${data.updated} student(s) in batch ${selectedBatch} as alumni.`);
      setStudentView('alumni');
    } catch (err) {
      alert(err.message);
    } finally {
      setAlumniActionBusy(false);
    }
  };

  const syncAlumniFromBatches = async () => {
    if (
      !window.confirm(
        'Auto-mark students as alumni when their batch end year has passed (July onwards)?'
      )
    ) {
      return;
    }
    setAlumniActionBusy(true);
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/students/sync-alumni-from-batches`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || 'Sync failed');
      }
      alert(data.message || `Updated ${data.updated} student(s).`);
      await fetchStudents();
    } catch (err) {
      alert(err.message);
    } finally {
      setAlumniActionBusy(false);
    }
  };

  if (isLoading) return <div>Loading students...</div>;
  if (error) return <div className="error-message">{`Error: ${error}`}</div>;

  const viewLabel = VIEW_TABS.find((t) => t.id === studentView)?.label || 'Students';

  return (
    <div className="admin-students__content">
      <h2 className="admin-students__title">{viewLabel}</h2>

      <div className="admin-students__view-tabs">
        {VIEW_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`admin-students__view-tab ${studentView === tab.id ? 'active' : ''}`}
            onClick={() => setStudentView(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="admin-students__alumni-tools">
        <select value={selectedBatch} onChange={(e) => setSelectedBatch(e.target.value)}>
          <option value="">Select batch for bulk move</option>
          {batches.map((batch) => (
            <option key={batch} value={batch}>
              {batch}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="admin-students__alumni-btn primary"
          onClick={markBatchAsAlumni}
          disabled={alumniActionBusy || !selectedBatch}
        >
          Move batch to Alumni
        </button>
        <button
          type="button"
          className="admin-students__alumni-btn"
          onClick={syncAlumniFromBatches}
          disabled={alumniActionBusy}
        >
          Auto-sync graduated batches
        </button>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <button className="download-btn" onClick={fetchStats} disabled={loadingStats}>
          {loadingStats ? 'Showing... Please wait' : 'Show Stats'}
        </button>
        <button className="download-excel-btn" onClick={downloadExcel}>
          Download as Excel
        </button>
        <button className="download-excel-btn" onClick={downloadPF16All} style={{ background: '#28a745' }}>
          Download 16PF (All)
        </button>
        <button className="download-excel-btn" onClick={downloadPF16Filtered} style={{ background: '#17a2b8' }}>
          Download 16PF (Filtered)
        </button>
        <button
          className="download-excel-btn"
          onClick={downloadIBPAll}
          style={{ background: '#ffc107', color: '#000' }}
        >
          Download IBP (All)
        </button>
        <button className="download-excel-btn" onClick={downloadIBPFiltered} style={{ background: '#fd7e14' }}>
          Download IBP (Filtered)
        </button>
      </div>

      {stats && (
        <div className="admin-stats">
          <h3>Statistics (active students)</h3>
          <div className="stats-circles">
            <div className="stat-circle">
              <div className="circle">{stats.total_active ?? stats.total_students}</div>
              <p>Active</p>
            </div>
            <div className="stat-circle">
              <div className="circle">{stats.total_alumni ?? 0}</div>
              <p>Alumni</p>
            </div>
            <div className="stat-circle">
              <div className="circle">{stats.signed_up}</div>
              <p>Signed Up</p>
            </div>
            <div className="stat-circle">
              <div className="circle">{stats.profile_created}</div>
              <p>Profile Created</p>
            </div>
            <div className="stat-circle">
              <div className="circle">{stats.form_filled}</div>
              <p>Psychometric From Filled</p>
            </div>
            <div className="stat-circle">
              <div className="circle">{stats.swot_generated}</div>
              <p>SWOT Generated</p>
            </div>
            <div className="stat-circle">
              <div className="circle">{stats.activities_generated}</div>
              <p>Activities Generated</p>
            </div>
            <div className="stat-circle">
              <div className="circle">{stats.mca_filled}</div>
              <p>MCA Form Filled</p>
            </div>
          </div>
        </div>
      )}

      <div className="admin-students__filters">
        <select
          value={selectedProgram}
          onChange={(e) => {
            setSelectedProgram(e.target.value);
            setSelectedMentor('');
          }}
        >
          <option value="">All Programs</option>
          {programs.map((program, index) => (
            <option key={index} value={program}>
              {program}
            </option>
          ))}
        </select>

        <select value={selectedMentor} onChange={(e) => setSelectedMentor(e.target.value)} disabled={!selectedProgram}>
          <option value="">All Mentors</option>
          {selectedProgram && mentorsByProgram[selectedProgram] ? (
            mentorsByProgram[selectedProgram].map((mentor, index) => (
              <option key={index} value={mentor}>
                {mentor}
              </option>
            ))
          ) : (
            <option disabled>No Mentors Available</option>
          )}
        </select>

        <select value={selectedStatus} onChange={(e) => setSelectedStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {statuses.map((status, index) => (
            <option key={index} value={status}>
              {status}
            </option>
          ))}
        </select>
      </div>

      <div className="student-count">
        <strong>
          {filteredStudents.length} {viewLabel.toLowerCase()} in
          <span className="highlight-text"> {selectedProgram || 'All Programs'} </span>
          under
          <span className="highlight-text"> {selectedMentor || 'All Mentors'} </span>
          with
          <span className="highlight-text"> {selectedStatus || 'All Statuses'} </span>
        </strong>
      </div>
      <br />

      {filteredStudents.length > 0 ? (
        <div className="admin-students__table-container">
          <table className="admin-students__table">
            <thead>
              <tr>
                <th>USN</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Program</th>
                <th>Batch</th>
                <th>LinkedIn</th>
                <th>Semester</th>
                <th>Assigned Mentor</th>
                <th>Status</th>
                {studentView !== 'all' && <th>Action</th>}
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((student) => (
                <tr key={student.student_usn}>
                  <td>{student.student_usn}</td>
                  <td>{student.student_name}</td>
                  <td>{student.phone}</td>
                  <td>{student.email}</td>
                  <td>{student.program}</td>
                  <td>{student.student_batch || '—'}</td>
                  <td>
                    <a href={student.linkedin} target="_blank" rel="noopener noreferrer">
                      {student.linkedin ? 'Profile' : 'N/A'}
                    </a>
                  </td>
                  <td>{student.semester}</td>
                  <td>{student.ass_mentor}</td>
                  <td>{student.status}</td>
                  {studentView !== 'all' && (
                    <td>
                      {studentView === 'active' ? (
                        <button
                          type="button"
                          className="admin-students__row-action to-alumni"
                          disabled={alumniActionBusy}
                          onClick={() => updateAlumniStatus(student.student_usn, true)}
                        >
                          Move to Alumni
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="admin-students__row-action to-active"
                          disabled={alumniActionBusy}
                          onClick={() => updateAlumniStatus(student.student_usn, false)}
                        >
                          Restore Active
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="admin-students__no-students">No students found.</div>
      )}
    </div>
  );
};

export default AdminStudents;
