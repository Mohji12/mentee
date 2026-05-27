import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import '../../../assets/css/AdminProfile.css'
import { API_BASE_URL } from '../../../api';
import { Link } from 'react-router-dom';
import { FaSignOutAlt } from 'react-icons/fa';  // Importing icons from react-icons


const AdminProfile = () => {
  const { admin_id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch profile details
    fetch(`${API_BASE_URL}/admin/${admin_id}/profile/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Profile not found');
        }
        return response.json();
      })
      .then((data) => {
        setProfile(data);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching profile:', error);
        setIsLoading(false);
      });
  }, [admin_id]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="admin-profile__content">
      <h2 className="admin-profile__title">Profile</h2>
      {profile && profile.admin_name ? (
        <div className="admin-profile__details">
          <p><strong>ID:</strong> {admin_id}</p>
          <p><strong>Name:</strong> {profile.admin_name}</p>
          <p><strong>Department:</strong> {profile.admin_department}</p>
          <p><strong>Email ID:</strong> {profile.admin_email}</p>
          <p><strong>Phone Number:</strong> {profile.admin_phoneno}</p>
          <p><strong>Designation:</strong> {profile.admin_department}</p>
          <p><strong>Campus:</strong> {profile.admin_campus}</p>
          <button 
            className="admin-profile-sidebar-logout-button"
            onClick={() => navigate("/logout", { state: { from: location.pathname } })}
          >
            <FaSignOutAlt />&nbsp;&nbsp;&nbsp;&nbsp;Logout
          </button>
        </div>
      ) : (
        <div className="admin-profile__no-profile">
          <p>No profile found.</p>
        </div>
      )}
    </div>
  );
};

export default AdminProfile;
