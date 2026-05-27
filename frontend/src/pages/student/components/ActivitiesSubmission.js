import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { API_BASE_URL } from "../../../api";
import "../../../assets/css/ActivitiesSubmission.css";

const ActivitiesSubmissions = () => {
  const { student_usn } = useParams();
  const [activities, setActivities] = useState([]);
  const [selectedActivity, setSelectedActivity] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [submissions, setSubmissions] = useState([]);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all');

  useEffect(() => {
    // Fetch logged activities (assigned by mentor in Activity Tracking)
    axios
      .get(`${API_BASE_URL}/student/${student_usn}/logged_activities`)
      .then((response) => {
        const list = response.data?.activities;
        setActivities(Array.isArray(list) ? list : []);
      })
      .catch((error) => {
        console.error("Error fetching activities:", error);
        setActivities([]);
      });

    // Fetch activity submissions (returns [] when none)
    axios
      .get(`${API_BASE_URL}/student/${student_usn}/activities/submissions`)
      .then((response) => {
        setSubmissions(Array.isArray(response.data) ? response.data : []);
      })
      .catch((error) => {
        console.error("Error fetching submissions:", error);
        setSubmissions([]);
      });
  }, [student_usn]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedActivity || !file) {
      setMessage("Please select an activity and upload a file.");
      return;
    }
  
    setIsUploading(true);
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE_URL}/student/${student_usn}/activities/${selectedActivity}/upload_proof`,
        formData,
        {
          headers: { 
            "Authorization": `Bearer ${token}`
            // Don't set Content-Type for FormData - axios will set it automatically with boundary
          },
        }
      );
      setMessage(response.data.message);
  
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      console.error('Error uploading file:', error);
      const errorMessage = error.response?.data?.detail || error.message || "Error uploading file. Please try again.";
      setMessage(`Error: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };
  
  const handleViewProof = async (activityId) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/student/${student_usn}/activities/${activityId}/proof`
      );
      window.open(response.data.proof_url, "_blank");
    } catch (error) {
      console.error("Error fetching proof URL:", error);
      alert("Error fetching proof file.");
    }
  };

  const getStatusColor = (status) => {
    switch(status.toLowerCase()) {
      case 'approved': return '#4CAF50';
      case 'rejected': return '#f44336';
      case 'pending': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getStatusIcon = (status) => {
    switch(status.toLowerCase()) {
      case 'approved': return '✅';
      case 'rejected': return '❌';
      case 'pending': return '⏳';
      default: return '📋';
    }
  };

  const getFilteredSubmissions = () => {
    if (selectedFilter === 'all') return submissions;
    return submissions.filter(submission => submission.status.toLowerCase() === selectedFilter);
  };

  const filteredSubmissions = getFilteredSubmissions();

  return (
    <div className="submissions-page">
      <div className="submissions-header">
        <div className="header-content">
          <h1 className="page-title">Activity Submissions</h1>
          <p className="page-subtitle">Track your submitted proofs and their review status</p>
        </div>
        <div className="student-usn">
          <span className="usn-text">{student_usn}</span>
        </div>

      </div>

      <div className="submissions-filters">
        <button 
          className={`filter-btn ${selectedFilter === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('all')}
        >
          All Submissions ({submissions.length})
        </button>
        <button 
          className={`filter-btn ${selectedFilter === 'pending' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('pending')}
        >
          Pending ({submissions.filter(s => s.status.toLowerCase() === 'pending').length})
        </button>
        <button 
          className={`filter-btn ${selectedFilter === 'approved' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('approved')}
        >
          Approved ({submissions.filter(s => s.status.toLowerCase() === 'approved').length})
        </button>
        <button 
          className={`filter-btn ${selectedFilter === 'rejected' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('rejected')}
        >
          Rejected ({submissions.filter(s => s.status.toLowerCase() === 'rejected').length})
        </button>
      </div>

      <div className="upload-section">
        {activities.length === 0 ? (
          <div className="no-activities-message" style={{ padding: '1rem', background: '#f5f5f5', borderRadius: 8, marginBottom: 8 }}>
            <strong>No activities assigned yet.</strong> Your mentor will assign activities from the <strong>Activity Tracking</strong> page. Once assigned, you can upload proofs here.
          </div>
        ) : null}
        <button 
          className="upload-button" 
          onClick={() => setIsPopupOpen(true)}
        >
          <span className="upload-icon">📤</span>
          Upload New Proof
        </button>
      </div>

      <div className="submissions-grid">
        {filteredSubmissions.length > 0 ? (
          filteredSubmissions.map((submission, index) => (
            <div key={submission.submission_id} className="submission-card">
              <div className="card-header">
                <div className="submission-id">
                  <span className="id-label">Submission #{submission.submission_id}</span>
                </div>
                <div className="submission-status">
                  <span 
                    className="status-badge" 
                    style={{ backgroundColor: getStatusColor(submission.status) }}
                  >
                    <span className="status-icon">{getStatusIcon(submission.status)}</span>
                    {submission.status}
                  </span>
                </div>
              </div>
              
              <div className="card-content">
                <div className="submission-details">
                  <div className="detail-item">
                    <span className="detail-label">Activity:</span>
                    <span className="detail-value">
                      {submission.activity_name || submission.activity_id}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Activity ID:</span>
                    <span className="detail-value">{submission.activity_id}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Submitted:</span>
                    <span className="detail-value">
                      {new Date(submission.submitted_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Completion Time:</span>
                    <span className="detail-value">
                      {submission.completed_in ? `${submission.completed_in} days` : 'Not specified'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="card-actions">
                <button
                  onClick={() => handleViewProof(submission.activity_id)}
                  className="view-proof-btn"
                >
                  <span className="btn-icon">👁️</span>
                  View Proof
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="no-submissions">
            <div className="no-submissions-icon">📝</div>
            <h3>No submissions found</h3>
            <p>
              {selectedFilter === 'all' 
                ? "You haven't submitted any activity proofs yet." 
                : `No ${selectedFilter} submissions found.`
              }
            </p>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {isPopupOpen && (
        <div className="upload-modal-overlay">
          <div className="upload-modal">
            <div className="modal-header">
              <h3>Upload Activity Proof</h3>
              <button 
                className="close-modal-btn" 
                onClick={() => setIsPopupOpen(false)}
              >
                &times;
              </button>
            </div>
            
            <form className="upload-form" onSubmit={handleSubmit}>
              <div className="form-field">
                <label>Select Activity:</label>
                <select
                  value={selectedActivity}
                  onChange={(e) => setSelectedActivity(e.target.value)}
                  disabled={isUploading}
                  required
                >
                  <option value="">-- Select an Activity --</option>
                  {activities.length === 0 ? (
                    <option value="" disabled>No activities assigned yet</option>
                  ) : (
                    activities.map((activity) => {
                      const activityName = (activity.activities && activity.activities.split(":")[0].trim()) || activity.activity_id;
                      return (
                        <option key={activity.activity_id} value={activity.activity_id}>
                          {activity.activity_id} - {activityName}
                        </option>
                      );
                    })
                  )}
                </select>
                {activities.length === 0 && (
                  <p className="form-hint" style={{ marginTop: 8, color: '#666', fontSize: '0.9rem' }}>
                    Your mentor will assign activities from the Activity Tracking page. Once assigned, they will appear here.
                  </p>
                )}
              </div>
              
              <div className="form-field">
                <label>Upload Proof File:</label>
                <input
                  type="file"
                  onChange={handleFileChange}
                  disabled={isUploading}
                  required
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                />
              </div>

              {message && (
                <div className={`message ${message.includes("Error") ? "error" : "success"}`}>
                  {message}
                </div>
              )}

              <div className="modal-actions">
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={isUploading}
                >
                  {isUploading ? "Uploading..." : "Upload Proof"}
                </button>
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setIsPopupOpen(false)}
                  disabled={isUploading}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivitiesSubmissions;
