import React, { useState, useRef } from "react";
import { useParams } from "react-router-dom"; 
import '../../../assets/css/Psychometric.css';
import { API_BASE_URL } from "../../../api";

const PsychometricForm = () => {
  const { student_usn } = useParams(); 
  const [formData, setFormData] = useState({
    present_address: "",
    permanent_address: "",
    educational_qualifications: "",
    subjects_strength: "",
    subjects_weakness: "",
    previous_work_experience: "",
    father_name: "",
    father_mobile_no: "",
    father_education: "",
    father_employment: "",
    mother_name: "",
    mother_mobile_no: "",
    mother_education: "",
    mother_employment: "",
    siblings_details: "",
    professional_dream: "",
    professional_fear: "",
    happiness_sources: "",
    expectations: "",
    goal_achieving_opportunities: "",
    participate_in_skill_programs: false,
    interested_skill_programs: "",
    external_factors_affecting_growth: "",
    primary_stressors: "",
    biggest_distractions: "",
    strongest_skills: "",
    areas_of_low_confidence: "",
    hobbies_interests: "",
    consent_given: true,
  });

  const [status, setStatus] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submitButtonRef = useRef(null);

  const totalSteps = 8;

  const pageFields = {
    1: ["present_address", "permanent_address"],
    2: ["educational_qualifications", "subjects_strength", "subjects_weakness", "previous_work_experience"],
    3: ["father_name", "father_mobile_no", "father_education", "father_employment", "mother_name", "mother_mobile_no", "mother_education", "mother_employment", "siblings_details"],
    4: ["professional_dream", "professional_fear", "happiness_sources"],
    5: ["expectations", "goal_achieving_opportunities", "participate_in_skill_programs", "interested_skill_programs"],
    6: ["external_factors_affecting_growth","primary_stressors", "biggest_distractions"],
    7: ["strongest_skills","areas_of_low_confidence","hobbies_interests"],
    8: ["consent_given"]
  };

  const validatePageFields = () => {
    const fieldsToValidate = pageFields[currentPage];
    return fieldsToValidate.every((field) => {
      return formData[field] !== "" && formData[field] !== null && formData[field] !== undefined;
    });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevFormData) => {
      const updatedFormData = {
        ...prevFormData,
        [name]: type === "checkbox" ? checked : value,
      };

      if (validatePageFields()) {
        setStatus("");
      }
      return updatedFormData;
    });
  };

  const handleNext = () => {
    if (validatePageFields()) {
      if (currentPage < totalSteps) {
        setCurrentPage(currentPage + 1);
      }
    } else {
      setStatus("Please fill all required fields on this page.");
    }
  };

  const handlePrev = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submit triggered - Current page:', currentPage, 'Total steps:', totalSteps, 'Is submitting:', isSubmitting);
    
    // Only allow submission on the last page and if not already submitting
    if (currentPage !== totalSteps || isSubmitting) {
      console.log('Form submission blocked - not on last page or already submitting');
      return;
    }
    
    // Validate all fields before submission
    if (!validatePageFields()) {
      setStatus("Please fill all required fields on this page.");
      return;
    }
    
    setIsSubmitting(true);
    setStatus("Submitting form...");
    
    fetch(`${API_BASE_URL}/student/${student_usn}/psychometric-form`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          setStatus("Form submitted successfully.");
        } else {
          throw new Error(data.detail || "Submission failed.");
        }
      })
      .catch((error) => {
        if (error.message === "Psychometric form already submitted for this semester") {
          setStatus("You have already submitted the psychometric form for this semester.");
        } else {
          setStatus(`Error: ${error.message}`);
        }
      })
      .finally(() => {
        setIsSubmitting(false);
      });
  };

  const handleKeyDown = (e) => {
    // Prevent form submission on Enter key press unless on the last page
    if (e.key === 'Enter' && currentPage !== totalSteps) {
      e.preventDefault();
      handleNext();
    }
  };

  const handleSubmitClick = () => {
    console.log('Submit button clicked');
    // Trigger form submission
    const form = document.querySelector('form');
    if (form) {
      form.requestSubmit();
    }
  };

  return (
    <div className="swot-form-container">
      {/* Header Section */}
      <div className="form-header">
        <h1 className="form-title">SWOT Analysis Form</h1>
        <p className="form-subtitle">Complete this form to generate your personalized SWOT analysis</p>
      </div>



      {/* Form Container */}
      <div className="form-card">
        <form onSubmit={handleSubmit} onKeyDown={handleKeyDown}>
          {/* Personal Information Section */}
          {currentPage === 1 && (
            <div className="form-section">
              <h3 className="section-title">Personal Information</h3>
              <div className="form-field">
                <label>Present Address</label>
                <input
                  type="text"
                  name="present_address"
                  value={formData.present_address}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Enter your current address"
                />
              </div>
              <div className="form-field">
                <label>Permanent Address</label>
                <input
                  type="text"
                  name="permanent_address"
                  value={formData.permanent_address}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Enter your permanent address"
                />
              </div>
            </div>
          )}

          {/* Educational Details Section */}
          {currentPage === 2 && (
            <div className="form-section">
              <h3 className="section-title">Educational Background</h3>
              <div className="form-field">
                <label>Educational Qualifications</label>
                <input
                  type="text"
                  name="educational_qualifications"
                  value={formData.educational_qualifications}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="List your highest qualifications"
                />
              </div>
              <div className="form-field">
                <label>Strengths in Subjects</label>
                <input
                  type="text"
                  name="subjects_strength"
                  value={formData.subjects_strength}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Which subjects do you excel in? List out"
                />
              </div>
              <div className="form-field">
                <label>Weaknesses in Subjects</label>
                <input
                  type="text"
                  name="subjects_weakness"
                  value={formData.subjects_weakness}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Which subjects do you struggle with? List out"
                />
              </div>
              <div className="form-field">
                <label>Previous Work Experience</label>
                <input
                  type="text"
                  name="previous_work_experience"
                  value={formData.previous_work_experience}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Describe any work experience you have, if applicable"
                />
              </div>
            </div>
          )}

          {/* Family Information Section */}
          {currentPage === 3 && (
            <div className="form-section">
              <h3 className="section-title">Family Background</h3>
              <div className="form-field">
                <label>Father's Name</label>
                <input
                  type="text"
                  name="father_name"
                  value={formData.father_name}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Father's Name"
                />
              </div>
              <div className="form-field">
                <label>Father's Mobile Number</label>
                <input
                  type="tel"
                  name="father_mobile_no"
                  value={formData.father_mobile_no}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Father's Mobile No."
                  maxLength="10"
                />
              </div>
              <div className="form-field">
                <label>Father's Education</label>
                <input
                  type="text"
                  name="father_education"
                  value={formData.father_education}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="What is your father's highest educational qualification?"
                />
              </div>
              <div className="form-field">
                <label>Father's Employment</label>
                <input
                  type="text"
                  name="father_employment"
                  value={formData.father_employment}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="What is your father's occupation?"
                />
              </div>
              <div className="form-field">
                <label>Mother's Name</label>
                <input
                  type="text"
                  name="mother_name"
                  value={formData.mother_name}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Mother's Name"
                />
              </div>
              <div className="form-field">
                <label>Mother's Mobile Number</label>
                <input
                  type="tel"
                  name="mother_mobile_no"
                  value={formData.mother_mobile_no}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Mother's Mobile No."
                  maxLength="10"
                />
              </div>
              <div className="form-field">
                <label>Mother's Education</label>
                <input
                  type="text"
                  name="mother_education"
                  value={formData.mother_education}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="What is your mother's highest educational qualification?"
                />
              </div>
              <div className="form-field">
                <label>Mother's Employment</label>
                <input
                  type="text"
                  name="mother_employment"
                  value={formData.mother_employment}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="What is your mother's occupation?"
                />
              </div>
              <div className="form-field">
                <label>Sibling's Details</label>
                <input
                  type="text"
                  name="siblings_details"
                  value={formData.siblings_details}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Do you have siblings? If yes, mention their occupation or educational status"
                />
              </div>
            </div>
          )}

          {/* Goals and Interests Section */}
          {currentPage === 4 && (
            <div className="form-section">
              <h3 className="section-title">Professional Aspirations</h3>
              <div className="form-field">
                <label>What is your professional dream?</label>
                <input
                  type="text"
                  name="professional_dream"
                  value={formData.professional_dream}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Describe your career aspirations"
                />
              </div>
              <div className="form-field">
                <label>What is your biggest fear?</label>
                <input
                  type="text"
                  name="professional_fear"
                  value={formData.professional_fear}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="What challenges or fears do you think might affect your career goals?"
                />
              </div>
              <div className="form-field">
                <label>What is your happiness in your personal/professional life?</label>
                <input
                  type="text"
                  name="happiness_sources"
                  value={formData.happiness_sources}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="What activities, achievements, or experience make you happy?"
                />
              </div>
            </div>
          )}

          {/* Opportunities and Expectations Section */}
          {currentPage === 5 && (
            <div className="form-section">
              <h3 className="section-title">Opportunities and Expectations</h3>
              <div className="form-field">
                <label>What are your expectations when joining JAIN (Deemed-to-be University)?</label>
                <input
                  type="text"
                  name="expectations"
                  value={formData.expectations}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="What do you hope to achieve academically and personally during your time at the university?"
                />
              </div>
              <div className="form-field">
                <label>What opportunities do you think will help you achieve your goals?</label>
                <input
                  type="text"
                  name="goal_achieving_opportunities"
                  value={formData.goal_achieving_opportunities}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="List the resources, programs, or experiences you believe will benefit you"
                />
              </div>
              <div className="form-field checkbox-field">
                <label>
                  <input
                    type="checkbox"
                    name="participate_in_skill_programs"
                    checked={formData.participate_in_skill_programs}
                    onChange={handleChange}
                    className="checkbox-input"
                  />
                  Would you like to participate in additional skills-building programs?
                </label>
              </div>
              {formData.participate_in_skill_programs && (
                <div className="form-field">
                  <label>What kind of skill-building programs are you interested in?</label>
                  <input
                    type="text"
                    name="interested_skill_programs"
                    value={formData.interested_skill_programs}
                    onChange={handleChange}
                    required
                    className="form-input"
                    placeholder="List out the interested skill building programs"
                  />
                </div>
              )}
            </div>
          )}

          {/* Challenges Section */}
          {currentPage === 6 && (
            <div className="form-section">
              <h3 className="section-title">Challenges</h3>
              <div className="form-field">
                <label>What external factors that you think might affect your academic growth?</label>
                <input
                  type="text"
                  name="external_factors_affecting_growth"
                  value={formData.external_factors_affecting_growth}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="For eg. family responsibilities, financial issues, etc."
                />
              </div>
              <div className="form-field">
                <label>What are your primary stressors?</label>
                <input
                  type="text"
                  name="primary_stressors"
                  value={formData.primary_stressors}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="List situations or tasks that cause you the most stress"
                />
              </div>
              <div className="form-field">
                <label>What do you consider the biggest distractions in your life right now?</label>
                <input
                  type="text"
                  name="biggest_distractions"
                  value={formData.biggest_distractions}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="For eg, social media, peer pressure, etc."
                />
              </div>
            </div>
          )}

          {/* Skills and Interests Section */}
          {currentPage === 7 && (
            <div className="form-section">
              <h3 className="section-title">Skills and Interests</h3>
              <div className="form-field">
                <label>What according to you, are your strongest skills?</label>
                <input
                  type="text"
                  name="strongest_skills"
                  value={formData.strongest_skills}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Mention any skills you feel particularly confident in"
                />
              </div>
              <div className="form-field">
                <label>What areas do you feel less confident?</label>
                <input
                  type="text"
                  name="areas_of_low_confidence"
                  value={formData.areas_of_low_confidence}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="Describe skills or areas where you think you need improvement"
                />
              </div>
              <div className="form-field">
                <label>What are your hobbies or extracurricular interests?</label>
                <input
                  type="text"
                  name="hobbies_interests"
                  value={formData.hobbies_interests}
                  onChange={handleChange}
                  required
                  className="form-input"
                  placeholder="List any activities or interests you enjoy outside academics"
                />
              </div>
            </div>
          )}

          {/* Consent Section */}
          {currentPage === 8 && (
            <div className="form-section">
              <h3 className="section-title">Consent</h3>
              <div className="form-field checkbox-field">
                <label>
                  <input
                    type="checkbox"
                    name="consent_given"
                    checked={formData.consent_given}
                    onChange={handleChange}
                    className="checkbox-input"
                    required
                  />
                  <span className="consent-text">
                    I hereby consent to the collection and analysis of my personal, academic, and professional data for the purpose of conducting a SWOT (Strengths, Weaknesses, Opportunities, and Threats) analysis. I understand that this analysis is intended to support my academic and personal growth. I acknowledge that this data may also be shared with designated university officials/ my mentor/ mentorship coordinator for analysis and academic purposes. I understand that all collected data will be kept confidential, securely stored, and used solely for educational and institutional purposes. Additionally, I recognize that all data provided is the proprietary property of JAIN (Deemed-to-be University) and will be handled in accordance with the university's data protection and privacy policies.
                  </span>
                </label>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="form-navigation">
            {currentPage > 1 && (
              <button type="button" onClick={handlePrev} className="nav-button prev-button">
                Previous
              </button>
            )}
            {currentPage < totalSteps ? (
              <button type="button" onClick={handleNext} className="nav-button next-button">
                Next →
              </button>
            ) : (
              <button 
                type="button" 
                ref={submitButtonRef}
                onClick={handleSubmitClick}
                className="submit-button" 
                disabled={isSubmitting}
              >
                {isSubmitting ? "Submitting..." : "Submit"}
              </button>
            )}
          </div>

          {/* Status Message */}
          {status && (
            <div className={`status-message ${status.includes('successfully') ? 'success' : 'error'}`}>
              {status}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default PsychometricForm;
