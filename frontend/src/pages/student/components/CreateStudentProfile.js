import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import '../../../assets/css/CreateStudentProfile.css';
import { API_BASE_URL } from '../../../api';

const CreateStudentProfile = () => {
  const { student_usn } = useParams();
  const navigate = useNavigate();
  const [studentProfile, setStudentProfile] = useState({
    student_name: '',
    student_phoneno: '',
    student_program: '',
    student_batch: '',
    assigned_mentor: '',
    department: '',
    linkedin: '',
    gender: '',
    blood_group: '',
    date_of_birth: '',
    parent_guardian_contact: '',
    mother_contact: '',
    father_contact: '',
  });
  const [mentors, setMentors] = useState([]);
  const [filteredMentors, setFilteredMentors] = useState([]);
  const [uniqueDepartments, setUniqueDepartments] = useState([]);
  const [error, setError] = useState(null);

  const [startYear, setStartYear] = useState('');
  const [duration, setDuration] = useState('');

  useEffect(() => {
    fetch(`${API_BASE_URL}/mentors`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to fetch mentors: ${response.statusText}`);
        }
        return response.json();
      })
      .then((data) => {
        if (!Array.isArray(data)) {
          console.error('Mentors API did not return an array:', data);
          setError('Invalid response from server');
          return;
        }
        console.log(`Fetched ${data.length} mentors from API`);
        setMentors(data);
        // Extract unique departments: deduplicate by normalizing (trim + lowercase) so
        // "Forensic science" and "Forensic Science" appear only once
        const deptMap = new Map();
        (data.map((m) => m.mentor_department).filter(Boolean)).forEach((dept) => {
          const key = dept.trim().toLowerCase();
          if (!deptMap.has(key)) {
            deptMap.set(key, dept.trim());
          }
        });
        const departments = Array.from(deptMap.values()).sort();
        setUniqueDepartments(departments);
        console.log(`Found ${departments.length} unique departments:`, departments);
      })
      .catch((error) => {
        console.error('Error fetching mentors:', error);
        setError(error.message || 'Failed to load mentors. Please refresh the page.');
      });
  }, []);

  useEffect(() => {
    if (studentProfile.department) {
      // Case-insensitive and trim whitespace comparison to handle variations like "Forensic science" vs "Forensic Science"
      const selectedDept = studentProfile.department.trim().toLowerCase();
      const filtered = mentors.filter((mentor) => 
        mentor.mentor_department && 
        mentor.mentor_department.trim().toLowerCase() === selectedDept
      );
      console.log(`Filtering mentors for department "${studentProfile.department}":`, {
        selectedDept,
        totalMentors: mentors.length,
        filteredCount: filtered.length,
        filteredMentors: filtered.map(m => ({ id: m.mentor_id, name: m.mentor_name, dept: m.mentor_department }))
      });
      setFilteredMentors(filtered);
    } else {
      setFilteredMentors([]);
    }
  }, [studentProfile.department, mentors]);

  const startYearOptions = Array.from({ length: 15 }, (_, i) => new Date().getFullYear() - 10 + i);
  const durationOptions = Array.from({ length: 6 }, (_, i) => i + 2);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setStudentProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleBatchChange = (e) => {
    const { name, value } = e.target;
    if (name === 'startYear') {
      setStartYear(value);
      if (duration) {
        setStudentProfile((prev) => ({
          ...prev,
          student_batch: `${value}-${parseInt(value) + parseInt(duration)}`,
        }));
      }
    } else if (name === 'duration') {
      setDuration(value);
      if (startYear) {
        setStudentProfile((prev) => ({
          ...prev,
          student_batch: `${startYear}-${parseInt(startYear) + parseInt(value)}`,
        }));
      }
    }
  };

  const handleLinkedinChange = (e) => {
    let inputValue = e.target.value.trim(); // Remove leading/trailing spaces
  
    // Remove any unnecessary tracking parameters if the user pastes a full LinkedIn URL
    inputValue = inputValue.split('?')[0]; // Removes everything after '?'
  
    // Extract the username if the user pasted a LinkedIn URL
    let username = inputValue.replace(/^(https?:\/\/)?(www\.)?linkedin\.com\/in\//, '');
  
    // Update state: Display username in input field, but store full LinkedIn URL
    setStudentProfile((prev) => ({
      ...prev,
      linkedin: `https://linkedin.com/in/${username}`, // Store complete LinkedIn URL
    }));
  };
  
  
  

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);

    // Validate all required fields
    if (!studentProfile.student_name || !studentProfile.student_name.trim()) {
      setError('Please enter your name.');
      return;
    }

    if (!studentProfile.student_phoneno || !studentProfile.student_phoneno.trim()) {
      setError('Please enter your phone number.');
      return;
    }

    if (!studentProfile.mother_contact || !studentProfile.mother_contact.trim()) {
      setError('Please enter mother contact number.');
      return;
    }

    if (!studentProfile.father_contact || !studentProfile.father_contact.trim()) {
      setError('Please enter father contact number.');
      return;
    }

    if (!studentProfile.student_program) {
      setError('Please select a program.');
      return;
    }

    if (!studentProfile.department) {
      setError('Please select a department.');
      return;
    }

    if (!studentProfile.student_batch || !startYear || !duration) {
      setError('Please select both start year and duration for batch.');
      return;
    }

    if (!studentProfile.assigned_mentor) {
      setError('Please select an assigned mentor.');
      return;
    }

    if (!studentProfile.linkedin || !studentProfile.linkedin.trim() || studentProfile.linkedin === 'https://linkedin.com/in/') {
      setError('Please enter your LinkedIn username.');
      return;
    }

    const concatenatedProgram = `${studentProfile.student_program} in ${studentProfile.department}`;
    const profileData = {
      ...studentProfile,
      student_program: concatenatedProgram,
      gender: studentProfile.gender || null,
      blood_group: studentProfile.blood_group || null,
      date_of_birth: studentProfile.date_of_birth || null,
      parent_guardian_contact: studentProfile.parent_guardian_contact || null,
      mother_contact: studentProfile.mother_contact || null,
      father_contact: studentProfile.father_contact || null,
    };

    fetch(`${API_BASE_URL}/student/${student_usn}/createprofile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          alert(data.message);
          navigate(`/student/${student_usn}/profile`);
        } else if (data.detail) {
          setError(data.detail);
        }
      })
      .catch((error) => setError(error.message || 'Failed to create profile. Please try again.'));
  };

  return (
    <div className="student-profile-form-container">
      <h2 className="student-profile-form-heading">Create Student Profile</h2>
      <h3 className="student-profile-form-heading1">Once the profile is submitted, it cannot be edited.</h3>
      {error && <p className="student-profile-form-error">{error}</p>}
      
      <form onSubmit={handleSubmit} className="student-profile-form">
        <div className="student-profile-form-group">
          <label>Name <span style={{ color: 'red' }}>*</span></label>
          <input 
            type="text" 
            name="student_name" 
            value={studentProfile.student_name} 
            onChange={handleChange} 
            placeholder="Enter full name" 
            required
          />
        </div>

        <div className="student-profile-form-group">
          <label>Phone Number <span style={{ color: 'red' }}>*</span></label>
          <input 
            type="text" 
            name="student_phoneno" 
            value={studentProfile.student_phoneno} 
            onChange={handleChange} 
            placeholder="Enter phone number" 
            maxLength="10" 
            required
          />
        </div>

        <div className="student-profile-form-group">
          <label>Mother Contact <span style={{ color: 'red' }}>*</span></label>
          <input
            type="text"
            name="mother_contact"
            value={studentProfile.mother_contact}
            onChange={handleChange}
            placeholder="Enter 10-digit number"
            maxLength="10"
            required
          />
        </div>

        <div className="student-profile-form-group">
          <label>Father Contact <span style={{ color: 'red' }}>*</span></label>
          <input
            type="text"
            name="father_contact"
            value={studentProfile.father_contact}
            onChange={handleChange}
            placeholder="Enter 10-digit number"
            maxLength="10"
            required
          />
        </div>

        <div className="student-profile-form-group">
          <label>Gender</label>
          <select 
            name="gender" 
            value={studentProfile.gender} 
            onChange={handleChange}
          >
            <option value="">Select Gender</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
            <option value="Prefer not to say">Prefer not to say</option>
          </select>
        </div>

        <div className="student-profile-form-group">
          <label>Blood Group</label>
          <select 
            name="blood_group" 
            value={studentProfile.blood_group} 
            onChange={handleChange}
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

        <div className="student-profile-form-group">
          <label>Date of Birth</label>
          <input 
            type="date" 
            name="date_of_birth" 
            value={studentProfile.date_of_birth} 
            onChange={handleChange} 
            placeholder="DD/MM/YYYY"
          />
        </div>

        <div className="student-profile-form-group">
          <label>Guardian Contact Number</label>
          <input 
            type="text" 
            name="parent_guardian_contact" 
            value={studentProfile.parent_guardian_contact} 
            onChange={handleChange} 
            placeholder="Enter 10-digit number" 
            maxLength="10"
          />
        </div>

        <div className="student-profile-form-group">
          <label>Program <span style={{ color: 'red' }}>*</span></label>
          <select 
            name="student_program" 
            value={studentProfile.student_program} 
            onChange={handleChange}
            required
          >
            <option value="">Select Program</option>
            <option value="BSc.">Bachelors of Science</option>
            <option value="MSc.">Masters of Science</option>
          </select>
        </div>

        {studentProfile.student_program && (
          <div className="student-profile-form-group">
            <label>Department <span style={{ color: 'red' }}>*</span></label>
            <select 
              name="department" 
              value={studentProfile.department} 
              onChange={handleChange}
              required
            >
              <option value="">Select Department</option>
              {uniqueDepartments.map((dept, index) => (
                <option key={index} value={dept}>{dept}</option>
              ))}
            </select>
          </div>
        )}

        <div className="student-profile-form-group">
          <label>Batch <span style={{ color: 'red' }}>*</span></label>
          <div className="batch-dropdowns">
            <select 
              name="startYear" 
              value={startYear} 
              onChange={handleBatchChange}
              required
            >
              <option value="">Start Year</option>
              {startYearOptions.map((year) => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
            <span> - </span>
            <select 
              name="duration" 
              value={duration} 
              onChange={handleBatchChange}
              required
            >
              <option value="">Duration (years)</option>
              {durationOptions.map((years) => (
                <option key={years} value={years}>{years} Years</option>
              ))}
            </select>
          </div>
          {studentProfile.student_batch && <p>Selected Batch: <strong>{studentProfile.student_batch}</strong></p>}
        </div>

        <div className="student-profile-form-group">
          <label>Assigned Mentor <span style={{ color: 'red' }}>*</span></label>
          <select 
            name="assigned_mentor" 
            value={studentProfile.assigned_mentor} 
            onChange={handleChange}
            required
          >
            <option value="">Select Mentor</option>
            {filteredMentors.map((mentor) => (
              <option key={mentor.mentor_id} value={mentor.mentor_id}>{mentor.mentor_name}</option>
            ))}
          </select>
        </div>

        <div className="student-profile-form-group">
          <label>LinkedIn <span style={{ color: 'red' }}>*</span></label>
          <input
            type="text"
            name="linkedin"
            value={studentProfile.linkedin.replace('https://linkedin.com/in/', '')} // Show only username
            onChange={handleLinkedinChange}
            placeholder="Enter LinkedIn username"
            required
          />
        </div>
        <button type="submit" className="student-profile-form-submit-btn">Create Profile</button><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
      </form>
    </div>
  );
};

export default CreateStudentProfile;
