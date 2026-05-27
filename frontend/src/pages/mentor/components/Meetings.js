import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Select from "react-select";
import "../../../assets/css/Meetings.css";
import { API_BASE_URL } from "../../../api";

const Meetings = () => {
  const { mentor_id } = useParams();
  const [assignedStudents, setAssignedStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [meetingDate, setMeetingDate] = useState("");
  const [venue, setVenue] = useState("");
  const [meetingMode, setMeetingMode] = useState("offline");
  const [meetings, setMeetings] = useState([]);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [newMeetingSuccess, setNewMeetingSuccess] = useState(false);
  const [loading, setLoading] = useState(false); // Loader state
  const [updateNotesModal, setUpdateNotesModal] = useState(false); // Modal for updating notes
  const [selectedMeetingId, setSelectedMeetingId] = useState(null); // ID of the meeting to update
  const [progressNotes, setProgressNotes] = useState(""); // New notes to update

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/meetings`);
        if (!response.ok) throw new Error("Failed to fetch meetings");
        const data = await response.json();
        setMeetings(data.meetings || []);
      } catch (err) {
        setError(err.message || "Error fetching meetings");
      }
    };

    fetchMeetings();
  }, [mentor_id, newMeetingSuccess]);

  useEffect(() => {
    const fetchAssignedStudents = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/mentor/${mentor_id}/assigned_students`
        );
        if (!response.ok) throw new Error("Failed to fetch students");
        const data = await response.json();
        setAssignedStudents(
          data.map((student) => ({
            value: student.student_usn,
            label: `${student.student_name} (${student.student_usn})`,
          }))
        );
      } catch (err) {
        setError(err.message || "Error fetching students");
      }
    };

    fetchAssignedStudents();
  }, [mentor_id]);

  const handleUpdateNotes = async () => {
    if (!progressNotes.trim()) {
      alert("Please enter the remark!");
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/${selectedMeetingId}/log_meeting`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ progress_notes: progressNotes }),
        }
      );

      if (!response.ok) throw new Error("Failed to update remark");

      alert("Remark updated successfully!");

      setMeetings((prevMeetings) =>
        prevMeetings.map((meeting) =>
          meeting.meeting_id === selectedMeetingId
            ? { ...meeting, progress_notes: progressNotes }
            : meeting
        )
      );
      setUpdateNotesModal(false); // Close the modal after update
    } catch (err) {
      setError(err.message || "Error updating remark");
    }
  };

  const handleScheduleMeeting = async () => {
    if (selectedStudents.length === 0 || !meetingDate) {
      alert("Please select students and date/time!");
      return;
    }
    if (meetingMode === "offline" && !venue.trim()) {
      alert("Please enter venue for offline meetings.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Send local time directly (meetingDate from datetime-local input is already in local format)
      const formattedDate = meetingDate;
      const studentUsns = selectedStudents.map((student) => student.value);

      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/schedule_meeting`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          meeting_date: formattedDate,
          venue: meetingMode === "online" ? "Online" : venue.trim(),
          meeting_mode: meetingMode,
          student_usns: studentUsns,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to schedule meeting");
      }

      alert("Meetings scheduled successfully!");
      setNewMeetingSuccess(true);
      setShowModal(false);
      setSelectedStudents([]);
      setMeetingDate("");
      setVenue("");
      setMeetingMode("offline");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const convertToLocalTime = (utcDate) => {
    if (!utcDate) return "Invalid Date";

    return new Date(utcDate).toLocaleString("en-IN", {
      timeZone: "Asia/Kolkata",
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  return (
    <div>
      <h1 className="meetings__title">Meetings with Mentor: {mentor_id}</h1>
      {error && <p className="meetings__error">{error}</p>}

      <button
        className="meetings__button meetings__button--schedule"
        onClick={() => setShowModal(true)}
      >
        Schedule New Meeting
      </button>

      {showModal && (
        <div className="meetings__modal">
          <div className="meetings__modal-content">
            <h2 className="meetings__modal-title">Schedule New Meeting</h2>

            <Select
  className="meetings__dropdown"
  options={[
    { value: "all", label: "Select All" }, // Add "Select All" option
    ...assignedStudents,
  ]}
  isMulti
  placeholder="Select Students"
  value={selectedStudents}
  onChange={(selectedOptions) => {
    if (selectedOptions.some((option) => option.value === "all")) {
      setSelectedStudents(assignedStudents); // Select all students
    } else {
      setSelectedStudents(selectedOptions); // Set selected students
    }
  }}
/>

            <input
              className="meetings__input meetings__input--datetime"
              type="datetime-local"
              value={meetingDate}
              onChange={(e) => setMeetingDate(e.target.value)}
            />

            <label className="meetings__label">Mode of meeting</label>
            <div className="meetings__mode-options">
              <label className="meetings__mode-option">
                <input
                  type="radio"
                  name="meetingMode"
                  value="online"
                  checked={meetingMode === "online"}
                  onChange={(e) => setMeetingMode(e.target.value)}
                />
                <span>Online</span>
              </label>
              <label className="meetings__mode-option">
                <input
                  type="radio"
                  name="meetingMode"
                  value="offline"
                  checked={meetingMode === "offline"}
                  onChange={(e) => setMeetingMode(e.target.value)}
                />
                <span>Offline</span>
              </label>
            </div>

            {meetingMode === "offline" && (
              <input
                className="meetings__input"
                type="text"
                placeholder="Venue / Location"
                value={venue}
                onChange={(e) => setVenue(e.target.value)}
              />
            )}
            {meetingMode === "online" && (
              <p className="meetings__online-note">A Google Meet link will be generated and sent to students.</p>
            )}

            <button
              className="meetings__button meetings__button--submit"
              onClick={handleScheduleMeeting}
              disabled={loading} // Disable button while loading
            >
              {loading ? "Scheduling..." : "Schedule Meeting"} {/* Show loader text */}
            </button>
            <button
              className="meetings__button meetings__button--close"
              onClick={() => setShowModal(false)}
              disabled={loading} // Disable closing while loading
            >
              Close
            </button>
          </div>
        </div>
      )}

      {updateNotesModal && (
        <div className="meetings__modal">
          <div className="meetings__modal-content">
            <h2 className="meetings__modal-title">Edit remark</h2>

            <textarea
              className="meetings__input meetings__textarea--remark"
              placeholder="Enter remark after the meeting..."
              value={progressNotes}
              onChange={(e) => setProgressNotes(e.target.value)}
            ></textarea>

            <button
              className="meetings__button meetings__button--submit"
              onClick={handleUpdateNotes}
            >
              Save remark
            </button>
            <button
              className="meetings__button meetings__button--close"
              onClick={() => setUpdateNotesModal(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      <h2 className="meetings__list-title">Existing Meetings</h2>
      {meetings.length === 0 ? (
        <p className="meetings__no-records">No meetings found for this mentor.</p>
      ) : (
        <div className="meetings__table-container">
          <table className="meetings__table">
            <thead>
              <tr className="meetings__table-header">
                <th>Student USN</th>
                <th>Name</th>
                <th>DateTime</th>
                <th>Mode</th>
                <th>Venue</th>
                <th>Status</th>
                <th>Remark</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {meetings.map((meeting) => {
                const mode = meeting.meeting_mode || "offline";
                const hasMeetLink = mode === "online" && meeting.google_meet_link;
                return (
                  <tr key={meeting.meeting_id}>
                    <td>{meeting.student_usn}</td>
                    <td>{meeting.student_name || "—"}</td>
                    <td>{convertToLocalTime(meeting.meeting_date)}</td>
                    <td>
                      <span className={`meeting-mode-badge meeting-mode-badge--${mode}`}>
                        {mode === "online" ? "Online" : "Offline"}
                      </span>
                    </td>
                    <td>{meeting.venue}</td>
                    <td>{meeting.status || "—"}</td>
                    <td className="meetings__remark-cell">{meeting.progress_notes || "—"}</td>
                    <td>
                      <div className="meetings__row-actions">
                        {hasMeetLink && (
                          <a
                            href={meeting.google_meet_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="meetings__button meetings__button--start"
                          >
                            Start meeting
                          </a>
                        )}
                        <button
                          className="meetings__button meetings__button--update"
                          onClick={() => {
                            setSelectedMeetingId(meeting.meeting_id);
                            setProgressNotes(meeting.progress_notes || "");
                            setUpdateNotesModal(true);
                          }}
                        >
                          Edit remark
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <br /><br />
          <br /><br />
          <br /><br />
          <br />
          <br />
        </div>
      )}
    </div>
  );
};

export default Meetings;
