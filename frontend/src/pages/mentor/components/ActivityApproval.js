import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { API_BASE_URL } from "../../../api";
import Modal from "react-modal";
import '../../../assets/css/Appointments.css';
import '../../../assets/css/ActivityApproval.css';

const ActivitiesApproval = () => {
  const { mentor_id } = useParams();
  const [activities, setActivities] = useState([]);
  const [allSubmissions, setAllSubmissions] = useState([]);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [reviewData, setReviewData] = useState({ status: "", percentage: "", rejection_reason: "" });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [activitiesRes, submissionsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/activities/submissions`),
          fetch(`${API_BASE_URL}/mentor/${mentor_id}/submissions`)
        ]);
        if (!activitiesRes.ok || !submissionsRes.ok) throw new Error("Failed to fetch data");
        const [activitiesData, submissionsData] = await Promise.all([
          activitiesRes.json(), submissionsRes.json()
        ]);
        setActivities(activitiesData);
        setAllSubmissions(submissionsData);
      } catch (error) {
        console.error("Error fetching data:", error);
        alert("Error loading data. Please try again later.");
      }
    };
    fetchData();
  }, [mentor_id]);

  const openModal = (activity) => {
    setSelectedActivity(activity);
    setReviewData({ status: "", percentage: "", rejection_reason: "" });
    setModalIsOpen(true);
  };
  const closeModal = () => {
    setModalIsOpen(false);
    setSelectedActivity(null);
  };
  const handleReview = async () => {
    if (!selectedActivity) return;
    const { status, percentage, rejection_reason } = reviewData;
    const payload = { status };
    if (status === "Approved") {
      const parsedPercentage = parseInt(percentage);
      if (isNaN(parsedPercentage)) return alert("Please enter a valid percentage.");
      payload.percentage = parsedPercentage;
    } else if (status === "Rejected") {
      if (!rejection_reason.trim()) return alert("Rejection reason is required.");
      payload.rejection_reason = rejection_reason.trim();
    } else {
      return alert("Please select a status.");
    }
    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/student/${selectedActivity.student_usn}/activities/${selectedActivity.activity_id}/review`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      );
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Review failed");
      }
      const updatedActivitiesRes = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/activities/submissions`);
      if (!updatedActivitiesRes.ok) throw new Error("Failed to refresh activities");
      const updatedActivities = await updatedActivitiesRes.json();
      setActivities(updatedActivities);
      closeModal();
    } catch (error) {
      console.error("Review error:", error);
      alert(error.message);
    }
  };
  const viewProof = async (student_usn, activity_id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/student/${student_usn}/activities/${activity_id}/proof`);
      if (!response.ok) throw new Error("Failed to fetch proof");
      const data = await response.json();
      window.open(data.proof_url, "_blank");
    } catch (error) {
      console.error("Proof error:", error);
      alert(error.message);
    }
  };

  return (
    <div className="meeting-portal-container">
      <div className="meeting-portal-title" style={{fontWeight:600,fontSize:'2rem',letterSpacing:'0.01em',marginBottom:24}}>All Activity Submissions</div>
      <div className="appointments-card-bg">
        <table className="meeting-table redesigned-meeting-table">
          <thead>
            <tr>
              <th>Submission ID</th>
              <th>Student</th>
              <th>Activity</th>
              <th>Submitted At</th>
              <th>Status</th>
              <th>Compl In</th>
              <th>Percentage</th>
              <th>Proof</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {allSubmissions.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: "center", padding: "1rem" }}>
                  No submissions found.
                </td>
              </tr>
            ) : (
              allSubmissions.map((submission, idx) => {
                const activity = activities.find(
                  (a) => a.student_usn === submission.student_usn && a.activity_id === submission.activity_id
                );
                return (
                  <tr key={submission.submission_id} className={idx%2===0 ? 'alt-row':''}>
                    <td>{submission.submission_id}</td>
                    <td>
                      <strong>{submission.student_usn}</strong>
                      <div style={{fontSize:'0.95em',color:'#767676'}}>{activity?.student_name || "-"}</div>
                    </td>
                    <td>{activity?.activity_name?.split(":")[0] || "-"}</td>
                    <td>{new Date(submission.submitted_at).toLocaleString()}</td>
                    <td>{submission.status}</td>
                    <td>{submission.completed_in || "-"}</td>
                    <td>{(submission.percentage || 0) + '%'}</td>
                    <td>
                      <button onClick={() => viewProof(submission.student_usn, submission.activity_id)}
                       className="verify-btn redesigned-verify-btn" style={{background:'#29A7E0'}}>
                        View
                      </button>
                    </td>
                    <td>
                      {submission.status === "Approved" ? (
                        <span className="status-reviewed" style={{color:'#42b983',fontWeight:600}}>Reviewed</span>
                      ) : (
                        <button onClick={() => openModal({ ...submission, ...activity })} className="verify-btn redesigned-verify-btn">
                          {submission.status === "Pending" ? "Review" : "Re-review"}
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
        <Modal isOpen={modalIsOpen} onRequestClose={closeModal} contentLabel="Review Activity Modal"
          style={{ overlay:{backgroundColor:'rgba(0,0,0,0.38)',zIndex:1500}, content:{borderRadius:16,maxWidth:410,margin:'auto'} }}>
          <div className="modal-content modal-appointment-pop">
            <h2 style={{ marginBottom:16, textAlign:'center' }}>Review Activity</h2>
            {selectedActivity && (
              <div style={{textAlign:'center'}}>
                <p><strong>Activity:</strong> {selectedActivity.activity_name}</p>
                <p><strong>USN:</strong> {selectedActivity.student_usn}</p>
                <div style={{marginBottom:16}}>
                  <label>Status:</label>
                  <select
                    value={reviewData.status}
                    onChange={(e) => setReviewData({ ...reviewData, status: e.target.value })}
                    style={{padding:'0.4rem',marginLeft:9,borderRadius:6}}
                  >
                    <option value="">Select Status</option>
                    <option value="Approved">Approve</option>
                    <option value="Rejected">Reject</option>
                  </select>
                </div>
                {reviewData.status === "Approved" && (
                  <div style={{marginBottom:16}}>
                    <label>Percentage:</label>
                    <input
                      type="number"
                      value={reviewData.percentage}
                      onChange={(e) => setReviewData({ ...reviewData, percentage: e.target.value })}
                      style={{padding:'0.4rem',marginLeft:9,borderRadius:6}}
                    />
                  </div>
                )}
                {reviewData.status === "Rejected" && (
                  <div style={{marginBottom:16}}>
                    <label>Rejection Reason:</label>
                    <textarea
                      value={reviewData.rejection_reason}
                      onChange={(e) => setReviewData({ ...reviewData, rejection_reason: e.target.value })}
                      rows={3} style={{borderRadius:6,width:'90%',marginTop:4,padding:8}}
                    />
                  </div>
                )}
                <div className="redesigned-modal-actions">
                  <button onClick={handleReview} className="modal-approve">Submit Review</button>
                  <button onClick={closeModal} className="modal-cancel">Cancel</button>
                </div>
              </div>
            )}
          </div>
        </Modal>
      </div>
    </div>
  );
};
export default ActivitiesApproval;