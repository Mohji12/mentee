import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import '../../../assets/css/Appointments.css';
import "../../../assets/css/ActivityTracking.css";
import { API_BASE_URL } from "../../../api";

const ActivityTracking = () => {
  const { mentor_id } = useParams();
  const [activities, setActivities] = useState([]);
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [formData, setFormData] = useState({
    remarks: "",
    completed_in: "",
    benefitted: "false",
    proof: "",
  });
  const [searchUSN, setSearchUSN] = useState("");
  const [showPopup, setShowPopup] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [studentOptions, setStudentOptions] = useState([]); // Store USN-Name options
  const [assignedStudents, setAssignedStudents] = useState([]); // For request activity modal
  const [requestFormData, setRequestFormData] = useState({
    student_usn: "",
    activities: "",
    duration_type: "Short Term",
    deadline: "",
    remarks: ""
  });
  const [requestStatus, setRequestStatus] = useState("");

  const fetchActivities = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const headers = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/activities`, { headers });
      if (!response.ok) {
        throw new Error("Failed to fetch activities");
      }
      const data = await response.json();
      setActivities(data);
      setFilteredActivities(data);
      const uniqueStudents = {};
      data.forEach(activity => {
        uniqueStudents[activity.student_usn] = activity.student_name;
      });
      setStudentOptions(Object.entries(uniqueStudents).map(([usn, name]) => ({
        value: usn,
        label: `${usn} - ${name}`,
      })));
    } catch (error) {
      console.error(error.message);
    }
  };

  useEffect(() => {
    const fetchAssignedStudents = async () => {
      try {
        const token = sessionStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/assigned_students`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setAssignedStudents(data);
        }
      } catch (error) {
        console.error("Error fetching assigned students:", error);
      }
    };

    fetchActivities();
    fetchAssignedStudents();
  }, [mentor_id]);

  // Refetch when tab/window gains focus so new mentee requests appear
  useEffect(() => {
    const onFocus = () => fetchActivities();
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [mentor_id]);

  // Auto-refresh every 25s so mentee-requested activities appear without manual refresh
  useEffect(() => {
    const intervalId = setInterval(fetchActivities, 25000);
    return () => clearInterval(intervalId);
  }, [mentor_id]);

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchUSN(value);
    if (value === "") {
      setFilteredActivities(activities);
    } else {
      const filtered = activities.filter((activity) =>
        `${activity.student_usn} - ${activity.student_name}`.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredActivities(filtered);
    }
  };

  const handleUpdateClick = (activity) => {
    setSelectedActivity(activity);
    setFormData({
      remarks: activity.remarks || "",
      completed_in: activity.completed_in || "",
      benefitted: activity.benefitted ? "true" : "false",
      proof: activity.proof || "",
    });
    setShowPopup(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === "completed_in" && parseInt(value, 10) < 0) {
      return;
    }
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    const urlRegex = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i;
    if (formData.proof && !urlRegex.test(formData.proof)) {
      alert("Please enter a valid URL for the proof field.");
      return;
    }
    if (!selectedActivity || !selectedActivity.activity_id) {
      alert("Activity ID is missing");
      return;
    }
    const updatedFormData = {
      remarks: formData.remarks.trim() || null,
      completed_in: formData.completed_in !== "" && formData.completed_in != null
        ? parseInt(formData.completed_in, 10)
        : null,
      benefitted: formData.benefitted === "true",
      proof: formData.proof && formData.proof.trim() !== "" ? formData.proof.trim() : null,
    };
    try {
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/${selectedActivity.activity_id}/update_activity`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(updatedFormData),
        }
      );
      if (!response.ok) {
        throw new Error("Failed to update activity");
      }
      alert("Activity updated successfully!");
      setShowPopup(false);
      setFormData({ remarks: "", completed_in: "", benefitted: "false", proof: "" });
      const refreshedResponse = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/activities`);
      const refreshedData = await refreshedResponse.json();
      setActivities(refreshedData);
      setFilteredActivities(refreshedData);
      // Update student options after refresh
      const uniqueStudents = {};
      refreshedData.forEach(activity => {
        uniqueStudents[activity.student_usn] = activity.student_name;
      });
      setStudentOptions(Object.entries(uniqueStudents).map(([usn, name]) => ({
        value: usn, label: `${usn} - ${name}`,
      })));
    } catch (error) {
      console.error("Error updating activity:", error.message);
    }
  };

  const handleRequestInputChange = (e) => {
    const { name, value } = e.target;
    setRequestFormData((prev) => ({ ...prev, [name]: value }));
    setRequestStatus("");
  };

  const handleRequestSubmit = async (e) => {
    e.preventDefault();
    
    if (!requestFormData.student_usn || !requestFormData.activities.trim()) {
      setRequestStatus("Please fill in all required fields.");
      return;
    }

    try {
      const token = sessionStorage.getItem('access_token');
      const payload = {
        student_usn: requestFormData.student_usn,
        activities: requestFormData.activities.trim(),
        duration_type: requestFormData.duration_type,
        remarks: requestFormData.remarks.trim() || null,
        deadline: requestFormData.deadline || null
      };

      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/request-activity`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to request activity");
      }

      setRequestStatus("Activity requested successfully!");
      setRequestFormData({
        student_usn: "",
        activities: "",
        duration_type: "Short Term",
        deadline: "",
        remarks: ""
      });

      // Refresh activities list
      setTimeout(async () => {
        const refreshedResponse = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/activities`);
        const refreshedData = await refreshedResponse.json();
        setActivities(refreshedData);
        setFilteredActivities(refreshedData);
        setShowRequestModal(false);
        setRequestStatus("");
      }, 1500);
    } catch (error) {
      console.error("Error requesting activity:", error);
      setRequestStatus(`Error: ${error.message}`);
    }
  };

  return (
    <div className="meeting-portal-container">
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:24,flexWrap:'wrap',gap:'1rem'}}>
        <div className="meeting-portal-title" style={{fontWeight:600,fontSize:'2rem',letterSpacing:'0.01em',marginBottom:0}}>
          Activity Tracking
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={() => fetchActivities()}
            className="verify-btn redesigned-verify-btn"
            style={{ background: '#2196F3', color: 'white', padding: '0.75rem 1.5rem', fontSize: '1rem', position: 'relative', zIndex: 1 }}
            title="Refresh to see new requests from mentees"
          >
            Refresh
          </button>
          <button
            onClick={() => setShowRequestModal(true)}
            className="verify-btn redesigned-verify-btn"
            style={{background:'#4CAF50',color:'white',padding:'0.75rem 1.5rem',fontSize:'1rem',position:'relative',zIndex:1}}
          >
            + Request New Activity
          </button>
        </div>
      </div>
      <div className="appointments-card-bg">
        <div className="activity-tracking__search" style={{marginBottom:'1.5rem'}}>
          <select
            value={searchUSN}
            onChange={handleSearchChange}
            className="activity-tracking__search-dropdown"
            style={{borderRadius:8,padding:'0.6rem',fontSize:'1rem',maxWidth:290}}
          >
            <option value="">Select USN - Name</option>
            {studentOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
        <div className="activity-table-scroll-wrapper">
          <table className="meeting-table redesigned-meeting-table activity-tracking__table">
            <thead>
              <tr>
                <th>Activity ID</th>
                <th>USN - Name</th>
                <th>Activity</th>
                <th>Term Type</th>
                <th>Start Date</th>
                <th>Deadline</th>
                <th>Comp. In</th>
                <th>Status</th>
                <th>Percentage</th>
                <th>Update</th>
              </tr>
            </thead>
            <tbody>
              {filteredActivities.map((activity,idx) => (
                <tr key={activity.activity_id} className={idx%2===0 ? 'alt-row':''}>
                  <td>{activity.activity_id}</td>
                  <td>
                    <div>
                      <strong>{activity.student_usn}</strong><br/>
                      <span style={{fontSize:'0.95em',color:'#767676'}}>{activity.student_name}</span>
                    </div>
                  </td>
                  <td className="activity-col-wrap">
                    <div>
                      {activity.requested_by === 'mentee' && (
                        <span className="mentee-request-badge" style={{
                          display: 'inline-block',
                          background: '#E3F2FD',
                          color: '#1565C0',
                          fontSize: '0.75rem',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          marginBottom: '4px',
                          fontWeight: 600
                        }}>
                          Requested by mentee
                        </span>
                      )}
                      <span>{activity.activities}</span>
                    </div>
                  </td>
                  <td>{activity.duration_type}</td>
                  <td>{new Date(activity.start_date).toLocaleDateString()}</td>
                  <td>{new Date(activity.deadline).toLocaleDateString()}</td>
                  <td>{activity.completed_in}</td>
                  <td>{activity.status}</td>
                  <td>{activity.percentage || "N/A"}</td>
                  <td>
                    <button
                      className="verify-btn redesigned-verify-btn"
                      style={{background:'#29A7E0'}}
                      onClick={() => handleUpdateClick(activity)}
                      title='Update activity details'
                    >
                      Update
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {showPopup && (
          <div className="modal-overlay">
            <div className="modal-content modal-appointment-pop" style={{maxWidth:430}}>
              <form className="activity-tracking__form" onSubmit={handleUpdateSubmit} style={{margin:0}}>
                <h3 className="activity-tracking__popup-title" style={{fontWeight:600,marginBottom:18}}>Update Activity</h3>
                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:10}}>Remarks:
                  <textarea
                    name="remarks"
                    value={formData.remarks}
                    onChange={handleInputChange}
                    onInput={(e) => {
                      e.target.style.height = "auto";
                      e.target.style.height = `${e.target.scrollHeight}px`;
                    }}
                    className="activity-tracking__textarea"
                    style={{minHeight: "40px", maxHeight: "160px", marginBottom:10, borderRadius:7, padding:8}}
                  />
                </label>
                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:10}}>
                  Completed In:
                  <input
                    type="number"
                    name="completed_in"
                    value={formData.completed_in}
                    onChange={handleInputChange}
                    className="activity-tracking__input"
                    style={{borderRadius:7,padding:8}}
                  />
                </label>
                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:10}}>
                  Benefitted:
                  <select
                    name="benefitted"
                    value={formData.benefitted}
                    onChange={handleInputChange}
                    className="activity-tracking__select"
                    style={{borderRadius:7,padding:7,minWidth:100,marginLeft:9}}
                  >
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                  </select>
                </label>
                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:15}}>
                  Proof (URL):
                  <input
                    type="url"
                    name="proof"
                    value={formData.proof}
                    onChange={handleInputChange}
                    className="activity-tracking__input"
                    style={{borderRadius:7,padding:8}}
                  />
                </label>
                <div className="redesigned-modal-actions">
                  <button type="submit" className="modal-approve" style={{minWidth:120}}>Update</button>
                  <button type="button" className="modal-cancel" style={{minWidth:120}} onClick={() => setShowPopup(false)}>Cancel</button>
                </div>
              </form>
            </div>
          </div>
        )}
        {showRequestModal && (
          <div className="modal-overlay">
            <div className="modal-content modal-appointment-pop" style={{maxWidth:500}}>
              <form className="activity-tracking__form" onSubmit={handleRequestSubmit} style={{margin:0}}>
                <h3 className="activity-tracking__popup-title" style={{fontWeight:600,marginBottom:18}}>Request New Activity</h3>
                
                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:10}}>
                  Student: <span style={{color:'red'}}>*</span>
                  <select
                    name="student_usn"
                    value={requestFormData.student_usn}
                    onChange={handleRequestInputChange}
                    className="activity-tracking__select"
                    style={{borderRadius:7,padding:8,width:'100%',marginTop:5}}
                    required
                  >
                    <option value="">Select a student</option>
                    {assignedStudents.map(student => (
                      <option key={student.student_usn} value={student.student_usn}>
                        {student.student_usn} - {student.student_name}
                      </option>
                    ))}
                  </select>
                </label>

                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:10}}>
                  Activity Description: <span style={{color:'red'}}>*</span>
                  <textarea
                    name="activities"
                    value={requestFormData.activities}
                    onChange={handleRequestInputChange}
                    onInput={(e) => {
                      e.target.style.height = "auto";
                      e.target.style.height = `${e.target.scrollHeight}px`;
                    }}
                    className="activity-tracking__textarea"
                    style={{minHeight: "80px", maxHeight: "200px", marginTop:5, borderRadius:7, padding:8}}
                    placeholder="Describe the activity you want to assign..."
                    required
                  />
                </label>

                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:10}}>
                  Duration Type: <span style={{color:'red'}}>*</span>
                  <select
                    name="duration_type"
                    value={requestFormData.duration_type}
                    onChange={handleRequestInputChange}
                    className="activity-tracking__select"
                    style={{borderRadius:7,padding:8,width:'100%',marginTop:5}}
                    required
                  >
                    <option value="Short Term">Short Term (90 days)</option>
                    <option value="Mid Term">Mid Term (182 days)</option>
                    <option value="Long Term">Long Term (365 days)</option>
                  </select>
                </label>

                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:10}}>
                  Deadline (Optional - will be auto-calculated if not provided):
                  <input
                    type="date"
                    name="deadline"
                    value={requestFormData.deadline}
                    onChange={handleRequestInputChange}
                    className="activity-tracking__input"
                    style={{borderRadius:7,padding:8,width:'100%',marginTop:5}}
                  />
                </label>

                <label style={{width:'100%',display:'block',textAlign:'left',marginBottom:15}}>
                  Remarks/Instructions (Optional):
                  <textarea
                    name="remarks"
                    value={requestFormData.remarks}
                    onChange={handleRequestInputChange}
                    onInput={(e) => {
                      e.target.style.height = "auto";
                      e.target.style.height = `${e.target.scrollHeight}px`;
                    }}
                    className="activity-tracking__textarea"
                    style={{minHeight: "60px", maxHeight: "150px", marginTop:5, borderRadius:7, padding:8}}
                    placeholder="Any additional instructions or remarks for the student..."
                  />
                </label>

                {requestStatus && (
                  <div style={{
                    padding: '10px',
                    marginBottom: '15px',
                    borderRadius: '7px',
                    backgroundColor: requestStatus.includes('Error') ? '#ffebee' : '#e8f5e9',
                    color: requestStatus.includes('Error') ? '#c62828' : '#2e7d32',
                    fontSize: '0.9rem'
                  }}>
                    {requestStatus}
                  </div>
                )}

                <div className="redesigned-modal-actions">
                  <button type="submit" className="modal-approve" style={{minWidth:120}} disabled={requestStatus.includes('successfully')}>
                    Request Activity
                  </button>
                  <button 
                    type="button" 
                    className="modal-cancel" 
                    style={{minWidth:120}} 
                    onClick={() => {
                      setShowRequestModal(false);
                      setRequestFormData({
                        student_usn: "",
                        activities: "",
                        duration_type: "Short Term",
                        deadline: "",
                        remarks: ""
                      });
                      setRequestStatus("");
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
export default ActivityTracking;