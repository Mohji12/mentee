import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/AcademicPerformance.css';
import { FaUpload, FaEye, FaFilePdf, FaTimes, FaTrash, FaDownload } from 'react-icons/fa';

const SEM_LABELS = ['I Sem', 'II Sem', 'III Sem', 'IV Sem'];
const MAX_FILE_SIZE = 20 * 1024 * 1024;
const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];

const statusBadgeClass = (status) => {
  const s = (status || 'pending').toLowerCase();
  if (s === 'verified') return 'ap-badge ap-badge-verified';
  if (s === 'rejected') return 'ap-badge ap-badge-rejected';
  if (s === 'reupload_required') return 'ap-badge ap-badge-reupload';
  return 'ap-badge ap-badge-pending';
};

const canModify = (status) => {
  const s = (status || 'pending').toLowerCase();
  return s === 'pending' || s === 'rejected' || s === 'reupload_required';
};

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
  const [marksheets, setMarksheets] = useState({});
  const [uploadingMarksheet, setUploadingMarksheet] = useState(null);
  const [marksheetFile, setMarksheetFile] = useState({});
  const [canFillSemester, setCanFillSemester] = useState(false);
  const [secondaryMarksheets, setSecondaryMarksheets] = useState({});
  const [uploadingSecondary, setUploadingSecondary] = useState(null);
  const [secondaryFile, setSecondaryFile] = useState({});
  const [secondaryMeta, setSecondaryMeta] = useState({
    10: { board_university: '', institution_name: '', year_of_passing: '', percentage_cgpa: '' },
    12: { board_university: '', institution_name: '', year_of_passing: '', percentage_cgpa: '' },
  });
  const [semesterMeta, setSemesterMeta] = useState({});
  const [documentsSummary, setDocumentsSummary] = useState(null);
  const [filters, setFilters] = useState({
    verification_status: '',
    document_type: '',
    semester: '',
    academic_year: '',
    search: '',
  });

  const token = () => sessionStorage.getItem('access_token');

  const buildQuery = useCallback(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
    const q = params.toString();
    return q ? `?${q}` : '';
  }, [filters]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      if (!token()) {
        setError('Please log in again.');
        setLoading(false);
        return;
      }
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance${buildQuery()}`, {
        headers: { Authorization: `Bearer ${token()}` },
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
      setDocumentsSummary(data.documents_summary || null);

      const marksheetMap = {};
      const metaMap = {};
      (data.semesters || []).forEach((sem) => {
        if (sem.marksheet) {
          marksheetMap[sem.semester] = sem.marksheet;
          metaMap[sem.semester] = {
            sgpa: sem.marksheet.sgpa || '',
            cgpa: sem.marksheet.cgpa || '',
            percentage: sem.marksheet.percentage || '',
            total_credits: sem.marksheet.total_credits || '',
            backlogs: sem.marksheet.backlogs || '',
            result_status: sem.marksheet.result_status || '',
            academic_year: sem.marksheet.academic_year || '',
          };
        }
      });
      setMarksheets(marksheetMap);
      setSemesterMeta((prev) => ({ ...prev, ...metaMap }));

      const secMeta = { ...secondaryMeta };
      [10, 12].forEach((std) => {
        const info = (data.secondary_marksheets || {})[std] || (data.secondary_marksheets || {})[String(std)];
        if (info) {
          secMeta[std] = {
            board_university: info.board_university || '',
            institution_name: info.institution_name || '',
            year_of_passing: info.year_of_passing || '',
            percentage_cgpa: info.percentage_cgpa || '',
          };
        }
      });
      setSecondaryMeta(secMeta);

      const blanks = {};
      for (let s = 1; s <= (data.max_semesters ?? 4); s++) {
        blanks[s] = { course: '', grade: '', overall_attendance: '' };
        if (!metaMap[s]) {
          metaMap[s] = {
            sgpa: '',
            cgpa: '',
            percentage: '',
            total_credits: '',
            backlogs: '',
            result_status: '',
            academic_year: '',
          };
        }
      }
      setNewRowBySem(blanks);
      setSemesterMeta((prev) => ({ ...metaMap, ...prev }));
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [student_usn, buildQuery]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${token()}`,
    'Content-Type': 'application/json',
  });

  const validateFile = (file) => {
    if (!ALLOWED_TYPES.includes(file.type) && !/\.(pdf|jpe?g|png)$/i.test(file.name)) {
      setError('Invalid file type. Please upload PDF, JPG, or PNG.');
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      setError('File size too large. Maximum size is 20MB.');
      return false;
    }
    return true;
  };

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
      setNewRowBySem((prev) => ({ ...prev, [semester]: { course: '', grade: '', overall_attendance: '' } }));
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

  const cancelEdit = () => setEditingId(null);

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
    const row = semesters.flatMap((s) => s.rows || []).find((r) => r.id === rowId);
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
        headers: { Authorization: `Bearer ${token()}` },
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
    setNewRowBySem((prev) => ({
      ...prev,
      [semester]: { ...(prev[semester] || {}), [field]: value },
    }));
  };

  const handleSecondaryFileChange = (standard, file) => {
    if (file && validateFile(file)) {
      setSecondaryFile((prev) => ({ ...prev, [standard]: file }));
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
      const formData = new FormData();
      formData.append('file', file);
      const meta = secondaryMeta[standard] || {};
      Object.entries(meta).forEach(([k, v]) => {
        if (v) formData.append(k, v);
      });
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/secondary-marksheet/${standard}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token()}` },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(typeof data.detail === 'string' ? data.detail : 'Failed to upload marksheet.');
        return;
      }
      await fetchData();
      setSecondaryFile((prev) => {
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

  const handleDeleteSecondary = async (standard) => {
    if (!window.confirm(`Delete ${standard}th marksheet?`)) return;
    setError('');
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/secondary-marksheet/${standard}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token()}` },
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to delete marksheet.');
        return;
      }
      await fetchData();
    } catch (e) {
      setError('Network error. Please try again.');
    }
  };

  const handleDownloadSecondary = async (standard) => {
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/secondary-marksheet/${standard}/download`, {
        headers: { Authorization: `Bearer ${token()}` },
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to download.');
        return;
      }
      if (data.download_url) window.open(data.download_url, '_blank');
    } catch (e) {
      setError('Failed to download marksheet.');
    }
  };

  const handleViewSecondaryMarksheet = (standard) => {
    const info = secondaryMarksheets[standard] || secondaryMarksheets[String(standard)];
    if (info && info.marksheet_view_url) {
      window.open(info.marksheet_view_url, '_blank');
      return;
    }
    fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/secondary-marksheet/${standard}`, {
      headers: { Authorization: `Bearer ${token()}` },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.marksheet_view_url) window.open(data.marksheet_view_url, '_blank');
        else setError('Failed to load marksheet.');
      })
      .catch(() => setError('Failed to load marksheet.'));
  };

  const handleMarksheetFileChange = (semester, file) => {
    if (file && validateFile(file)) {
      setMarksheetFile((prev) => ({ ...prev, [semester]: file }));
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
      const formData = new FormData();
      formData.append('file', file);
      const meta = semesterMeta[semester] || {};
      Object.entries(meta).forEach(([k, v]) => {
        if (v) formData.append(k, v);
      });
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/marksheet/${semester}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token()}` },
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(typeof data.detail === 'string' ? data.detail : 'Failed to upload marksheet.');
        return;
      }
      await fetchData();
      setMarksheetFile((prev) => {
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

  const handleDeleteMarksheet = async (semester) => {
    if (!window.confirm(`Delete semester ${semester} marksheet?`)) return;
    setError('');
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/marksheet/${semester}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token()}` },
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to delete marksheet.');
        return;
      }
      await fetchData();
    } catch (e) {
      setError('Network error. Please try again.');
    }
  };

  const handleDownloadMarksheet = async (semester) => {
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/marksheet/${semester}/download`, {
        headers: { Authorization: `Bearer ${token()}` },
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Failed to download.');
        return;
      }
      if (data.download_url) window.open(data.download_url, '_blank');
    } catch (e) {
      setError('Failed to download marksheet.');
    }
  };

  const handleViewMarksheet = (semester) => {
    const marksheet = marksheets[semester];
    if (marksheet && marksheet.marksheet_view_url) {
      window.open(marksheet.marksheet_view_url, '_blank');
    } else {
      fetch(`${API_BASE_URL}/student/${student_usn}/academic-performance/marksheet/${semester}`, {
        headers: { Authorization: `Bearer ${token()}` },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.marksheet_view_url) window.open(data.marksheet_view_url, '_blank');
          else setError('Failed to load marksheet.');
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

      {documentsSummary && (
        <div className="ap-docs-summary">
          <div className="ap-docs-stat"><span>Uploaded</span><strong>{documentsSummary.total_uploaded}</strong></div>
          <div className="ap-docs-stat"><span>Missing</span><strong>{documentsSummary.missing_count}</strong></div>
          <div className="ap-docs-stat"><span>Pending</span><strong>{documentsSummary.pending_verification}</strong></div>
          <div className="ap-docs-stat"><span>Verified</span><strong>{documentsSummary.verified}</strong></div>
          <div className="ap-docs-stat"><span>Rejected</span><strong>{documentsSummary.rejected}</strong></div>
        </div>
      )}

      <div className="ap-filters">
        <select value={filters.verification_status} onChange={(e) => setFilters((p) => ({ ...p, verification_status: e.target.value }))}>
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="verified">Verified</option>
          <option value="rejected">Rejected</option>
          <option value="reupload_required">Re-upload required</option>
        </select>
        <select value={filters.document_type} onChange={(e) => setFilters((p) => ({ ...p, document_type: e.target.value }))}>
          <option value="">All document types</option>
          <option value="10th">10th</option>
          <option value="12th">12th</option>
          <option value="semester">Semester</option>
        </select>
        <select value={filters.semester} onChange={(e) => setFilters((p) => ({ ...p, semester: e.target.value }))}>
          <option value="">All semesters</option>
          {[1, 2, 3, 4].slice(0, maxSemesters).map((s) => (
            <option key={s} value={s}>Semester {s}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Academic year"
          value={filters.academic_year}
          onChange={(e) => setFilters((p) => ({ ...p, academic_year: e.target.value }))}
        />
        <input
          type="text"
          placeholder="Search institution/board"
          value={filters.search}
          onChange={(e) => setFilters((p) => ({ ...p, search: e.target.value }))}
        />
        <button type="button" className="ap-filter-btn" onClick={fetchData}>Apply filters</button>
      </div>

      <div className="ap-secondary-section">
        <h3 className="ap-secondary-title">Step 1: School education (10th &amp; 12th)</h3>
        <p className="ap-hint">Upload PDF/JPG/PNG (max 20MB). Fill board, school, year, and percentage. Verified documents cannot be replaced or deleted.</p>
        <div className="ap-secondary-cards">
          {[10, 12].map((std) => {
            const info = secondaryInfo(std);
            const meta = secondaryMeta[std] || {};
            const modifiable = !info || canModify(info.verification_status);
            return (
              <div key={std} className="ap-secondary-card">
                <h4 className="ap-secondary-card-title">{std}th Standard Marksheet</h4>
                {info && (
                  <span className={statusBadgeClass(info.verification_status)}>
                    {(info.verification_status || 'pending').replace('_', ' ')}
                  </span>
                )}
                <div className="ap-meta-grid">
                  <input
                    placeholder="Board/University"
                    value={meta.board_university || ''}
                    disabled={info && !modifiable}
                    onChange={(e) => setSecondaryMeta((p) => ({ ...p, [std]: { ...p[std], board_university: e.target.value } }))}
                  />
                  <input
                    placeholder="School/College Name"
                    value={meta.institution_name || ''}
                    disabled={info && !modifiable}
                    onChange={(e) => setSecondaryMeta((p) => ({ ...p, [std]: { ...p[std], institution_name: e.target.value } }))}
                  />
                  <input
                    placeholder="Year of Passing"
                    value={meta.year_of_passing || ''}
                    disabled={info && !modifiable}
                    onChange={(e) => setSecondaryMeta((p) => ({ ...p, [std]: { ...p[std], year_of_passing: e.target.value } }))}
                  />
                  <input
                    placeholder="Percentage/CGPA"
                    value={meta.percentage_cgpa || ''}
                    disabled={info && !modifiable}
                    onChange={(e) => setSecondaryMeta((p) => ({ ...p, [std]: { ...p[std], percentage_cgpa: e.target.value } }))}
                  />
                </div>
                {info?.remarks && <p className="ap-remarks">Remarks: {info.remarks}</p>}
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
                      <button type="button" className="ap-view-marksheet-btn" onClick={() => handleDownloadSecondary(std)}>
                        <FaDownload /> Download
                      </button>
                      {modifiable && (
                        <>
                          <label className="ap-upload-marksheet-btn">
                            <FaUpload /> Replace
                            <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => handleSecondaryFileChange(std, e.target.files[0])} style={{ display: 'none' }} />
                          </label>
                          <button type="button" className="ap-remove-btn" onClick={() => handleDeleteSecondary(std)}>
                            <FaTrash /> Delete
                          </button>
                        </>
                      )}
                    </div>
                    {secondaryFile[std] && (
                      <div className="ap-marksheet-preview">
                        <span>{secondaryFile[std].name}</span>
                        <button type="button" className="ap-remove-file-btn" onClick={() => setSecondaryFile((prev) => { const u = { ...prev }; delete u[std]; return u; })}><FaTimes /></button>
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
                      <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => handleSecondaryFileChange(std, e.target.files[0])} style={{ display: 'none' }} />
                    </label>
                    {secondaryFile[std] && (
                      <div className="ap-marksheet-preview">
                        <span>{secondaryFile[std].name}</span>
                        <button type="button" className="ap-remove-file-btn" onClick={() => setSecondaryFile((prev) => { const u = { ...prev }; delete u[std]; return u; })}><FaTimes /></button>
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

      {!canFillSemester ? (
        <div className="ap-semester-blocked">
          <p className="ap-blocked-msg">Upload both 10th and 12th standard marksheets above to unlock semester grades and marksheet upload.</p>
        </div>
      ) : (
        <>
          <h3 className="ap-semester-section-title">Step 2: Graduation records (semester-wise)</h3>
          <p className="ap-hint">Add grades row by row. Upload semester marksheet with SGPA/CGPA. Once verified, documents cannot be changed.</p>
          {[1, 2, 3, 4].slice(0, maxSemesters).map((sem) => {
            const sec = (semesters || []).find((s) => s.semester === sem) || { semester: sem, rows: [] };
            const rows = sec.rows || [];
            const draft = newRowBySem[sem] || { course: '', grade: '', overall_attendance: '' };
            const ms = marksheets[sem];
            const meta = semesterMeta[sem] || {};
            const modifiable = !ms || canModify(ms.verification_status);
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
                            <td><input type="text" value={editDraft.course} onChange={(e) => setEditDraft((prev) => ({ ...prev, course: e.target.value }))} placeholder="Course" /></td>
                            <td><input type="text" value={editDraft.grade} onChange={(e) => setEditDraft((prev) => ({ ...prev, grade: e.target.value }))} placeholder="Grade" /></td>
                            <td><input type="text" value={editDraft.overall_attendance} onChange={(e) => setEditDraft((prev) => ({ ...prev, overall_attendance: e.target.value }))} placeholder="Attendance" /></td>
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
                      <td><input type="text" value={draft.course} onChange={(e) => updateNewRowDraft(sem, 'course', e.target.value)} placeholder="Course name" /></td>
                      <td><input type="text" value={draft.grade} onChange={(e) => updateNewRowDraft(sem, 'grade', e.target.value)} placeholder="Grade" /></td>
                      <td><input type="text" value={draft.overall_attendance} onChange={(e) => updateNewRowDraft(sem, 'overall_attendance', e.target.value)} placeholder="Attendance" /></td>
                      <td>
                        <button type="button" className="ap-add-row" onClick={() => saveNewRow(sem)} disabled={savingNewBySem === sem}>{savingNewBySem === sem ? 'Saving...' : 'Save row'}</button>
                      </td>
                    </tr>
                  </tbody>
                </table>

                <div className="ap-marksheet-section">
                  <h4 className="ap-marksheet-title">
                    Semester Marksheet{' '}
                    {ms && <span className={statusBadgeClass(ms.verification_status)}>{(ms.verification_status || 'pending').replace('_', ' ')}</span>}
                  </h4>
                  <div className="ap-meta-grid">
                    <input placeholder="SGPA" value={meta.sgpa || ''} disabled={ms && !modifiable} onChange={(e) => setSemesterMeta((p) => ({ ...p, [sem]: { ...p[sem], sgpa: e.target.value } }))} />
                    <input placeholder="CGPA" value={meta.cgpa || ''} disabled={ms && !modifiable} onChange={(e) => setSemesterMeta((p) => ({ ...p, [sem]: { ...p[sem], cgpa: e.target.value } }))} />
                    <input placeholder="Percentage" value={meta.percentage || ''} disabled={ms && !modifiable} onChange={(e) => setSemesterMeta((p) => ({ ...p, [sem]: { ...p[sem], percentage: e.target.value } }))} />
                    <input placeholder="Total Credits" value={meta.total_credits || ''} disabled={ms && !modifiable} onChange={(e) => setSemesterMeta((p) => ({ ...p, [sem]: { ...p[sem], total_credits: e.target.value } }))} />
                    <input placeholder="Backlogs" value={meta.backlogs || ''} disabled={ms && !modifiable} onChange={(e) => setSemesterMeta((p) => ({ ...p, [sem]: { ...p[sem], backlogs: e.target.value } }))} />
                    <input placeholder="Result Status" value={meta.result_status || ''} disabled={ms && !modifiable} onChange={(e) => setSemesterMeta((p) => ({ ...p, [sem]: { ...p[sem], result_status: e.target.value } }))} />
                    <input placeholder="Academic Year" value={meta.academic_year || ''} disabled={ms && !modifiable} onChange={(e) => setSemesterMeta((p) => ({ ...p, [sem]: { ...p[sem], academic_year: e.target.value } }))} />
                  </div>
                  {ms?.remarks && <p className="ap-remarks">Remarks: {ms.remarks}</p>}
                  {ms ? (
                    <div className="ap-marksheet-uploaded">
                      <div className="ap-marksheet-info">
                        <FaFilePdf className="ap-marksheet-icon" />
                        <span>Marksheet uploaded</span>
                        {ms.uploaded_at && (
                          <span className="ap-marksheet-date">({new Date(ms.uploaded_at).toLocaleDateString()})</span>
                        )}
                      </div>
                      <div className="ap-marksheet-actions">
                        <button type="button" className="ap-view-marksheet-btn" onClick={() => handleViewMarksheet(sem)}><FaEye /> View</button>
                        <button type="button" className="ap-view-marksheet-btn" onClick={() => handleDownloadMarksheet(sem)}><FaDownload /> Download</button>
                        {modifiable && (
                          <>
                            <label className="ap-upload-marksheet-btn">
                              <FaUpload /> Replace
                              <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => handleMarksheetFileChange(sem, e.target.files[0])} style={{ display: 'none' }} />
                            </label>
                            <button type="button" className="ap-remove-btn" onClick={() => handleDeleteMarksheet(sem)}><FaTrash /> Delete</button>
                          </>
                        )}
                      </div>
                      {marksheetFile[sem] && (
                        <div className="ap-marksheet-preview">
                          <span>{marksheetFile[sem].name}</span>
                          <button type="button" className="ap-remove-file-btn" onClick={() => setMarksheetFile((prev) => { const u = { ...prev }; delete u[sem]; return u; })}><FaTimes /></button>
                          <button type="button" className="ap-upload-confirm-btn" onClick={() => handleUploadMarksheet(sem)} disabled={uploadingMarksheet === sem}>
                            {uploadingMarksheet === sem ? 'Uploading...' : 'Upload'}
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="ap-marksheet-upload">
                      <label className="ap-upload-marksheet-btn">
                        <FaUpload /> Upload Marksheet
                        <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => handleMarksheetFileChange(sem, e.target.files[0])} style={{ display: 'none' }} />
                      </label>
                      {marksheetFile[sem] && (
                        <div className="ap-marksheet-preview">
                          <span>{marksheetFile[sem].name}</span>
                          <button type="button" className="ap-remove-file-btn" onClick={() => setMarksheetFile((prev) => { const u = { ...prev }; delete u[sem]; return u; })}><FaTimes /></button>
                          <button type="button" className="ap-upload-confirm-btn" onClick={() => handleUploadMarksheet(sem)} disabled={uploadingMarksheet === sem}>
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
