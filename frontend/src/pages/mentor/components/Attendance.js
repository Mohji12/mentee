import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import { FaCheck, FaTimes, FaClock, FaEdit } from "react-icons/fa";
import "../../../assets/css/Attendance.css";
import { API_BASE_URL } from "../../../api";

const Attendance = () => {
  const { mentor_id } = useParams();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [sessionName, setSessionName] = useState("");
  const [duration, setDuration] = useState(30);
  const [location, setLocation] = useState("");
  const [currentQR, setCurrentQR] = useState(null);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [showRecordsModal, setShowRecordsModal] = useState(false);
  
  // Manual attendance states
  const [showManualModal, setShowManualModal] = useState(false);
  const [selectedSessionId, setSelectedSessionId] = useState("");
  const [studentsList, setStudentsList] = useState([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [markingAttendance, setMarkingAttendance] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);

  // Dashboard stats
  const [dashboardStats, setDashboardStats] = useState(null);

  // Weekly report
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [weekStartParam, setWeekStartParam] = useState("");
  const [loadingWeeklyReport, setLoadingWeeklyReport] = useState(false);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/attendance/stats`);
      if (!response.ok) return;
      const data = await response.json();
      setDashboardStats(data);
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  const fetchSessions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/attendance/sessions`);
      if (!response.ok) throw new Error("Failed to fetch sessions");
      const data = await response.json();
      setSessions(data);
    } catch (err) {
      setError(err.message || "Error fetching sessions");
    }
  };

  useEffect(() => {
    fetchSessions();
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mentor_id]);

  useEffect(() => {
    if (!mentor_id) return;
    const params = new URLSearchParams();
    if (weekStartParam) params.set("week_start", weekStartParam);
    const url = `${API_BASE_URL}/mentor/${mentor_id}/attendance/weekly-report${params.toString() ? "?" + params.toString() : ""}`;
    setLoadingWeeklyReport(true);
    fetch(url)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setWeeklyReport(data))
      .catch(() => setWeeklyReport(null))
      .finally(() => setLoadingWeeklyReport(false));
  }, [mentor_id, weekStartParam]);

  const generateQRCode = async () => {
    if (!sessionName.trim()) {
      alert("Please enter a session name");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/attendance/generate-qr`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_name: sessionName,
          duration_minutes: duration,
          location: location,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate QR code");
      }

      const data = await response.json();
      setCurrentQR(data);
      setShowGenerateModal(false);
      setSessionName("");
      setLocation("");
      setDuration(30);
      fetchSessions();
      fetchStats();
    } catch (err) {
      setError(err.message || "Error generating QR code");
    } finally {
      setLoading(false);
    }
  };

  const fetchAttendanceRecords = async (sessionId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/attendance/records/${sessionId}`
      );
      if (!response.ok) throw new Error("Failed to fetch attendance records");
      const data = await response.json();
      setAttendanceRecords(data);
      setShowRecordsModal(true);
    } catch (err) {
      setError(err.message || "Error fetching attendance records");
    }
  };

  const deactivateSession = async (sessionId) => {
    if (!window.confirm("Are you sure you want to deactivate this session?")) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/attendance/deactivate-session/${sessionId}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) throw new Error("Failed to deactivate session");
      
      alert("Session deactivated successfully");
      fetchSessions();
      fetchStats();
    } catch (err) {
      setError(err.message || "Error deactivating session");
    }
  };

  const formatDate = (dateString) => {
    // Database stores IST as naive datetime, format it as IST
    const date = new Date(dateString);
    // Format as IST time (Asia/Kolkata timezone)
    return date.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const isExpired = (expiresAt) => {
    // Compare IST times - database stores IST as naive datetime
    const expiryDate = new Date(expiresAt);
    const now = new Date();
    // Since both are stored/interpreted as IST, direct comparison works
    return expiryDate < now;
  };

  const fetchStudentsForManualAttendance = async (sessionId) => {
    if (!sessionId) return;
    
    setLoadingStudents(true);
    setError("");
    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/attendance/manual/${sessionId}`
      );
      if (!response.ok) throw new Error("Failed to fetch students");
      const data = await response.json();
      setStudentsList(data.students || []);
    } catch (err) {
      setError(err.message || "Error fetching students");
      setStudentsList([]);
    } finally {
      setLoadingStudents(false);
    }
  };

  const handleManualAttendanceClick = () => {
    setShowManualModal(true);
    setSelectedSessionId("");
    setStudentsList([]);
  };

  const handleSessionSelect = (sessionId) => {
    setSelectedSessionId(sessionId);
    fetchStudentsForManualAttendance(sessionId);
  };

  const markAttendance = async (studentUsn, status, notes = "") => {
    setMarkingAttendance(true);
    setError("");
    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/attendance/manual-mark`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: selectedSessionId,
            student_usn: studentUsn,
            status: status,
            notes: notes,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to mark attendance");
      }

      // Refresh students list to show updated attendance
      await fetchStudentsForManualAttendance(selectedSessionId);
      setEditingStudent(null);
      fetchStats();
    } catch (err) {
      setError(err.message || "Error marking attendance");
    } finally {
      setMarkingAttendance(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case "present":
        return "#28a745";
      case "absent":
        return "#dc3545";
      case "late":
        return "#ffc107";
      default:
        return "#6c757d";
    }
  };

  const markAllPresent = async () => {
    const toMark = studentsList.filter((s) => !s.has_attendance || (s.status || "").toLowerCase() !== "present");
    if (toMark.length === 0) {
      alert("All students are already marked present.");
      return;
    }
    setMarkingAttendance(true);
    setError("");
    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/attendance/manual-mark-bulk`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: selectedSessionId,
            students: toMark.map((s) => ({ student_usn: s.student_usn, status: "present", notes: null })),
          }),
        }
      );
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to mark attendance");
      }
      await fetchStudentsForManualAttendance(selectedSessionId);
      fetchStats();
    } catch (err) {
      setError(err.message || "Error marking all present");
    } finally {
      setMarkingAttendance(false);
    }
  };

  const activeSessionsForManual = sessions.filter((s) => s.is_active && !isExpired(s.expires_at));

  return (
    <div className="attendance-container">
      <div className="attendance-header">
        <h2>Attendance Management</h2>
      </div>

      {dashboardStats && (
        <div className="attendance-dashboard">
          <div className="stat-card">
            <span className="stat-label">Total Sessions</span>
            <span className="stat-value">{dashboardStats.total_sessions}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Active Sessions</span>
            <span className="stat-value">{dashboardStats.active_sessions}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Assigned Students</span>
            <span className="stat-value">{dashboardStats.assigned_students_count}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Attendance Marked</span>
            <span className="stat-value">{dashboardStats.total_records}</span>
          </div>
          <div className="stat-card stat-card--present">
            <span className="stat-label">Present</span>
            <span className="stat-value">{dashboardStats.present_count}</span>
          </div>
          <div className="stat-card stat-card--absent">
            <span className="stat-label">Absent</span>
            <span className="stat-value">{dashboardStats.absent_count}</span>
          </div>
          <div className="stat-card stat-card--late">
            <span className="stat-label">Late</span>
            <span className="stat-value">{dashboardStats.late_count}</span>
          </div>
          <div className="stat-card stat-card--week">
            <span className="stat-label">This Week (Present)</span>
            <span className="stat-value">{dashboardStats.this_week_present ?? 0}</span>
          </div>
        </div>
      )}

      <div className="header-buttons">
        <button
          className="btn-manual-attendance"
          onClick={handleManualAttendanceClick}
        >
          Manual Attendance
        </button>
        <button
          className="btn-generate-qr"
          onClick={() => setShowGenerateModal(true)}
        >
          Generate QR Code
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {currentQR && (
        <div className="qr-display-modal">
          <div className="qr-display-content">
            <h3>QR Code Generated Successfully!</h3>
            <div className="qr-code-display">
              <QRCodeSVG value={currentQR.qr_code_data} size={256} />
            </div>
            <p><strong>Session:</strong> {currentQR.session_name || "Unnamed Session"}</p>
            <p><strong>Expires at:</strong> {formatDate(currentQR.expires_at)}</p>
            <button
              className="btn-close"
              onClick={() => setCurrentQR(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {showGenerateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Generate QR Code</h3>
            <div className="form-group">
              <label>Session Name:</label>
              <input
                type="text"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                placeholder="e.g., Morning Session"
              />
            </div>
            <div className="form-group">
              <label>Duration (minutes):</label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value) || 30)}
                min="1"
                max="1440"
              />
            </div>
            <div className="form-group">
              <label>Location (optional):</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g., Room 101"
              />
            </div>
            <div className="modal-actions">
              <button
                className="btn-primary"
                onClick={generateQRCode}
                disabled={loading}
              >
                {loading ? "Generating..." : "Generate QR Code"}
              </button>
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowGenerateModal(false);
                  setSessionName("");
                  setLocation("");
                  setDuration(30);
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="sessions-list">
        <h3>Attendance Sessions</h3>
        {sessions.length === 0 ? (
          <p>No sessions created yet. Generate a QR code to get started.</p>
        ) : (
          <>
            {/* Desktop Table View */}
            <table className="sessions-table">
              <thead>
                <tr>
                  <th>Session Name</th>
                  <th>Created At</th>
                  <th>Expires At</th>
                  <th>Location</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.session_id}>
                    <td>{session.session_name || "Unnamed Session"}</td>
                    <td>{formatDate(session.created_at)}</td>
                    <td>{formatDate(session.expires_at)}</td>
                    <td>{session.location || "N/A"}</td>
                    <td>
                      <span
                        className={`status-badge ${
                          !session.is_active
                            ? "inactive"
                            : isExpired(session.expires_at)
                            ? "expired"
                            : "active"
                        }`}
                      >
                        {!session.is_active
                          ? "Inactive"
                          : isExpired(session.expires_at)
                          ? "Expired"
                          : "Active"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-view"
                        onClick={() => fetchAttendanceRecords(session.session_id)}
                      >
                        View Records
                      </button>
                      <button
                        className="btn-manual"
                        onClick={() => {
                          setShowManualModal(true);
                          handleSessionSelect(session.session_id);
                        }}
                        title="Mark attendance manually"
                      >
                        Mark Manually
                      </button>
                      {session.is_active && !isExpired(session.expires_at) && (
                        <button
                          className="btn-deactivate"
                          onClick={() => deactivateSession(session.session_id)}
                        >
                          Deactivate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Mobile Card View */}
            <div className="sessions-table-mobile">
              {sessions.map((session) => (
                <div key={session.session_id} className="session-card">
                  <div className="session-card-header">
                    <div className="session-card-name">
                      {session.session_name || "Unnamed Session"}
                    </div>
                    <div className="session-card-status">
                      <span
                        className={`status-badge ${
                          !session.is_active
                            ? "inactive"
                            : isExpired(session.expires_at)
                            ? "expired"
                            : "active"
                        }`}
                      >
                        {!session.is_active
                          ? "Inactive"
                          : isExpired(session.expires_at)
                          ? "Expired"
                          : "Active"}
                      </span>
                    </div>
                  </div>
                  <div className="session-card-info">
                    <strong>Created:</strong> {formatDate(session.created_at)}
                  </div>
                  <div className="session-card-info">
                    <strong>Expires:</strong> {formatDate(session.expires_at)}
                  </div>
                  <div className="session-card-info">
                    <strong>Location:</strong> {session.location || "N/A"}
                  </div>
                  <div className="session-card-actions">
                    <button
                      className="btn-view"
                      onClick={() => fetchAttendanceRecords(session.session_id)}
                    >
                      View Records
                    </button>
                    <button
                      className="btn-manual"
                      onClick={() => {
                        setShowManualModal(true);
                        handleSessionSelect(session.session_id);
                      }}
                    >
                      Mark Manually
                    </button>
                    {session.is_active && !isExpired(session.expires_at) && (
                      <button
                        className="btn-deactivate"
                        onClick={() => deactivateSession(session.session_id)}
                      >
                        Deactivate
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Weekly Attendance Report */}
      <section className="weekly-report-section">
        <h3>Weekly Attendance Report</h3>
        <div className="weekly-report-controls">
          <button
            type="button"
            className="btn-week-nav"
            onClick={() => {
              if (weeklyReport?.week_start) {
                const d = new Date(weeklyReport.week_start);
                d.setDate(d.getDate() - 7);
                setWeekStartParam(d.toISOString().slice(0, 10));
              } else {
                const today = new Date();
                const day = today.getDay();
                const diff = day === 0 ? 6 : day - 1;
                const monday = new Date(today);
                monday.setDate(monday.getDate() - diff - 7);
                setWeekStartParam(monday.toISOString().slice(0, 10));
              }
            }}
          >
            Previous week
          </button>
          <span className="weekly-report-range">
            {weeklyReport
              ? `${weeklyReport.week_start} – ${weeklyReport.week_end}`
              : loadingWeeklyReport
              ? "Loading..."
              : "Select week"}
          </span>
          <button
            type="button"
            className="btn-week-nav"
            onClick={() => {
              if (weeklyReport?.week_start) {
                const d = new Date(weeklyReport.week_start);
                d.setDate(d.getDate() + 7);
                setWeekStartParam(d.toISOString().slice(0, 10));
              } else {
                const today = new Date();
                const day = today.getDay();
                const diff = day === 0 ? 6 : day - 1;
                const monday = new Date(today);
                monday.setDate(monday.getDate() - diff + 7);
                setWeekStartParam(monday.toISOString().slice(0, 10));
              }
            }}
          >
            Next week
          </button>
          <input
            type="date"
            className="weekly-report-date-input"
            value={weekStartParam}
            onChange={(e) => setWeekStartParam(e.target.value || "")}
            title="Pick Monday of week"
          />
        </div>
        {loadingWeeklyReport && <p className="weekly-report-loading">Loading report...</p>}
        {!loadingWeeklyReport && weeklyReport && (
          <div className="weekly-report-table-wrap">
            <table className="weekly-report-table">
              <thead>
                <tr>
                  <th>Student USN</th>
                  <th>Name</th>
                  <th>Present</th>
                  <th>Absent</th>
                  <th>Late</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {weeklyReport.students.map((row) => (
                  <tr key={row.student_usn}>
                    <td>{row.student_usn}</td>
                    <td>{row.student_name || "—"}</td>
                    <td>{row.present_count ?? 0}</td>
                    <td>{row.absent_count ?? 0}</td>
                    <td>{row.late_count ?? 0}</td>
                    <td className="weekly-report-details">
                      {row.records && row.records.length > 0
                        ? row.records.map((r, i) => (
                            <span key={i} className="weekly-report-detail-chip">
                              {r.session_name || r.session_id} ({r.status}) {r.marked_at ? new Date(r.marked_at).toLocaleDateString() : ""}
                            </span>
                          ))
                        : "No records"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {showRecordsModal && (
        <div className="modal-overlay">
          <div className="modal-content records-modal">
            <h3>Attendance Records</h3>
            {attendanceRecords.length === 0 ? (
              <p>No attendance records for this session yet.</p>
            ) : (
              <>
                {/* Desktop Table View */}
                <table className="records-table">
                  <thead>
                    <tr>
                      <th>Student USN</th>
                      <th>Student Name</th>
                      <th>Marked At</th>
                      <th>Status</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendanceRecords.map((record) => (
                      <tr key={record.id}>
                        <td>{record.student_usn}</td>
                        <td>{record.student_name || "N/A"}</td>
                        <td>{formatDate(record.marked_at)}</td>
                        <td>
                          <span className={`status-badge ${record.status}`}>
                            {record.status}
                          </span>
                        </td>
                        <td>{record.notes || "N/A"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Mobile Card View */}
                <div className="records-table-mobile">
                  {attendanceRecords.map((record) => (
                    <div key={record.id} className="record-card">
                      <div className="record-card-info">
                        <strong>USN:</strong> {record.student_usn}
                      </div>
                      <div className="record-card-info">
                        <strong>Name:</strong> {record.student_name || "N/A"}
                      </div>
                      <div className="record-card-info">
                        <strong>Marked At:</strong> {formatDate(record.marked_at)}
                      </div>
                      <div className="record-card-info">
                        <strong>Status:</strong>{" "}
                        <span className={`status-badge ${record.status}`}>
                          {record.status}
                        </span>
                      </div>
                      <div className="record-card-info">
                        <strong>Notes:</strong> {record.notes || "N/A"}
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
            <button
              className="btn-close"
              onClick={() => {
                setShowRecordsModal(false);
                setAttendanceRecords([]);
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Manual Attendance Modal */}
      {showManualModal && (
        <div className="modal-overlay">
          <div className="modal-content manual-attendance-modal">
            <h3>Manual Attendance</h3>
            
            {!selectedSessionId ? (
              <div className="session-selector">
                <p className="manual-attendance-hint">Select an existing session to mark attendance for your assigned students.</p>
                {activeSessionsForManual.length === 0 ? (
                  <div className="no-active-sessions-msg">
                    <p>No active sessions. Generate a QR session first or use an existing session to mark attendance.</p>
                    <button
                      type="button"
                      className="btn-primary"
                      onClick={() => {
                        setShowManualModal(false);
                        setShowGenerateModal(true);
                      }}
                    >
                      Generate QR Code
                    </button>
                  </div>
                ) : (
                  <>
                    <label>Select Session:</label>
                    <select
                      value={selectedSessionId}
                      onChange={(e) => handleSessionSelect(e.target.value)}
                      className="session-select"
                    >
                      <option value="">-- Select a session --</option>
                      {activeSessionsForManual.map((session) => (
                        <option key={session.session_id} value={session.session_id}>
                          {session.session_name || "Unnamed Session"} - {formatDate(session.created_at)}
                        </option>
                      ))}
                    </select>
                  </>
                )}
              </div>
            ) : (
              <>
                <div className="manual-attendance-header">
                  <div>
                    <strong>Session:</strong>{" "}
                    {sessions.find((s) => s.session_id === selectedSessionId)?.session_name ||
                      "Unnamed Session"}
                  </div>
                  <div className="manual-attendance-header-actions">
                    <button
                      type="button"
                      className="btn-mark-all-present"
                      onClick={markAllPresent}
                      disabled={markingAttendance || studentsList.every((s) => s.has_attendance && (s.status || "").toLowerCase() === "present")}
                    >
                      {markingAttendance ? "Marking..." : "Mark all Present"}
                    </button>
                    <button
                      className="btn-secondary btn-sm"
                      onClick={() => {
                        setSelectedSessionId("");
                        setStudentsList([]);
                      }}
                    >
                      Change Session
                    </button>
                  </div>
                </div>

                {loadingStudents ? (
                  <div className="loading">Loading students...</div>
                ) : studentsList.length === 0 ? (
                  <div className="no-students">No students assigned to this mentor.</div>
                ) : (
                  <div className="students-attendance-list">
                    <div className="students-list-header">
                      <span>Student</span>
                      <span>Status</span>
                      <span>Actions</span>
                    </div>
                    {studentsList.map((student) => (
                      <div key={student.student_usn} className="student-attendance-item">
                        <div className="student-info">
                          <div className="student-name">{student.student_name || "N/A"}</div>
                          <div className="student-usn">{student.student_usn}</div>
                        </div>
                        <div className="attendance-status">
                          {student.has_attendance ? (
                            <span
                              className="status-badge"
                              style={{ backgroundColor: getStatusColor(student.status) }}
                            >
                              {student.status || "present"}
                            </span>
                          ) : (
                            <span className="status-badge not-marked">Not Marked</span>
                          )}
                        </div>
                        <div className="attendance-actions">
                          {editingStudent === student.student_usn ? (
                            <div className="edit-attendance-form">
                              <select
                                className="status-select"
                                defaultValue={student.status || "present"}
                                onChange={(e) => {
                                  const newStatus = e.target.value;
                                  markAttendance(student.student_usn, newStatus, "");
                                }}
                                disabled={markingAttendance}
                              >
                                <option value="present">Present</option>
                                <option value="absent">Absent</option>
                                <option value="late">Late</option>
                              </select>
                              <button
                                className="btn-cancel-edit"
                                onClick={() => setEditingStudent(null)}
                                disabled={markingAttendance}
                              >
                                Cancel
                              </button>
                            </div>
                          ) : (
                            <div className="action-buttons">
                              {!student.has_attendance ? (
                                <>
                                  <button
                                    className="btn-mark-present"
                                    onClick={() => markAttendance(student.student_usn, "present")}
                                    disabled={markingAttendance}
                                    title="Mark as Present"
                                  >
                                    <FaCheck /> Present
                                  </button>
                                  <button
                                    className="btn-mark-absent"
                                    onClick={() => markAttendance(student.student_usn, "absent")}
                                    disabled={markingAttendance}
                                    title="Mark as Absent"
                                  >
                                    <FaTimes /> Absent
                                  </button>
                                  <button
                                    className="btn-mark-late"
                                    onClick={() => markAttendance(student.student_usn, "late")}
                                    disabled={markingAttendance}
                                    title="Mark as Late"
                                  >
                                    <FaClock /> Late
                                  </button>
                                </>
                              ) : (
                                <button
                                  className="btn-edit"
                                  onClick={() => setEditingStudent(student.student_usn)}
                                  disabled={markingAttendance}
                                  title="Edit Attendance"
                                >
                                  <FaEdit /> Edit
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            <div className="modal-actions">
              <button
                className="btn-close"
                onClick={() => {
                  setShowManualModal(false);
                  setSelectedSessionId("");
                  setStudentsList([]);
                  setEditingStudent(null);
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Attendance;

