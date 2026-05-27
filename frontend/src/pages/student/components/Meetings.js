import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import '../../../assets/css/StudentMeetings.css';
import { API_BASE_URL } from "../../../api";

const StudentMeetings = () => {
  const { student_usn } = useParams();
  const [meetings, setMeetings] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/student/${student_usn}/meetings`);
        if (!response.ok) throw new Error("Failed to fetch meetings");
        const data = await response.json();

        const updatedMeetings = data.meetings.map(meeting => {
          // Database stores IST directly, just format for display
          const meetingDate = new Date(meeting.meeting_date);
          meeting.meeting_date = meetingDate.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
          return meeting;
        });

        setMeetings(updatedMeetings);
      } catch (err) {
        setError("Failed to fetch meetings");
      }
    };

    fetchMeetings();
  }, [student_usn]);

  const filteredMeetings = meetings.filter(
    (meeting) => meeting.status !== "pending" && meeting.status !== "rejected"
  );

  return (
    <div className="student-meetings-container">
      <h2 className="student-meetings-title">Scheduled Meetings</h2>

      {error && <p className="student-meetings-error">{error}</p>}

      {filteredMeetings.length === 0 ? (
        <p className="student-meetings-no-schedule">No meetings scheduled yet.</p>
      ) : (
        <div className="meeting-cards-list student-meetings-cards">
          {filteredMeetings.map((meeting) => {
            const mode = meeting.meeting_mode || "offline";
            const isOnlineWithLink = mode === "online" && meeting.google_meet_link;
            return (
              <div key={meeting.meeting_id} className="meeting-card student-meeting-card">
                <div className="meeting-card-header">
                  <span className="meeting-card-id">{meeting.meeting_id}</span>
                  <span className={`meeting-mode-badge meeting-mode-badge--${mode}`}>
                    {mode === "online" ? "Online" : "Offline"}
                  </span>
                </div>
                <div className="meeting-card-body">
                  <p><strong>Mentor:</strong> {meeting.mentor_id}</p>
                  <p><strong>Date & Time:</strong> {meeting.meeting_date}</p>
                  <p><strong>Location:</strong> {meeting.venue}</p>
                  <p><strong>Status:</strong> <span className={`status-badge status-badge--${meeting.status}`}>{meeting.status}</span></p>
                  {meeting.progress_notes && (
                    <p><strong>Progress Notes:</strong> {meeting.progress_notes}</p>
                  )}
                </div>
                <div className="meeting-card-actions">
                  {isOnlineWithLink && (
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
  );
};

export default StudentMeetings;
