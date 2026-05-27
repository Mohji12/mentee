import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/MentorConsolidatedInternalMarks.css';
import { FaGraduationCap, FaDownload, FaUpload, FaFileAlt } from 'react-icons/fa';

function downloadCsv(filename, text) {
  const blob = new Blob(['\ufeff', text], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function escapeCsvCell(v) {
  if (v == null || v === '') return '';
  const s = String(v);
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

const MentorConsolidatedInternalMarks = () => {
  const { mentor_id } = useParams();
  const [semester, setSemester] = useState(1);
  const [batchId, setBatchId] = useState('');
  const [batches, setBatches] = useState([]);
  const [matrix, setMatrix] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [importFile, setImportFile] = useState(null);
  const [importTitle, setImportTitle] = useState('');
  const [importSection, setImportSection] = useState('');
  const [importProgram, setImportProgram] = useState('');
  const [importBranch, setImportBranch] = useState('');
  const [importYear, setImportYear] = useState('');
  const [importing, setImporting] = useState(false);
  const [importMessage, setImportMessage] = useState('');
  const [importErrors, setImportErrors] = useState([]);

  const token = () => sessionStorage.getItem('access_token');

  const loadBatches = useCallback(async () => {
    try {
      const res = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/internal-marks/batches?semester=${semester}`,
        { headers: { Authorization: `Bearer ${token()}` } }
      );
      const data = await res.json().catch(() => []);
      if (!res.ok) throw new Error(data?.detail || 'Failed to load batches');
      setBatches(Array.isArray(data) ? data : []);
    } catch (e) {
      setBatches([]);
    }
  }, [mentor_id, semester]);

  const loadMatrix = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams({ semester: String(semester) });
      if (batchId) params.set('batch_id', batchId);
      const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/internal-marks/matrix?${params}`, {
        headers: { Authorization: `Bearer ${token()}` },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data?.detail || 'Failed to load matrix');
      setMatrix(data);
    } catch (e) {
      setMatrix(null);
      setError(e?.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [mentor_id, semester, batchId]);

  useEffect(() => {
    setBatchId('');
  }, [semester, mentor_id]);

  useEffect(() => {
    loadBatches();
  }, [loadBatches]);

  useEffect(() => {
    loadMatrix();
  }, [loadMatrix]);

  const titleLine = useMemo(() => {
    const b = matrix?.batch;
    if (!b) return '';
    const parts = [
      b.title,
      b.program_label,
      b.branch_label,
      b.section_code ? `Section ${b.section_code}` : null,
      b.academic_year ? `AY ${b.academic_year}` : null,
    ].filter(Boolean);
    return parts.join(' · ');
  }, [matrix]);

  const downloadTemplate = () => {
    const tpl =
      'student_usn,subject_code,subject_name,component_label,score\n' +
      '23MSRDS018,22CSB3001,Sample Course,Activity-1,9.5\n';
    downloadCsv('internal_marks_template.csv', tpl);
  };

  const submitImport = async (e) => {
    e.preventDefault();
    setImportMessage('');
    setImportErrors([]);
    if (!importFile) {
      setImportMessage('Choose a CSV or Excel file first.');
      return;
    }
    setImporting(true);
    try {
      const fd = new FormData();
      fd.append('semester', String(semester));
      fd.append('file', importFile);
      if (importTitle.trim()) fd.append('title', importTitle.trim());
      if (importSection.trim()) fd.append('section_code', importSection.trim());
      if (importProgram.trim()) fd.append('program_label', importProgram.trim());
      if (importBranch.trim()) fd.append('branch_label', importBranch.trim());
      if (importYear.trim()) fd.append('academic_year', importYear.trim());

      const res = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/internal-marks/import`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token()}` },
        body: fd,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const d = data?.detail;
        let msg = 'Import failed';
        if (typeof d === 'string') msg = d;
        else if (Array.isArray(d) && d[0]?.msg) msg = d.map((x) => x.msg || JSON.stringify(x)).join('; ');
        else if (d && typeof d === 'object') msg = JSON.stringify(d);
        throw new Error(msg);
      }
      setImportMessage(
        `Import done. Batch #${data.batch_id}: inserted ${data.rows_inserted}, updated ${data.rows_updated}, skipped ${data.rows_skipped}.`
      );
      if (Array.isArray(data.errors) && data.errors.length > 0) {
        setImportErrors(data.errors);
      }
      setImportFile(null);
      const fileInput = document.getElementById('mcim-file-input');
      if (fileInput) fileInput.value = '';
      await loadBatches();
      await loadMatrix();
    } catch (err) {
      setImportMessage(err?.message || 'Import failed');
    } finally {
      setImporting(false);
    }
  };

  const exportCsv = () => {
    if (!matrix?.students?.length || !matrix?.flat_columns?.length) return;
    const headers = [
      'Student USN',
      'Student Name',
      ...matrix.flat_columns.map((c) => `${c.subject_code} — ${c.component_label}`),
    ];
    const lines = [headers.map(escapeCsvCell).join(',')];
    for (const row of matrix.students) {
      const cells = [row.student_usn, row.student_name || '', ...(row.scores || [])];
      lines.push(cells.map(escapeCsvCell).join(','));
    }
    const fname = `internal_marks_sem${semester}_${mentor_id}.csv`;
    downloadCsv(fname, lines.join('\r\n'));
  };

  const hasData = matrix?.flat_columns?.length > 0 && matrix?.students?.length > 0;

  return (
    <div className="mcim-wrap">
      <div className="mcim-header">
        <h1>
          <FaGraduationCap style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
          Consolidated Internal Marks
        </h1>
        <p>
          Upload a CSV or Excel file to import internal marks for your assigned mentees only. View the consolidated grid
          below; use horizontal scroll for many subjects — USN and name stay pinned.
        </p>
        {titleLine && <div className="mcim-meta">{titleLine}</div>}
      </div>

      <div className="mcim-upload-panel">
        <h2>
          <FaUpload style={{ marginRight: '0.45rem', verticalAlign: 'middle' }} />
          Import marks (your mentees only)
        </h2>
        <p style={{ margin: '0 0 0.75rem', fontSize: '0.85rem', color: '#64748b' }}>
          Each row: student_usn, subject_code, component_label, score — optional subject_name. Rows for students not assigned
          to you are skipped.
        </p>
        <form onSubmit={submitImport}>
          <div className="mcim-upload-grid">
            <label>
              File (.csv / .xlsx)
              <input
                id="mcim-file-input"
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(e) => setImportFile(e.target.files?.[0] || null)}
              />
            </label>
            <label>
              Title (optional)
              <input type="text" value={importTitle} onChange={(e) => setImportTitle(e.target.value)} placeholder="Report title" />
            </label>
            <label>
              Section code (optional)
              <input type="text" value={importSection} onChange={(e) => setImportSection(e.target.value)} placeholder="e.g. 5PMCSA" />
            </label>
            <label>
              Program (optional)
              <input type="text" value={importProgram} onChange={(e) => setImportProgram(e.target.value)} />
            </label>
            <label>
              Branch (optional)
              <input type="text" value={importBranch} onChange={(e) => setImportBranch(e.target.value)} />
            </label>
            <label>
              Academic year (optional)
              <input type="text" value={importYear} onChange={(e) => setImportYear(e.target.value)} placeholder="2024-25" />
            </label>
          </div>
          <div className="mcim-upload-actions">
            <button type="submit" className="mcim-btn" disabled={importing}>
              {importing ? 'Uploading…' : 'Upload import'}
            </button>
            <button type="button" className="mcim-btn mcim-btn--secondary" onClick={downloadTemplate}>
              <FaFileAlt style={{ marginRight: '0.35rem' }} />
              Download template CSV
            </button>
          </div>
        </form>
        {importMessage && (
          <div className={importErrors.length ? 'mcim-import-result mcim-import-result--warn' : 'mcim-import-result'}>
            {importMessage}
            {importErrors.length > 0 && (
              <div className="mcim-import-errors">{importErrors.slice(0, 50).join('\n')}</div>
            )}
          </div>
        )}
      </div>

      <div className="mcim-controls">
        <label>
          Semester
          <select value={semester} onChange={(e) => setSemester(Number(e.target.value))}>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label>
          Import batch
          <select value={batchId} onChange={(e) => setBatchId(e.target.value)}>
            <option value="">Latest (auto)</option>
            {batches.map((b) => (
              <option key={b.id} value={String(b.id)}>
                #{b.id}
                {b.section_code ? ` · ${b.section_code}` : ''}
                {b.title ? ` · ${b.title.slice(0, 40)}${b.title.length > 40 ? '…' : ''}` : ''} ({b.row_count} rows)
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="mcim-btn mcim-btn--secondary" onClick={() => loadMatrix()}>
          Refresh
        </button>
        {hasData && (
          <button type="button" className="mcim-btn" onClick={exportCsv}>
            <FaDownload style={{ marginRight: '0.35rem' }} />
            Download CSV
          </button>
        )}
      </div>

      {loading && <div className="mcim-loading">Loading…</div>}
      {error && <div className="mcim-error">{error}</div>}

      {!loading && !error && !hasData && (
        <div className="mcim-empty">
          No internal marks for this semester yet. Use <strong>Import marks</strong> above (CSV/Excel), then refresh or pick
          the batch.
        </div>
      )}

      {hasData && (
        <div className="mcim-scroll">
          <table className="mcim-table">
            <thead>
              <tr>
                <th className="mcim-sticky mcim-th-sticky" rowSpan={2}>
                  Student Code
                </th>
                <th className="mcim-sticky-2 mcim-th-sticky-2" rowSpan={2}>
                  Student Name
                </th>
                {matrix.subjects.map((sub) => (
                  <th key={sub.subject_code} colSpan={sub.components.length} className="mcim-subject-head">
                    {sub.subject_code}
                    {sub.subject_name ? ` — ${sub.subject_name}` : ''}
                  </th>
                ))}
              </tr>
              <tr>
                {matrix.flat_columns.map((c, i) => (
                  <th key={`${c.subject_code}-${c.component_key}-${i}`}>{c.component_label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.students.map((row) => (
                <tr key={row.student_usn}>
                  <td className="mcim-sticky">{row.student_usn}</td>
                  <td className="mcim-sticky-2">{row.student_name || '—'}</td>
                  {(row.scores || []).map((sc, j) => (
                    <td key={j}>{sc != null && sc !== '' ? sc : '—'}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default MentorConsolidatedInternalMarks;
