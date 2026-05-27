import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { API_BASE_URL } from "../../../api";
import '../../../assets/css/Appointments.css';

const StudentScheduleMeeting = () => {
  const { student_usn } = useParams();
  const [meetingDate, setMeetingDate] = useState("");
  const [meetingMode, setMeetingMode] = useState("offline");
  const [venue, setVenue] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [meetings, setMeetings] = useState([]);

  const fetchMeetings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/student/${student_usn}/scheduled_pending_meetings`);
      const data = await response.json();
      setMeetings(data.meetings || []);
    } catch (err) {
      console.error("Failed to fetch meetings:", err);
    }
  };

  useEffect(() => {
    fetchMeetings();
  }, [student_usn]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatusMessage("");
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/student/${student_usn}/request_meeting`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          meeting_date: meetingDate,
          meeting_mode: meetingMode,
          venue: meetingMode === "offline" ? venue : "Online",
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to schedule meeting.");
      }

      const data = await response.json();
      setStatusMessage(`Meeting request sent successfully! ID: ${data.meeting_id}`);
      setMeetingDate("");
      setVenue("");
      fetchMeetings();
      setModalOpen(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="meeting-portal-container">
      <h2 className="meeting-portal-title">Schedule your meeting in a click...</h2>

      <button className="open-modal-button" onClick={() => setModalOpen(true)}>
        + Schedule New Meeting
      </button>

      {statusMessage && <p className="status-message success">{statusMessage}</p>}
      {error && <p className="status-message error">{error}</p>}

      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Request a Meeting</h3>
            <form onSubmit={handleSubmit} className="meeting-form-modal">
              <label>
                Meeting Date & Time:
                <input
                  type="datetime-local"
                  value={meetingDate}
                  onChange={(e) => setMeetingDate(e.target.value)}
                  required
                  disabled={loading}
                />
              </label>
              <label className="meeting-mode-label">Mode of meeting:</label>
              <div className="meeting-mode-options">
                <label className="mode-option">
                  <input
                    type="radio"
                    name="meetingMode"
                    value="online"
                    checked={meetingMode === "online"}
                    onChange={(e) => setMeetingMode(e.target.value)}
                    disabled={loading}
                  />
                  <span>Online</span>
                </label>
                <label className="mode-option">
                  <input
                    type="radio"
                    name="meetingMode"
                    value="offline"
                    checked={meetingMode === "offline"}
                    onChange={(e) => setMeetingMode(e.target.value)}
                    disabled={loading}
                  />
                  <span>Offline</span>
                </label>
              </div>
              {meetingMode === "offline" && (
                <label>
                  Location:
                  <input
                    type="text"
                    value={venue}
                    onChange={(e) => setVenue(e.target.value)}
                    required
                    disabled={loading}
                    placeholder="Enter meeting location"
                  />
                </label>
              )}
              {meetingMode === "online" && (
                <p className="meeting-online-note">Meeting will be held online. A Google Meet link will be shared after your mentor approves.</p>
              )}
              <div className="modal-buttons">
                <button type="submit" disabled={loading}>
                  {loading ? "Requesting..." : "Submit Request"}
                </button>
                <button type="button" onClick={() => setModalOpen(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <h3 className="meeting-table-title">Scheduled Meetings</h3>
      <div className="meetings-section-content">
        {meetings.length === 0 ? (
          <p className="meetings-empty">No meetings found.</p>
        ) : (
          <div className="meeting-cards-list">
            {meetings.map((meeting) => {
              const mode = meeting.meeting_mode || "offline";
              const isOnlineApproved = mode === "online" && meeting.status === "approved" && meeting.google_meet_link;
              return (
                <div key={meeting.meeting_id} className="meeting-card">
                  <div className="meeting-card-header">
                    <span className="meeting-card-id">{meeting.meeting_id}</span>
                    <span className={`meeting-mode-badge meeting-mode-badge--${mode}`}>
                      {mode === "online" ? "Online" : "Offline"}
                    </span>
                  </div>
                  <div className="meeting-card-body">
                    <p><strong>Mentor:</strong> {meeting.mentor_id}</p>
                    <p><strong>Date & Time:</strong> {new Date(meeting.meeting_date).toLocaleString()}</p>
                    <p><strong>Location:</strong> {meeting.venue}</p>
                    <p><strong>Status:</strong> <span className={`status-badge status-badge--${meeting.status}`}>{meeting.status}</span></p>
                  </div>
                  <div className="meeting-card-actions">
                    {isOnlineApproved && (
                      <a
                        href={meeting.google_meet_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-start-meeting"
                      >
                        Start meeting
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default StudentScheduleMeeting;
