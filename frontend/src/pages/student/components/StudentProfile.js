import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import '../../../assets/css/StudentProfile.css';
import { API_BASE_URL } from '../../../api';
import { FaSignOutAlt, FaPen, FaTimes, FaCamera, FaTrash, FaUser } from 'react-icons/fa';

const StudentProfile = () => {
  const { student_usn } = useParams();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [photoUploading, setPhotoUploading] = useState(false);
  const photoInputRef = useRef(null);
  const [formData, setFormData] = useState({
    student_name: '',
    student_phoneno: '',
    semester: '',
    gender: '',
    blood_group: '',
    date_of_birth: '',
    parent_guardian_contact: '',
    mother_contact: '',
    father_contact: '',
    linkedin: ''
  });
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetch(`${API_BASE_URL}/student/${student_usn}/myprofile`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Profile not found');
        }
        return response.json();
      })
      .then((data) => {
        setProfile(data);
        setFormData({
          student_name: data.student_name || '',
          student_phoneno: data.student_phoneno || '',
          semester: data.semester ?? '',
          gender: data.gender || '',
          blood_group: data.blood_group || '',
          date_of_birth: data.date_of_birth || '',
          parent_guardian_contact: data.parent_guardian_contact || '',
          mother_contact: data.mother_contact || '',
          father_contact: data.father_contact || '',
          linkedin: data.linkedin || ''
        });
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching profile:', error);
        setIsLoading(false);
      });
  }, [student_usn]);

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const allowed = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowed.includes(file.type)) {
      alert('Only JPG, JPEG, and PNG images are allowed.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must not exceed 5 MB.');
      return;
    }
    setPhotoUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/uploadphoto`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      setProfile(prev => ({ ...prev, profile_photo_url: data.profile_photo_url }));
    } catch (err) {
      alert(err.message);
    } finally {
      setPhotoUploading(false);
      if (photoInputRef.current) photoInputRef.current.value = '';
    }
  };

  const handlePhotoDelete = async () => {
    if (!window.confirm('Are you sure you want to delete your profile photo?')) return;
    try {
      const res = await fetch(`${API_BASE_URL}/student/${student_usn}/deletephoto`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Delete failed');
      setProfile(prev => ({ ...prev, profile_photo_url: null }));
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCreateProfile = () => {
    navigate(`/student/${student_usn}/createprofile`);
  };

  const handleEditProfile = () => {
    const payload = {
      student_name: formData.student_name?.trim() || null,
      student_phoneno: formData.student_phoneno?.trim() || null,
      semester: formData.semester === '' ? null : Number(formData.semester),
      gender: formData.gender?.trim() || null,
      blood_group: formData.blood_group?.trim() || null,
      date_of_birth: formData.date_of_birth?.trim() || null,
      parent_guardian_contact: formData.parent_guardian_contact?.trim() || null,
      mother_contact: formData.mother_contact?.trim() || null,
      father_contact: formData.father_contact?.trim() || null,
      linkedin: formData.linkedin?.trim() || null,
    };
    if (payload.date_of_birth === '') payload.date_of_birth = null;
    fetch(`${API_BASE_URL}/student/${student_usn}/editprofile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to update profile');
        }
        return response.json();
      })
      .then((data) => {
        setIsModalOpen(false);
        setProfile(prevProfile => ({
          ...prevProfile,
          student_name: formData.student_name,
          student_phoneno: formData.student_phoneno,
          semester: formData.semester === '' ? prevProfile.semester : Number(formData.semester),
          gender: formData.gender,
          blood_group: formData.blood_group,
          date_of_birth: formData.date_of_birth,
          parent_guardian_contact: formData.parent_guardian_contact,
          mother_contact: formData.mother_contact,
          father_contact: formData.father_contact,
          linkedin: formData.linkedin
        }));
      })
      .catch((error) => {
        console.error('Error updating profile:', error);
        alert('Failed to update profile. Please try again.');
      });
  };

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isModalOpen && profile) {
      document.body.classList.add('modal-open');
      setFormData({
        student_name: profile.student_name || '',
        student_phoneno: profile.student_phoneno || '',
        semester: profile.semester ?? '',
        gender: profile.gender || '',
        blood_group: profile.blood_group || '',
        date_of_birth: profile.date_of_birth || '',
        parent_guardian_contact: profile.parent_guardian_contact || '',
          mother_contact: profile.mother_contact || '',
          father_contact: profile.father_contact || '',
        linkedin: profile.linkedin || ''
      });
    } else {
      document.body.classList.remove('modal-open');
    }
    return () => document.body.classList.remove('modal-open');
  }, [isModalOpen, profile]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const renderLinkedIn = (linkedin) => {
    const empty = !linkedin || !String(linkedin).trim();
    if (empty) return <span className="sp-profile-empty">—</span>;
    const trimmed = String(linkedin).trim();
    const hasHttp = /^https?:\/\//i.test(trimmed);
    const hasLinkedIn = /linkedin\.com\/in\//i.test(trimmed);
    const url = hasHttp && hasLinkedIn
      ? trimmed.split('?')[0]
      : `https://linkedin.com/in/${trimmed.replace(/^.*linkedin\.com\/in\/?/i, '').replace(/^\/+/, '')}`;
    return (
      <a href={url} target="_blank" rel="noopener noreferrer" className="sp-profile-linkedin-btn">
        View
      </a>
    );
  };

  const show = (value) => (value != null && String(value).trim() !== '' ? String(value).trim() : null);
  const display = (value) => show(value) ?? '—';


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
          onClick={() => {
            console.log('Edit button clicked, current modal state:', isModalOpen);
            setIsModalOpen(true);
          }}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
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
            zIndex: 10
          }}
        >
          <FaPen style={{ fontSize: '1.2rem', color: '#030303' }} />
        </button>
      </div>
      
      {profile && profile.student_name ? (
        <div className="sp-profile-details-container">
          <div className="sp-profile-photo-section">
            <div className="sp-profile-photo-wrapper">
              {profile.profile_photo_url ? (
                <img src={profile.profile_photo_url} alt="Profile" className="sp-profile-photo" />
              ) : (
                <div className="sp-profile-photo-placeholder"><FaUser /></div>
              )}
              <label className="sp-profile-photo-upload-btn" title="Upload photo">
                <FaCamera />
                <input
                  ref={photoInputRef}
                  type="file"
                  accept=".jpg,.jpeg,.png"
                  onChange={handlePhotoUpload}
                  style={{ display: 'none' }}
                  disabled={photoUploading}
                />
              </label>
            </div>
            {profile.profile_photo_url && (
              <button className="sp-profile-photo-delete-btn" onClick={handlePhotoDelete} title="Delete photo">
                <FaTrash /> Remove Photo
              </button>
            )}
            {photoUploading && <span className="sp-profile-photo-loading">Uploading...</span>}
          </div>
          <div className="sp-profile-details">
            <div><span className="sp-profile-label">USN:</span> {display(profile.student_usn)}</div>
            <div><span className="sp-profile-label">Name:</span> {display(profile.student_name)}</div>
            <div><span className="sp-profile-label">Email:</span> {display(profile.student_email)}</div>
            <div><span className="sp-profile-label">Phone Number:</span> {display(profile.student_phoneno)}</div>
            <div><span className="sp-profile-label">Gender:</span> {display(profile.gender)}</div>
            <div><span className="sp-profile-label">Blood Group:</span> {display(profile.blood_group)}</div>
            <div><span className="sp-profile-label">Date of Birth:</span> {display(profile.date_of_birth)}</div>
            <div><span className="sp-profile-label">Guardian Contact:</span> {display(profile.parent_guardian_contact)}</div>
            <div><span className="sp-profile-label">Mother Contact:</span> {display(profile.mother_contact)}</div>
            <div><span className="sp-profile-label">Father Contact:</span> {display(profile.father_contact)}</div>
            <div><span className="sp-profile-label">Program:</span> {display(profile.student_program)}</div>
            <div><span className="sp-profile-label">Batch:</span> {display(profile.student_batch)}</div>
            <div><span className="sp-profile-label">Semester:</span> {display(profile.semester)}</div>
            <div><span className="sp-profile-label">Assigned Mentor:</span> {display(profile.assigned_mentor)}</div>
            <div><span className="sp-profile-label">LinkedIn:</span> {renderLinkedIn(profile.linkedin)}</div>
            <div className="sp-logout-button-container">
              <button
                className="sp-sidebar-logout-button"
                onClick={() => navigate("/logout", { state: { from: location.pathname } })}
              >
                <FaSignOutAlt />&nbsp;&nbsp;&nbsp;&nbsp;Logout
              </button>
            </div>
          </div>
          
        </div>
      ) : (
        <div><br/><br/>
          <p>No profile found.</p>
          <button className="sp-profile-create-button" onClick={handleCreateProfile}>Create Profile</button>
          <div className="sp-logout-button-container">
            <button
              className="sp-sidebar-logout-button"
              onClick={() => navigate("/logout", { state: { from: location.pathname } })}
            >
              <FaSignOutAlt />&nbsp;&nbsp;&nbsp;&nbsp;Logout
            </button>
          </div>
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
          {console.log('Rendering modal, isModalOpen:', isModalOpen)}
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
                <label htmlFor="student_name">Name:</label>
                <input
                  id="student_name"
                  type="text"
                  name="student_name"
                  value={formData.student_name}
                  onChange={handleInputChange}
                  placeholder="Enter your name"
                />
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="student_phoneno">Phone Number:</label>
                <input
                  id="student_phoneno"
                  type="text"
                  name="student_phoneno"
                  value={formData.student_phoneno}
                  onChange={handleInputChange}
                  placeholder="10-digit number"
                  maxLength="10"
                />
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="gender">Gender:</label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="semester">Semester:</label>
                <select
                  id="semester"
                  name="semester"
                  value={formData.semester}
                  onChange={handleInputChange}
                >
                  <option value="">Select Semester</option>
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                  <option value="4">4</option>
                  <option value="5">5</option>
                  <option value="6">6</option>
                  <option value="7">7</option>
                  <option value="8">8</option>
                </select>
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="blood_group">Blood Group:</label>
                <select
                  id="blood_group"
                  name="blood_group"
                  value={formData.blood_group}
                  onChange={handleInputChange}
                >
                  <option value="">Select Blood Group</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="date_of_birth">Date of Birth:</label>
                <input
                  id="date_of_birth"
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleInputChange}
                />
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="parent_guardian_contact">Guardian Contact:</label>
                <input
                  id="parent_guardian_contact"
                  type="text"
                  name="parent_guardian_contact"
                  value={formData.parent_guardian_contact}
                  onChange={handleInputChange}
                  placeholder="10-digit number"
                  maxLength="10"
                />
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="mother_contact">Mother Contact:</label>
                <input
                  id="mother_contact"
                  type="text"
                  name="mother_contact"
                  value={formData.mother_contact}
                  onChange={handleInputChange}
                  placeholder="10-digit number"
                  maxLength="10"
                />
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="father_contact">Father Contact:</label>
                <input
                  id="father_contact"
                  type="text"
                  name="father_contact"
                  value={formData.father_contact}
                  onChange={handleInputChange}
                  placeholder="10-digit number"
                  maxLength="10"
                />
              </div>
              <div className="sp-profile-form-group">
                <label htmlFor="linkedin">LinkedIn:</label>
                <input
                  id="linkedin"
                  type="url"
                  name="linkedin"
                  value={formData.linkedin}
                  onChange={handleInputChange}
                  placeholder="https://linkedin.com/in/yourprofile"
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

export default StudentProfile;