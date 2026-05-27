import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import * as XLSX from 'xlsx';
import '../../../assets/css/AdminStudents.css';

const AdminStudents = () => {
  const { admin_id } = useParams();
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [mentorsByProgram, setMentorsByProgram] = useState({});
  const [statuses, setStatuses] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState('');
  const [selectedMentor, setSelectedMentor] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/admin/${admin_id}/get_all_students`);
        if (!response.ok) {
          throw new Error('Error fetching students');
        }
        const data = await response.json();
        setStudents(data);
        setFilteredStudents(data);
        extractFilters(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStudents();
  }, [admin_id]);

  const extractFilters = (data) => {
    const uniquePrograms = [...new Set(data.map(student => student.program))];

    // Group mentors by program (department)
    const mentorsByDept = {};
    data.forEach(student => {
      if (!mentorsByDept[student.program]) {
        mentorsByDept[student.program] = new Set();
      }
      mentorsByDept[student.program].add(student.ass_mentor);
    });

    // Convert mentor sets to arrays for easy mapping
    for (const program in mentorsByDept) {
      mentorsByDept[program] = [...mentorsByDept[program]];
    }

    let uniqueStatuses = [...new Set(data.map(student => student.status))];

    // Always include the full pipeline ending with MCA Form Filled
    const mcaPipeline = "Signed Up → Profile Created → Form Filled → SWOT Generated → Activities Generated → MCA Form Filled";
    if (!uniqueStatuses.includes(mcaPipeline)) {
      uniqueStatuses.push(mcaPipeline);
    }

    setPrograms(uniquePrograms);
    setMentorsByProgram(mentorsByDept);
    setStatuses(uniqueStatuses);
  };

  useEffect(() => {
    handleFilterChange();
  }, [selectedProgram, selectedMentor, selectedStatus]);

  const handleFilterChange = () => {
    let filtered = students;
    if (selectedProgram) {
      filtered = filtered.filter(student => student.program === selectedProgram);
    }
    if (selectedMentor) {
      filtered = filtered.filter(student => student.ass_mentor === selectedMentor);
    }
    if (selectedStatus) {
      filtered = filtered.filter(student => student.status === selectedStatus);
    }
    setFilteredStudents(filtered);
  };

  const downloadExcel = () => {
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(filteredStudents);
    XLSX.utils.book_append_sheet(wb, ws, 'Students');
    XLSX.writeFile(wb, 'students.xlsx');
  };

  const downloadPF16All = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/pf16-form/download-all`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

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
    } catch (error) {
      console.error('Download error:', error);
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
        {
          headers: { Authorization: `Bearer ${token}` },
        }
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
      const filename = response.headers.get('Content-Disposition')?.split('filename=')[1] || '16PF_Filtered.zip';
      a.download = filename.replace(/"/g, '');
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download filtered 16PF ZIP file.');
    }
  };

  const downloadIBPAll = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/admin/${admin_id}/ibp-form/download-all`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

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
    } catch (error) {
      console.error('Download error:', error);
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
        {
          headers: { Authorization: `Bearer ${token}` },
        }
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
      const filename = response.headers.get('Content-Disposition')?.split('filename=')[1] || 'IBP_Filtered.zip';
      a.download = filename.replace(/"/g, '');
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
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
    } catch (error) {
      setError(error.message);
    } finally {
      setLoadingStats(false);
    }
  };

  if (isLoading) return <div>Loading students...</div>;
  if (error) return <div className="error-message">{`Error: ${error}`}</div>;

  return (
    <div className="admin-students__content">
      <h2 className="admin-students__title">All Students</h2>
      
      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <button
          className="download-btn"
          onClick={fetchStats}
          disabled={loadingStats}
        >
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
        <button className="download-excel-btn" onClick={downloadIBPAll} style={{ background: '#ffc107', color: '#000' }}>
          Download IBP (All)
        </button>
        <button className="download-excel-btn" onClick={downloadIBPFiltered} style={{ background: '#fd7e14' }}>
          Download IBP (Filtered)
        </button>
      </div>

      {stats && (
        <div className="admin-stats">
          <h3>Statistics</h3>
          <div className="stats-circles">
            <div className="stat-circle">
              <div className="circle">{stats.total_students}</div>
              <p>Total</p>
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

      {/* Filters */}
      <div className="admin-students__filters">
        <select value={selectedProgram} onChange={(e) => {
          setSelectedProgram(e.target.value);
          setSelectedMentor(''); // Reset mentor when department changes
        }}>
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
          Total students in  
          <span className="highlight-text"> {selectedProgram || "All Programs"} </span>
          under
          <span className="highlight-text"> {selectedMentor || "All Mentors"} </span>
          with 
          <span className="highlight-text"> {selectedStatus || "All Statuses"} </span>:
          &nbsp;{filteredStudents.length}
        </strong>
      </div><br/>

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
              <th>LinkedIn</th>
              <th>Semester</th>
              <th>Assigned Mentor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.map(student => (
              <tr key={student.student_usn}>
                <td>{student.student_usn}</td>
                <td>{student.student_name}</td>
                <td>{student.phone}</td>
                <td>{student.email}</td>
                <td>{student.program}</td>
                <td><a href={student.linkedin} target="_blank" rel="noopener noreferrer">{student.linkedin ? 'Profile' : 'N/A'}</a></td>
                <td>{student.semester}</td>
                <td>{student.ass_mentor}</td>
                <td>{student.status}</td>
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
