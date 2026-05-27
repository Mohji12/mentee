import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { API_BASE_URL } from "../../../api";
import '../../../assets/css/Appointments.css';

const Appointments = () => {
  const { mentor_id } = useParams();
  const [meetings, setMeetings] = useState([]);
  const [error, setError] = useState("");
  const [selectedMeetingId, setSelectedMeetingId] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/pending_meetings`);
        if (!response.ok) throw new Error("Failed to fetch meetings");
        const data = await response.json();
        const updatedMeetings = data.map(meeting => {
          const meetingDate = new Date(meeting.meeting_date);
          meetingDate.setHours(meetingDate.getHours() + 5);
          meetingDate.setMinutes(meetingDate.getMinutes() + 30);
          meeting.meeting_date = meetingDate.toLocaleString();
          return meeting;
        });
        setMeetings(updatedMeetings);
      } catch {
        setError("Failed to fetch meetings");
      }
    };
    fetchMeetings();
  }, [mentor_id]);

  const handleVerifyClick = (meetingId) => {
    setSelectedMeetingId(meetingId);
    setShowModal(true);
  };

  const handleResponse = async (status) => {
    try {
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/${selectedMeetingId}/respond_meeting`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!response.ok) throw new Error("Failed to update meeting");
      setMeetings(prev => prev.filter(m => m.id !== selectedMeetingId));
    } catch (error) {
      console.error("Error updating meeting:", error);
    } finally {
      setShowModal(false);
    }
  };

  return (
    <div className="meeting-portal-container">
      <div className="meeting-portal-title" style={{fontWeight:600,fontSize:'2rem',letterSpacing:'0.02em',marginBottom:24}}>
        Pending Mentor Appointments
      </div>
      {error && <div className="status-message error">{error}</div>}
      <div className="appointments-card-bg">
        {meetings.length === 0 ? (
          <div className="mentor-meetings-no-schedule">
            No pending meetings scheduled.
          </div>
        ) : (
          <div className="mentor-meetings-table-container">
            <table className="meeting-table redesigned-meeting-table mentor-appointments-table">
              <thead>
                <tr>
                  <th>Meeting ID</th>
                  <th>Student USN</th>
                  <th>Name</th>
                  <th>Date/Time</th>
                  <th>Mode</th>
                  <th>Venue / Location</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {meetings.map((meeting, idx) => {
                  const mode = meeting.meeting_mode || "offline";
                  const names = meeting.student_names;
                  const nameDisplay = Array.isArray(names)
                    ? names.filter(Boolean).join(", ") || "—"
                    : names || "—";
                  return (
                    <tr key={meeting.id} className={idx % 2 === 0 ? "alt-row" : ""}>
                      <td>{meeting.id}</td>
                      <td>{Array.isArray(meeting.student_usn) ? meeting.student_usn.join(", ") : meeting.student_usn}</td>
                      <td>{nameDisplay}</td>
                      <td>{meeting.meeting_date}</td>
                      <td>
                        <span className={`meeting-mode-badge meeting-mode-badge--${mode}`}>
                          {mode === "online" ? "Online" : "Offline"}
                        </span>
                      </td>
                      <td>{meeting.venue}</td>
                      <td>
                        <button
                          onClick={() => handleVerifyClick(meeting.id)}
                          className="verify-btn redesigned-verify-btn"
                          title="Verify and respond to this meeting"
                        >
                          Verify
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content modal-appointment-pop">
            <h2 style={{ textAlign: "center", marginBottom: 16 }}>Approve or Reject Meeting?</h2>
            <p style={{ fontWeight: "bold", textAlign: "center" }}>Meeting ID: {selectedMeetingId}</p>
            <div className="modal-actions redesigned-modal-actions">
              <button
                onClick={() => handleResponse("approved")}
                className="modal-approve"
              >
                Approve
              </button>
              <button
                onClick={() => handleResponse("rejected")}
                className="modal-reject"
              >
                Reject
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="modal-cancel"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;
