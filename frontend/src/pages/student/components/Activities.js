import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import '../../../assets/css/Activities.css';
import { API_BASE_URL } from '../../../api';

const ActivitiesPage = () => {
  const { student_usn } = useParams();
  const [activities, setActivities] = useState(null);
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [requestFormData, setRequestFormData] = useState({
    activities: "",
    duration_type: "Short Term",
    deadline: "",
    remarks: ""
  });
  const [requestStatus, setRequestStatus] = useState("");

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/student/${student_usn}/activities`);
        if (response.status === 404) {
          setActivities([]);
          return;
        }
        if (!response.ok) {
          throw new Error('Failed to fetch activities');
        }
        const data = await response.json();
        setActivities(data);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchActivities();
  }, [student_usn]);

  const handleRequestInputChange = (e) => {
    const { name, value } = e.target;
    setRequestFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRequestSubmit = async (e) => {
    e.preventDefault();
    setRequestStatus("");

    try {
      const token = sessionStorage.getItem('access_token');
      const payload = {
        activities: requestFormData.activities.trim(),
        duration_type: requestFormData.duration_type,
        remarks: requestFormData.remarks.trim() || null,
      };

      // Add deadline if provided
      if (requestFormData.deadline) {
        payload.deadline = new Date(requestFormData.deadline).toISOString();
      }

      const response = await fetch(
        `${API_BASE_URL}/student/${student_usn}/request-activity`,
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

      setRequestStatus("Activity requested successfully! Your mentor will be notified.");
      setRequestFormData({
        activities: "",
        duration_type: "Short Term",
        deadline: "",
        remarks: ""
      });

      // Refresh activities list; new request is stored and will show on mentor's Activity Tracking
      setTimeout(async () => {
        const refreshedResponse = await fetch(`${API_BASE_URL}/student/${student_usn}/activities`);
        if (refreshedResponse.ok) {
          const refreshedData = await refreshedResponse.json();
          setActivities(refreshedData);
        }
        setShowRequestModal(false);
        setRequestStatus("");
      }, 1500);
    } catch (error) {
      console.error("Error requesting activity:", error);
      setRequestStatus(`Error: ${error.message}`);
    }
  };

  if (error) {
    return (
      <div className="activities-error">
        <div className="error-icon">⚠️</div>
        <h2>Oops! Something went wrong</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()} className="retry-btn">
          Try Again
        </button>
      </div>
    );
  }

  if (activities === null) {
    return (
      <div className="activities-loading">
        <div className="loading-spinner"></div>
        <p>Loading your activities...</p>
      </div>
    );
  }

  // Handle different data structures and ensure exactly 3 activities (1 short, 1 mid, 1 long term)
  const getActivityCards = () => {
    const allActivities = [];
    
    // Check if activities is an array
    if (Array.isArray(activities)) {
      activities.forEach((activity, index) => {
        if (index >= 3) return; // Limit to 3 activities (1 per type)
        
        if (activity && typeof activity === 'object') {
          // If it's an object, extract the activity name
          const activityName = activity.activities || activity.activity || activity.name || `Activity ${index + 1}`;
          const type = activity.duration_type || 'short';
          const category = type === 'short' ? 'Short Term' : type === 'mid' ? 'Mid Term' : 'Long Term';
          
          allActivities.push({
            name: activityName,
            type: type,
            category: category,
            originalData: activity
          });
        } else if (typeof activity === 'string') {
          // If it's a string, treat it as a short term activity
          allActivities.push({
            name: activity,
            type: 'short',
            category: 'Short Term',
            originalData: activity
          });
        }
      });
    } else if (typeof activities === 'object' && activities !== null) {
      // Handle object structure with keys like short_term, mid_term, etc.
      // Only show 1 activity per type (short_term, mid_term, long_term)
      const activitySlots = [
        { key: 'short_term', type: 'short', category: 'Short Term' },
        { key: 'mid_term', type: 'mid', category: 'Mid Term' },
        { key: 'long_term', type: 'long', category: 'Long Term' }
      ];

      activitySlots.forEach((slot) => {
        const activityData = activities[slot.key];
        if (activityData) {
          if (typeof activityData === 'string') {
            allActivities.push({
              name: activityData,
              type: slot.type,
              category: slot.category,
              originalData: activityData
            });
          } else if (typeof activityData === 'object' && activityData.activities) {
            allActivities.push({
              name: activityData.activities,
              type: slot.type,
              category: slot.category,
              originalData: activityData
            });
          }
        } else {
          // Create placeholder for empty slots
          allActivities.push({
            name: `No ${slot.category} Activity Assigned`,
            type: slot.type,
            category: slot.category,
            originalData: null,
            isPlaceholder: true
          });
        }
      });
    }

    return allActivities;
  };

  const activityCards = getActivityCards();
  
  if (activityCards.length === 0) {
    return (
      <div className="activities-empty">
        <div className="empty-icon">📚</div>
        <h2>No Activities Found</h2>
        <p>You don't have any activities assigned yet. Check back later!</p>
      </div>
    );
  }
  
  const filteredActivities = selectedFilter === 'all' 
    ? activityCards 
    : activityCards.filter(activity => activity.type === selectedFilter);

  const getStatusColor = (type) => {
    switch(type) {
      case 'short': return '#4CAF50';
      case 'mid': return '#FF9800';
      case 'long': return '#2196F3';
      default: return '#9E9E9E';
    }
  };

  return (
    <div className="activities-page">
      <div className="activities-header">
        <div className="header-content">
          <h1 className="page-title">My Activities</h1>
          <p className="page-subtitle">Track your learning journey and progress</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => setShowRequestModal(true)}
            className="filter-btn"
            style={{
              background: '#4CAF50',
              color: 'white',
              padding: '0.75rem 1.5rem',
              fontSize: '1rem',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '500',
              transition: 'background 0.3s'
            }}
            onMouseOver={(e) => e.target.style.background = '#45a049'}
            onMouseOut={(e) => e.target.style.background = '#4CAF50'}
          >
            + Request New Activity
          </button>
          <div className="student-usn">
            <span className="usn-text">{student_usn}</span>
          </div>
        </div>
      </div>

      <div className="activities-filters">
        <button 
          className={`filter-btn ${selectedFilter === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('all')}
        >
          All Activities ({activityCards.length})
        </button>
        <button 
          className={`filter-btn ${selectedFilter === 'short' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('short')}
        >
          Short Term ({activityCards.filter(a => a.type === 'short').length})
        </button>
        <button 
          className={`filter-btn ${selectedFilter === 'mid' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('mid')}
        >
          Mid Term ({activityCards.filter(a => a.type === 'mid').length})
        </button>
        <button 
          className={`filter-btn ${selectedFilter === 'long' ? 'active' : ''}`}
          onClick={() => setSelectedFilter('long')}
        >
          Long Term ({activityCards.filter(a => a.type === 'long').length})
        </button>
      </div>

      <div className="activities-grid">
        {filteredActivities.map((activity, index) => (
          <div 
            key={`activity-${index}`}
            className={`activity-card ${activity.isPlaceholder ? 'placeholder' : ''}`} 
            style={{ borderLeftColor: getStatusColor(activity.type) }}
          >
            <div className="card-header">
              <div className="activity-type">
                <span className="type-label">{activity.category}</span>
              </div>
              <div className="activity-status">
                <span className="status-dot" style={{ backgroundColor: getStatusColor(activity.type) }}></span>
                {activity.isPlaceholder ? 'Not Assigned' : 'Active'}
              </div>
            </div>
            
            <div className="card-content">
              <h3 className="activity-title">{activity.name}</h3>
              {!activity.isPlaceholder && (
                <div className="activity-meta">
                  <div className="meta-item">
                    <span className="meta-icon">📅</span>
                    <span className="meta-text">Duration: {activity.type === 'short' ? '3 months' : activity.type === 'mid' ? '6 months' : '1 year'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-icon">🎯</span>
                    <span className="meta-text">Focus: {activity.type === 'short' ? 'Quick Wins' : activity.type === 'mid' ? 'Skill Building' : 'Long-term Growth'}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredActivities.length === 0 && (
        <div className="no-activities-filtered">
          <div className="no-activities-icon">🔍</div>
          <h3>No activities found</h3>
          <p>Try selecting a different filter or check back later.</p>
        </div>
      )}

      {/* Request Activity Modal */}
      {showRequestModal && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }} onClick={() => {
          if (!requestStatus.includes('successfully')) {
            setShowRequestModal(false);
            setRequestFormData({
              activities: "",
              duration_type: "Short Term",
              deadline: "",
              remarks: ""
            });
            setRequestStatus("");
          }
        }}>
          <div className="modal-content" style={{
            background: 'white',
            borderRadius: '12px',
            padding: '2rem',
            maxWidth: '500px',
            width: '90%',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }} onClick={(e) => e.stopPropagation()}>
            <form onSubmit={handleRequestSubmit} style={{ margin: 0 }}>
              <h3 style={{ fontWeight: 600, marginBottom: 18, fontSize: '1.5rem' }}>Request New Activity</h3>
              
              <label style={{ width: '100%', display: 'block', textAlign: 'left', marginBottom: 10 }}>
                Activity Description: <span style={{ color: 'red' }}>*</span>
                <textarea
                  name="activities"
                  value={requestFormData.activities}
                  onChange={handleRequestInputChange}
                  onInput={(e) => {
                    e.target.style.height = "auto";
                    e.target.style.height = `${e.target.scrollHeight}px`;
                  }}
                  style={{
                    minHeight: "80px",
                    maxHeight: "200px",
                    marginTop: 5,
                    borderRadius: 7,
                    padding: 8,
                    width: '100%',
                    border: '1px solid #ddd',
                    fontFamily: 'inherit',
                    fontSize: '1rem'
                  }}
                  placeholder="Describe the activity you want to request..."
                  required
                />
              </label>

              <label style={{ width: '100%', display: 'block', textAlign: 'left', marginBottom: 10 }}>
                Duration Type: <span style={{ color: 'red' }}>*</span>
                <select
                  name="duration_type"
                  value={requestFormData.duration_type}
                  onChange={handleRequestInputChange}
                  style={{
                    borderRadius: 7,
                    padding: 8,
                    width: '100%',
                    marginTop: 5,
                    border: '1px solid #ddd',
                    fontFamily: 'inherit',
                    fontSize: '1rem'
                  }}
                  required
                >
                  <option value="Short Term">Short Term (90 days)</option>
                  <option value="Mid Term">Mid Term (182 days)</option>
                  <option value="Long Term">Long Term (365 days)</option>
                </select>
              </label>

              <label style={{ width: '100%', display: 'block', textAlign: 'left', marginBottom: 10 }}>
                Deadline (Optional - will be auto-calculated if not provided):
                <input
                  type="date"
                  name="deadline"
                  value={requestFormData.deadline}
                  onChange={handleRequestInputChange}
                  style={{
                    borderRadius: 7,
                    padding: 8,
                    width: '100%',
                    marginTop: 5,
                    border: '1px solid #ddd',
                    fontFamily: 'inherit',
                    fontSize: '1rem'
                  }}
                />
              </label>

              <label style={{ width: '100%', display: 'block', textAlign: 'left', marginBottom: 15 }}>
                Notes for Mentor (Optional):
                <textarea
                  name="remarks"
                  value={requestFormData.remarks}
                  onChange={handleRequestInputChange}
                  onInput={(e) => {
                    e.target.style.height = "auto";
                    e.target.style.height = `${e.target.scrollHeight}px`;
                  }}
                  style={{
                    minHeight: "60px",
                    maxHeight: "150px",
                    marginTop: 5,
                    borderRadius: 7,
                    padding: 8,
                    width: '100%',
                    border: '1px solid #ddd',
                    fontFamily: 'inherit',
                    fontSize: '1rem'
                  }}
                  placeholder="Any additional notes or context for your mentor..."
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

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => {
                    if (!requestStatus.includes('successfully')) {
                      setShowRequestModal(false);
                      setRequestFormData({
                        activities: "",
                        duration_type: "Short Term",
                        deadline: "",
                        remarks: ""
                      });
                      setRequestStatus("");
                    }
                  }}
                  style={{
                    padding: '0.75rem 1.5rem',
                    borderRadius: '7px',
                    border: '1px solid #ddd',
                    background: 'white',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    minWidth: 120
                  }}
                  disabled={requestStatus.includes('successfully')}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={requestStatus.includes('successfully')}
                  style={{
                    padding: '0.75rem 1.5rem',
                    borderRadius: '7px',
                    border: 'none',
                    background: requestStatus.includes('successfully') ? '#ccc' : '#4CAF50',
                    color: 'white',
                    cursor: requestStatus.includes('successfully') ? 'not-allowed' : 'pointer',
                    fontSize: '1rem',
                    minWidth: 120,
                    fontWeight: '500'
                  }}
                >
                  Request Activity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivitiesPage;
