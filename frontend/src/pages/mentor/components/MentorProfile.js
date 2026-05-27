import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import '../../../assets/css/StudentProfile.css';
import { API_BASE_URL } from '../../../api';
import { FaSignOutAlt, FaPen, FaTimes } from 'react-icons/fa';

const Profile = () => {
  const { mentor_id } = useParams();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    mentor_name: '',
    mentor_department: '',
    mentor_phoneno: '',
    mentor_email: ''
  });
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetch(`${API_BASE_URL}/mentor/${mentor_id}/profile`)
      .then((response) => {
        if (!response.ok) throw new Error('Profile not found');
        return response.json();
      })
      .then((data) => {
        setProfile(data);
        setFormData({
          mentor_name: data.mentor_name || '',
          mentor_department: data.mentor_department || '',
          mentor_phoneno: data.mentor_phoneno || '',
          mentor_email: data.mentor_email || ''
        });
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching profile:', error);
        setIsLoading(false);
      });
  }, [mentor_id]);

  const handleEditProfile = () => {
    // Make PUT request to update profile
    fetch(`${API_BASE_URL}/mentor/${mentor_id}/editprofile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to update profile');
        }
        return response.json();
      })
      .then((data) => {
        setIsModalOpen(false);
        // Update the profile state with the new data
        setProfile(prevProfile => ({
          ...prevProfile,
          mentor_name: formData.mentor_name,
          mentor_department: formData.mentor_department,
          mentor_phoneno: formData.mentor_phoneno,
          mentor_email: formData.mentor_email
        }));
      })
      .catch((error) => {
        console.error('Error updating profile:', error);
        alert('Failed to update profile. Please try again.');
      });
  };

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isModalOpen) {
      document.body.classList.add('modal-open');
    } else {
      document.body.classList.remove('modal-open');
    }

    return () => {
      document.body.classList.remove('modal-open');
    };
  }, [isModalOpen]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  if (isLoading) {
    return <div className="sp-profile-loading">Loading...</div>;
  }

  return (
    <div className='sp-details-profile'>
      <div className="sp-profile-header">
        <h2 className="sp-profile-title">
          Profile
        </h2>
        <button 
          className="sp-profile-edit-button"
          onClick={() => setIsModalOpen(true)}
          style={{
            position: 'absolute',
            top: '15px',
            right: '15px',
            background: 'white',
            border: '2px solid #e2e8f0',
            borderRadius: '12px',
            padding: '0.75rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: '44px',
            minHeight: '44px',
            zIndex: 10,
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
        >
          <FaPen style={{ fontSize: '1.2rem', color: '#030303' }} />
        </button>
      </div>
      
      {profile && profile.mentor_name ? (
        <div className="sp-profile-details-container">
          <div className="sp-profile-details">
            <div><span className="sp-profile-label">ID:</span> {mentor_id}</div>
            <div><span className="sp-profile-label">Name:</span> {profile.mentor_name}</div>
            <div><span className="sp-profile-label">Email:</span> {profile.mentor_email}</div>
            <div><span className="sp-profile-label">Phone Number:</span> {profile.mentor_phoneno}</div>
            <div><span className="sp-profile-label">Department:</span> {profile.mentor_department}</div>
            <button
              className="sp-sidebar-logout-button"
              onClick={() => navigate("/logout", { state: { from: location.pathname } })}
            >
              <FaSignOutAlt />&nbsp;&nbsp;&nbsp;&nbsp;Logout
            </button><br/><br/><br/><br/>
          </div>
        </div>
      ) : (
        <div><br/><br/>
          <p>No profile found.</p>
          <button
            className="sp-sidebar-logout-button"
            onClick={() => navigate("/logout", { state: { from: location.pathname } })}
          >
            <FaSignOutAlt />&nbsp;&nbsp;&nbsp;&nbsp;Logout
          </button>
        </div>
      )}

      {/* Mobile-Optimized Edit Modal */}
      {isModalOpen && (
        <div 
          className="sp-profile-modal" 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 999999,
            width: '100vw',
            height: '100vh'
          }}
        >
          <div 
            className="sp-profile-modal-content"
            style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '20px',
              width: '90%',
              maxWidth: '500px',
              maxHeight: '90vh',
              overflowY: 'auto',
              position: 'relative',
              zIndex: 1000000
            }}
          >
            <div className="sp-profile-modal-header">
              <h3>Edit Profile</h3>
              <button 
                className="sp-profile-modal-close" 
                onClick={() => setIsModalOpen(false)}
                aria-label="Close modal"
              >
                <FaTimes />
              </button>
            </div>
            
            <div className="sp-profile-form">
              <div className="sp-profile-form-group">
                <label htmlFor="mentor_name">Name:</label>
                <input
                  id="mentor_name"
                  type="text"
                  name="mentor_name"
                  value={formData.mentor_name}
                  onChange={handleInputChange}
                  placeholder="Enter your name"
                />
              </div>
              
              <div className="sp-profile-form-group">
                <label htmlFor="mentor_email">Email:</label>
                <input
                  id="mentor_email"
                  type="email"
                  name="mentor_email"
                  value={formData.mentor_email}
                  onChange={handleInputChange}
                  placeholder="Enter your email"
                />
              </div>
              
              <div className="sp-profile-form-group">
                <label htmlFor="mentor_phoneno">Phone Number:</label>
                <input
                  id="mentor_phoneno"
                  type="tel"
                  name="mentor_phoneno"
                  value={formData.mentor_phoneno}
                  onChange={handleInputChange}
                  placeholder="Enter your phone number"
                />
              </div>
              
              <div className="sp-profile-form-group">
                <label htmlFor="mentor_department">Department:</label>
                <input
                  id="mentor_department"
                  type="text"
                  name="mentor_department"
                  value={formData.mentor_department}
                  onChange={handleInputChange}
                  placeholder="Enter your department"
                />
              </div>
              
              <div className="sp-profile-buttons-container">
                <button 
                  className="sp-profile-save-btn" 
                  onClick={handleEditProfile}
                >
                  Save Changes
                </button>
                <button 
                  className="sp-profile-cancel-btn" 
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
