import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/AcademicPerformance.css';
import { FaUpload, FaEye, FaFilePdf, FaTimes } from 'react-icons/fa';

const SEM_LABELS = ['I Sem', 'II Sem', 'III Sem', 'IV Sem'];

const AcademicPerformance = () => {
  const { student_usn } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [maxSemesters, setMaxSemesters] = useState(4);
  const [semesters, setSemesters] = useState([]);
  const [savingRowId, setSavingRowId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editDraft, setEditDraft] = useState({ course: '', grade: '', overall_attendance: '' });
  const [newRowBySem, setNewRowBySem] = useState({});
  const [savingNewBySem, setSavingNewBySem] = useState(null);
  const [marksheets, setMarksheets] = useState({}); // {semester: {url, view_url, uploaded_at}}
  const [uploadingMarksheet, setUploadingMarksheet] = useState(null); // semester number
  const [marksheetFile, setMarksheetFile] = useState({}); // {semester: File}
  const [viewingMarksheet, setViewingMarksheet] = useState(null); // semester number
  const [canFillSemester, setCanFillSemester] = useState(false);
  const [secondaryMarksheets, setSecondaryMarksheets] = useState({}); // {10: {...}, 12: {...}}
  const [uploadingSecondary, setUploadingSecondary] = useState(null); // 10 or 12
  const [secondaryFile, setSecondaryFile] = useState({}); // {10: File, 12: File}

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const token = sessionStorage.getItem('access_token');
      if (!token) {
        setError('Please log in again.');
        setLoading(false);
        return;
      }
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        if (res.status === 403) setError('You do not have access.');
        else setError('Failed to load academic performance.');
        setLoading(false);
        return;
      }
      const data = await res.json();
      setMaxSemesters(data.max_semesters ?? 4);
      setSemesters(data.semesters ?? []);
      setCanFillSemester(!!data.can_fill_semester);
      setSecondaryMarksheets(data.secondary_marksheets || {});

      // Extract marksheet info
      const marksheetMap = {};
      (data.semesters || []).forEach(sem => {
        if (sem.marksheet) {
          marksheetMap[sem.semester] = sem.marksheet;
        }
      });
      setMarksheets(marksheetMap);

      const blanks = {};
      for (let s = 1; s <= (data.max_semesters ?? 4); s++) blanks[s] = { course: '', grade: '', overall_attendance: '' };
      setNewRowBySem(blanks);
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [student_usn]);

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${sessionStorage.getItem('access_token')}`,
    'Content-Type': 'application/json',
  });

  const saveNewRow = async (semester) => {
    const draft = newRowBySem[semester] || { course: '', grade: '', overall_attendance: '' };
    const course = (draft.course || '').trim();
    if (!course) {
      setError('Enter course name to save.');
      return;
    }
    setError('');
    setSavingNewBySem(semester);
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/rows`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          semester,
          course,
          grade: (draft.grade || '').trim(),
          overall_attendance: (draft.overall_attendance || '').trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to save row.');
        return;
      }
      setSemesters(data.semesters || []);
      setNewRowBySem(prev => ({ ...prev, [semester]: { course: '', grade: '', overall_attendance: '' } }));
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setSavingNewBySem(null);
    }
  };

  const startEdit = (row) => {
    if (row.is_locked) {
      setError('This row is locked and cannot be edited.');
      return;
    }
    setEditingId(row.id);
    setEditDraft({ course: row.course || '', grade: row.grade || '', overall_attendance: row.overall_attendance || '' });
  };

  const cancelEdit = () => {
    setEditingId(null);
  };

  const saveEditedRow = async () => {
    const course = (editDraft.course || '').trim();
    if (!course) {
      setError('Course name is required.');
      return;
    }
    setError('');
    setSavingRowId(editingId);
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/rows/${editingId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          course,
          grade: (editDraft.grade || '').trim(),
          overall_attendance: (editDraft.overall_attendance || '').trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to update row.');
        return;
      }
      setSemesters(data.semesters || []);
      setEditingId(null);
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setSavingRowId(null);
    }
  };

  const deleteRow = async (rowId) => {
    const row = semesters.flatMap(s => s.rows || []).find(r => r.id === rowId);
    if (row && row.is_locked) {
      setError('This row is locked and cannot be deleted.');
      return;
    }
    if (!window.confirm('Remove this row?')) return;
    setError('');
    setSavingRowId(rowId);
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/rows/${rowId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${sessionStorage.getItem('access_token')}` },
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to delete row.');
        return;
      }
      setSemesters(data.semesters || []);
      if (editingId === rowId) setEditingId(null);
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setSavingRowId(null);
    }
  };

  const updateNewRowDraft = (semester, field, value) => {
    setNewRowBySem(prev => ({
      ...prev,
      [semester]: { ...(prev[semester] || {}), [field]: value },
    }));
  };

  const handleSecondaryFileChange = (standard, file) => {
    if (file) {
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Please upload PDF, JPG, PNG, or GIF.');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        setError('File size too large. Maximum size is 10MB.');
        return;
      }
      setSecondaryFile(prev => ({ ...prev, [standard]: file }));
      setError('');
    }
  };

  const handleUploadSecondaryMarksheet = async (standard) => {
    const file = secondaryFile[standard];
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    setError('');
    setUploadingSecondary(standard);
    try {
      const token = sessionStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/secondary-marksheet/${standard}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to upload marksheet.');
        return;
      }
      await fetchData();
      setSecondaryFile(prev => {
        const updated = { ...prev };
        delete updated[standard];
        return updated;
      });
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setUploadingSecondary(null);
    }
  };

  const handleViewSecondaryMarksheet = (standard) => {
    const info = secondaryMarksheets[standard] || secondaryMarksheets[String(standard)];
    if (info && info.marksheet_view_url) {
      window.open(info.marksheet_view_url, '_blank');
      return;
    }
    const token = sessionStorage.getItem('access_token');
    fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/secondary-marksheet/${standard}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => {
        if (data.marksheet_view_url) window.open(data.marksheet_view_url, '_blank');
        else setError('Failed to load marksheet.');
      })
      .catch(() => setError('Failed to load marksheet.'));
  };

  const handleMarksheetFileChange = (semester, file) => {
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        setError('Invalid file type. Please upload PDF, JPG, PNG, or GIF.');
        return;
      }
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size too large. Maximum size is 10MB.');
        return;
      }
      setMarksheetFile(prev => ({ ...prev, [semester]: file }));
      setError('');
    }
  };

  const handleUploadMarksheet = async (semester) => {
    const file = marksheetFile[semester];
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setError('');
    setUploadingMarksheet(semester);

    try {
      const token = sessionStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/marksheet/${semester}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to upload marksheet.');
        return;
      }

      // Refresh data
      await fetchData();
      setMarksheetFile(prev => {
        const updated = { ...prev };
        delete updated[semester];
        return updated;
      });
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setUploadingMarksheet(null);
    }
  };

  const handleViewMarksheet = (semester) => {
    const marksheet = marksheets[semester];
    if (marksheet && marksheet.marksheet_view_url) {
      window.open(marksheet.marksheet_view_url, '_blank');
    } else {
      // Fetch fresh URL
      const token = sessionStorage.getItem('access_token');
      fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/marksheet/${semester}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then(res => res.json())
        .then(data => {
          if (data.marksheet_view_url) {
            window.open(data.marksheet_view_url, '_blank');
          } else {
            setError('Failed to load marksheet.');
          }
        })
        .catch(() => setError('Failed to load marksheet.'));
    }
  };

  if (loading) {
    return (
      <div className="ap-page">
        <div className="ap-loading">Loading...</div>
      </div>
    );
  }

  const secondaryInfo = (standard) => secondaryMarksheets[standard] || secondaryMarksheets[String(standard)];

  return (
    <div className="ap-page">
      <h2 className="ap-title">Academic Performance</h2>
      {error && <div className="ap-error">{error}</div>}

      {/* Step 1: Secondary education marksheets (10th & 12th) */}
      <div className="ap-secondary-section">
        <h3 className="ap-secondary-title">Step 1: Secondary education marksheets</h3>
        <p className="ap-hint">Upload your 10th and 12th standard marksheets first. After both are uploaded, you can fill semester grades and upload semester marksheets below.</p>
        <div className="ap-secondary-cards">
          {[10, 12].map((std) => {
            const info = secondaryInfo(std);
            return (
              <div key={std} className="ap-secondary-card">
                <h4 className="ap-secondary-card-title">{std}th Standard Marksheet</h4>
                {info ? (
                  <div className="ap-marksheet-uploaded">
                    <div className="ap-marksheet-info">
                      <FaFilePdf className="ap-marksheet-icon" />
                      <span>Uploaded</span>
                      {info.uploaded_at && (
                        <span className="ap-marksheet-date">({new Date(info.uploaded_at).toLocaleDateString()})</span>
                      )}
                    </div>
                    <div className="ap-marksheet-actions">
                      <button type="button" className="ap-view-marksheet-btn" onClick={() => handleViewSecondaryMarksheet(std)}>
                        <FaEye /> View
                      </button>
                      <label className="ap-upload-marksheet-btn">
                        <FaUpload /> Replace
                        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.gif" onChange={(e) => handleSecondaryFileChange(std, e.target.files[0])} style={{ display: 'none' }} />
                      </label>
                    </div>
                    {secondaryFile[std] && (
                      <div className="ap-marksheet-preview">
                        <span>{secondaryFile[std].name}</span>
                        <button type="button" className="ap-remove-file-btn" onClick={() => setSecondaryFile(prev => { const u = { ...prev }; delete u[std]; return u; })}><FaTimes /></button>
                        <button type="button" className="ap-upload-confirm-btn" onClick={() => handleUploadSecondaryMarksheet(std)} disabled={uploadingSecondary === std}>
                          {uploadingSecondary === std ? 'Uploading...' : 'Upload'}
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="ap-marksheet-upload">
                    <label className="ap-upload-marksheet-btn">
                      <FaUpload /> Upload Marksheet
                      <input type="file" accept=".pdf,.jpg,.jpeg,.png,.gif" onChange={(e) => handleSecondaryFileChange(std, e.target.files[0])} style={{ display: 'none' }} />
                    </label>
                    {secondaryFile[std] && (
                      <div className="ap-marksheet-preview">
                        <span>{secondaryFile[std].name}</span>
                        <button type="button" className="ap-remove-file-btn" onClick={() => setSecondaryFile(prev => { const u = { ...prev }; delete u[std]; return u; })}><FaTimes /></button>
                        <button type="button" className="ap-upload-confirm-btn" onClick={() => handleUploadSecondaryMarksheet(std)} disabled={uploadingSecondary === std}>
                          {uploadingSecondary === std ? 'Uploading...' : 'Upload'}
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Step 2: Semester grades and marksheets (only when 10th & 12th are uploaded) */}
      {!canFillSemester ? (
        <div className="ap-semester-blocked">
          <p className="ap-blocked-msg">Upload both 10th and 12th standard marksheets above to unlock semester grades and marksheet upload.</p>
        </div>
      ) : (
        <>
          <h3 className="ap-semester-section-title">Step 2: Semester grades and marksheets</h3>
          <p className="ap-hint">Add grades row by row. Once saved, each row is locked and cannot be edited or deleted.</p>
          {[1, 2, 3, 4].slice(0, maxSemesters).map((sem) => {
        const sec = (semesters || []).find(s => s.semester === sem) || { semester: sem, rows: [] };
        const rows = sec.rows || [];
        const draft = newRowBySem[sem] || { course: '', grade: '', overall_attendance: '' };
        return (
          <div key={sem} className="ap-semester-block">
            <h3 className="ap-semester-label">{SEM_LABELS[sem - 1]}</h3>
            <table className="ap-table">
              <thead>
                <tr>
                  <th>Course</th>
                  <th>Grade</th>
                  <th>Overall Attendance</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className={r.is_locked ? 'ap-row-locked' : ''}>
                    {editingId === r.id && !r.is_locked ? (
                      <>
                        <td><input type="text" value={editDraft.course} onChange={e => setEditDraft(prev => ({ ...prev, course: e.target.value }))} placeholder="Course" /></td>
                        <td><input type="text" value={editDraft.grade} onChange={e => setEditDraft(prev => ({ ...prev, grade: e.target.value }))} placeholder="Grade" /></td>
                        <td><input type="text" value={editDraft.overall_attendance} onChange={e => setEditDraft(prev => ({ ...prev, overall_attendance: e.target.value }))} placeholder="Attendance" /></td>
                        <td>
                          <button type="button" className="ap-save-row-btn" onClick={saveEditedRow} disabled={savingRowId === r.id}>{savingRowId === r.id ? 'Saving...' : 'Save'}</button>
                          <button type="button" className="ap-remove-btn" onClick={cancelEdit}>Cancel</button>
                        </td>
                      </>
                    ) : (
                      <>
                        <td>{r.course}</td>
                        <td>{r.grade}</td>
                        <td>{r.overall_attendance}</td>
                        <td>
                          {r.is_locked ? (
                            <span className="ap-locked-badge">Locked</span>
                          ) : (
                            <>
                              <button type="button" className="ap-remove-btn" onClick={() => startEdit(r)}>Edit</button>
                              <button type="button" className="ap-remove-btn" onClick={() => deleteRow(r.id)} disabled={savingRowId === r.id}>Delete</button>
                            </>
                          )}
                        </td>
                      </>
                    )}
                  </tr>
                ))}
                <tr className="ap-new-row">
                  <td><input type="text" value={draft.course} onChange={e => updateNewRowDraft(sem, 'course', e.target.value)} placeholder="Course name" /></td>
                  <td><input type="text" value={draft.grade} onChange={e => updateNewRowDraft(sem, 'grade', e.target.value)} placeholder="Grade" /></td>
                  <td><input type="text" value={draft.overall_attendance} onChange={e => updateNewRowDraft(sem, 'overall_attendance', e.target.value)} placeholder="Attendance" /></td>
                  <td>
                    <button type="button" className="ap-add-row" onClick={() => saveNewRow(sem)} disabled={savingNewBySem === sem}>{savingNewBySem === sem ? 'Saving...' : 'Save row'}</button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            {/* Marksheet Upload Section */}
            <div className="ap-marksheet-section">
              <h4 className="ap-marksheet-title">Marksheet</h4>
              {marksheets[sem] ? (
                <div className="ap-marksheet-uploaded">
                  <div className="ap-marksheet-info">
                    <FaFilePdf className="ap-marksheet-icon" />
                    <span>Marksheet uploaded</span>
                    {marksheets[sem].uploaded_at && (
                      <span className="ap-marksheet-date">
                        ({new Date(marksheets[sem].uploaded_at).toLocaleDateString()})
                      </span>
                    )}
                  </div>
                  <div className="ap-marksheet-actions">
                    <button
                      type="button"
                      className="ap-view-marksheet-btn"
                      onClick={() => handleViewMarksheet(sem)}
                    >
                      <FaEye /> View Marksheet
                    </button>
                    <label className="ap-upload-marksheet-btn">
                      <FaUpload /> Replace
                      <input
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png,.gif"
                        onChange={(e) => handleMarksheetFileChange(sem, e.target.files[0])}
                        style={{ display: 'none' }}
                      />
                    </label>
                  </div>
                  {marksheetFile[sem] && (
                    <div className="ap-marksheet-preview">
                      <span>{marksheetFile[sem].name}</span>
                      <button
                        type="button"
                        className="ap-remove-file-btn"
                        onClick={() => setMarksheetFile(prev => {
                          const updated = { ...prev };
                          delete updated[sem];
                          return updated;
                        })}
                      >
                        <FaTimes />
                      </button>
                      <button
                        type="button"
                        className="ap-upload-confirm-btn"
                        onClick={() => handleUploadMarksheet(sem)}
                        disabled={uploadingMarksheet === sem}
                      >
                        {uploadingMarksheet === sem ? 'Uploading...' : 'Upload'}
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="ap-marksheet-upload">
                  <label className="ap-upload-marksheet-btn">
                    <FaUpload /> Upload Marksheet
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png,.gif"
                      onChange={(e) => handleMarksheetFileChange(sem, e.target.files[0])}
                      style={{ display: 'none' }}
                    />
                  </label>
                  {marksheetFile[sem] && (
                    <div className="ap-marksheet-preview">
                      <span>{marksheetFile[sem].name}</span>
                      <button
                        type="button"
                        className="ap-remove-file-btn"
                        onClick={() => setMarksheetFile(prev => {
                          const updated = { ...prev };
                          delete updated[sem];
                          return updated;
                        })}
                      >
                        <FaTimes />
                      </button>
                      <button
                        type="button"
                        className="ap-upload-confirm-btn"
                        onClick={() => handleUploadMarksheet(sem)}
                        disabled={uploadingMarksheet === sem}
                      >
                        {uploadingMarksheet === sem ? 'Uploading...' : 'Upload'}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        );
      })}
        </>
      )}
    </div>
  );
};

export default AcademicPerformance;
