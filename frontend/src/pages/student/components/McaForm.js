import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/mca.css';
import Modal from 'react-modal';
import '../../../assets/css/Loader.css';
import { triggerPdfDownload } from '../../../utils/triggerPdfDownload';

Modal.setAppElement('#root');

const McaForm = () => {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [status, setStatus] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isObservationModalOpen, setIsObservationModalOpen] = useState(false);
  const [isDownloadModalOpen, setIsDownloadModalOpen] = useState(false);
  const [calculationStatus, setCalculationStatus] = useState('');
  const [observationStatus, setObservationStatus] = useState('');
  const [downloadStatus, setDownloadStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [lockStatus, setLockStatus] = useState(null);
  const [isFormLocked, setIsFormLocked] = useState(false);
  const navigate = useNavigate();

  // Page configuration - Updated for 45 questions total
  // Page 1: 8 questions, Page 2: 8 questions, Page 3: 8 questions
  // Page 4: 8 questions, Page 5: 8 questions, Page 6: 5 questions
  const pageFields = {
    1: ["listens_carefully", "discouraged_by_criticism", "builds_trust", "adapts_to_styles", "shares_with_classmates", "sets_expectations", "aligns_expectations", "wants_mentor_to_adapt"],
    2: ["expects_improvement_feedback", "understands_diff_impacts", "goal_setting_with_mentor", "sees_mentor_as_role_model", "aligns_with_industry_expectations", "polite_repetition_reminder", "estimates_mentor_knowledge", "considers_industry_exposure"],
    3: ["self_assess_abilities", "understands_worklife_balance", "discusses_knowledge_strategies", "avoids_using_mentor_network", "discusses_goal_strategies", "improves_communication", "stays_self_motivated", "discusses_career_options"],
    4: ["frequent_meetings", "extra_effort_due_to_exposure", "prefers_active_sessions", "seeks_networking_support", "wants_showcasing_contributions", "handles_background_differences", "expects_independence", "wants_feedback_grouped"],
    5: ["avoids_bias_prejudice", "expects_motivation_support", "works_with_diverse_mentors", "likes_success_stories", "expects_networking_help", "encouraged_for_projects", "expects_career_exposure", "supports_experimentation"],
    6: ["supports_industry_interaction", "respects_contrary_views", "encourages_market_analysis", "showcases_contributions", "accepts_open_criticism"]
  };

  useEffect(() => {
    const fetchQuestionsAndLockStatus = async () => {
      try {
        setLoading(true);
        const usn = sessionStorage.getItem('userId');
        if (!usn) {
          setStatus('USN not found, please log in again.');
          setLoading(false);
          return;
        }
        
        // Fetch both questions and lock status
        const [questionsResponse, lockStatusResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/student/${usn}/mca-questions`),
          fetch(`${API_BASE_URL}/student/${usn}/mca-lock-status`)
        ]);
        
        if (!questionsResponse.ok) {
          throw new Error(`HTTP error! status: ${questionsResponse.status}`);
        }
        
        const questionsData = await questionsResponse.json();
        const lockStatusData = await lockStatusResponse.json();
        
        setQuestions(questionsData);
        setLockStatus(lockStatusData);
        setIsFormLocked(lockStatusData.is_locked);
        
        // Ensure data is an array
        if (Array.isArray(questionsData)) {
          const initialAnswers = questionsData.reduce((acc, q) => {
            acc[q.alias] = '';
            return acc;
          }, {});
          setAnswers(initialAnswers);
        } else {
          console.error('Expected array of questions, got:', questionsData);
          setStatus('Error loading questions. Please refresh the page.');
        }
      } catch (error) {
        console.error('Error fetching questions or lock status:', error);
        setStatus('Error loading form data. Please refresh the page.');
      } finally {
        setLoading(false);
      }
    };

    fetchQuestionsAndLockStatus();
  }, []);

  const validatePageFields = () => {
    const fieldsToValidate = pageFields[currentPage];
    return fieldsToValidate.every((field) => {
      const value = answers[field];
      return value !== "" && value !== null && value !== undefined;
    });
  };

  const handleChange = (alias, value) => {
    setAnswers((prevAnswers) => {
      return {
        ...prevAnswers,
        [alias]: value,
      };
    });
  };

  const handleNext = () => {
    if (validatePageFields()) {
      if (currentPage < 6) {
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('');

    const unansweredQuestions = questions.filter(q => !answers[q.alias]);
    if (unansweredQuestions.length > 0) {
      setStatus('Please answer all questions before submitting.');
      return;
    }

    try {
      const usn = sessionStorage.getItem('userId');
      if (!usn) {
        setStatus('USN not found, please log in again.');
        return;
      }

      // Create payload with internal field names as keys (not the full question text)
      const payload = {};
      console.log('Questions data:', questions);
      console.log('Answers data:', answers);
      
      questions.forEach(q => {
        if (answers[q.alias]) {
          // Use the internal_name from the question data, or fallback to alias
          const fieldName = q.internal_name || q.alias;
          payload[fieldName] = parseInt(answers[q.alias]);
          console.log(`Field: ${q.alias} -> ${fieldName}, Value: ${answers[q.alias]} -> ${parseInt(answers[q.alias])}`);
        } else {
          console.log(`Missing answer for: ${q.alias}`);
        }
      });

      console.log('Final payload:', payload);
      console.log('Payload keys:', Object.keys(payload));
      console.log('Payload values:', Object.values(payload));

      const response = await fetch(`${API_BASE_URL}/student/${usn}/mca-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      
      if (response.ok) {
        setStatus('MCA assignment submitted successfully!');
        setIsModalOpen(true);
      } else {
        let errorMessage = 'Form submission failed.';
        
        if (response.status === 423) {
          // Lock status error
          errorMessage = data.detail || 'MCA form is currently locked. Please try again later.';
        } else if (response.status === 400) {
          // Already submitted error
          errorMessage = data.detail || 'Form is already submitted.';
        } else {
          // Other errors
          errorMessage = typeof data.detail === 'string' ? data.detail : 
                        (data.detail && typeof data.detail === 'object' ? JSON.stringify(data.detail) : 
                        'Form submission failed.');
        }
        
        setStatus(errorMessage);
      }
    } catch (error) {
      setStatus('Form is Already Submitted.');
      console.error('Submission error:', error);
    }
  };

  const handleCalculateCompetencies = async () => {
    setIsCalculating(true);
    setCalculationStatus('');
    try {
      const usn = sessionStorage.getItem('userId');
      if (!usn) {
        setCalculationStatus('USN not found, please log in again.');
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/student/${usn}/calculate_competencies?usn=${usn}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setIsModalOpen(false);
        setIsObservationModalOpen(true);
      } else {
        const data = await response.json();
        const errorMessage = typeof data.detail === 'string' ? data.detail : 
                           (data.detail && typeof data.detail === 'object' ? JSON.stringify(data.detail) : 
                           'Failed to calculate competencies.');
        setCalculationStatus(errorMessage);
      }
    } catch (error) {
      console.error('Error calculating competencies:', error);
      setCalculationStatus('Failed to calculate competencies.');
    } finally {
      setIsCalculating(false);
    }
  };

  const handleGenerateObservation = async () => {
    setIsGenerating(true);
    setObservationStatus('Generating observations... This may take a few minutes.');
    try {
      const usn = sessionStorage.getItem('userId');
      if (!usn) {
        setObservationStatus('USN not found, please log in again.');
        setIsGenerating(false);
        return;
      }
      
      const token = sessionStorage.getItem('access_token');
      if (!token) {
        setObservationStatus('Authentication token not found. Please log in again.');
        setIsGenerating(false);
        return;
      }

      // Create AbortController for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout

      const response = await fetch(`${API_BASE_URL}/generate_observation_recommendations?student_usn=${usn}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
          } else {
            const errorText = await response.text();
            errorMessage = errorText || errorMessage;
          }
        } catch (e) {
          console.error('Error parsing error response:', e);
        }
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      
      const successMessage = typeof data.message === 'string' ? data.message : 
                           'Observations generated successfully!';
      setObservationStatus(successMessage);
      
      // Show download modal instead of redirecting
      setTimeout(() => {
        setIsObservationModalOpen(false);
        setIsDownloadModalOpen(true);
      }, 2000);
    } catch (error) {
      if (error.name === 'AbortError') {
        setObservationStatus('Request timed out. The generation is taking longer than expected. Please try again.');
      } else {
        const errorMessage = error.message || 'Failed to generate observations.';
        setObservationStatus(`Error: ${errorMessage}`);
      }
      console.error('Error generating observations:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadReport = async () => {
    setIsDownloading(true);
    setDownloadStatus('Preparing PDF… This can take one to two minutes.');
    const controller = new AbortController();
    const downloadTimeoutMs = 180000; // 3 min — server builds PDF + may fetch images / Plotly chart
    const timeoutId = setTimeout(() => controller.abort(), downloadTimeoutMs);
    try {
      const usn = sessionStorage.getItem('userId');
      if (!usn) {
        setDownloadStatus('USN not found, please log in again.');
        setIsDownloading(false);
        return;
      }
      
      const response = await fetch(`${API_BASE_URL}/student/${usn}/reportdownload`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${sessionStorage.getItem('access_token')}`
        },
        signal: controller.signal,
      });

      // Check if response is OK
      if (!response.ok) {
        // Try to get error message
        let errorMessage = 'Failed to download report.';
        try {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            errorMessage = typeof data.detail === 'string' ? data.detail : 
                          (data.detail && typeof data.detail === 'object' ? JSON.stringify(data.detail) : 
                          `Server error: ${response.status} ${response.statusText}`);
          } else {
            const text = await response.text();
            errorMessage = text || `Server error: ${response.status} ${response.statusText}`;
          }
        } catch (e) {
          errorMessage = `Server error: ${response.status} ${response.statusText}`;
        }
        setDownloadStatus(errorMessage);
        setIsDownloading(false);
        return;
      }

      // Check if response is actually a PDF
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/pdf')) {
        setDownloadStatus('Error: Server did not return a PDF file.');
        setIsDownloading(false);
        return;
      }

      // Create blob from response
      const blob = await response.blob();
      console.log('Blob created, size:', blob.size, 'type:', blob.type);
      
      // Check if blob is valid
      if (!blob || blob.size === 0) {
        setDownloadStatus('Error: Received empty file.');
        setIsDownloading(false);
        return;
      }

      try {
        triggerPdfDownload(blob, `student_profile_${usn}.pdf`);
        setDownloadStatus('Report downloaded successfully! Check your downloads folder.');
      } catch (downloadError) {
        console.error('Download error:', downloadError);
        try {
          const objectUrl = URL.createObjectURL(blob);
          window.open(objectUrl, '_blank');
          setDownloadStatus('Report opened in a new tab. Use Ctrl+S to save the PDF.');
          setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
        } catch (fallbackError) {
          console.error('Fallback error:', fallbackError);
          setDownloadStatus('Error: Could not download file. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error downloading report:', error);
      if (error.name === 'AbortError') {
        setDownloadStatus('Download timed out. The server may still be building the PDF — wait a moment and tap Download again, or refresh and try from the dashboard.');
      } else {
        setDownloadStatus(`Failed to download report: ${error.message || 'Unknown error'}`);
      }
    } finally {
      clearTimeout(timeoutId);
      setIsDownloading(false);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setCalculationStatus('');
    navigate('/student/dashboard');
  };

  const handleCloseObservationModal = () => {
    setIsObservationModalOpen(false);
    navigate('/student/dashboard');
  }

  const handleCloseDownloadModal = () => {
    setIsDownloadModalOpen(false);
    navigate('/student/dashboard');
  }

  const renderQuestion = (fieldName) => {
    const question = questions.find(q => q.alias === fieldName);
    if (!question) return null;

    const hasAsterisk = question.has_asterisk || question.question.includes('*');

    return (
      <div key={fieldName} className={`mca-question ${hasAsterisk ? 'asterisk-question' : ''}`}>
        <label htmlFor={fieldName}>
          {question.question}
        </label>
        <select
          id={fieldName}
          name={fieldName}
          value={answers[fieldName]}
          onChange={(e) => handleChange(fieldName, e.target.value)}
          required
          className={hasAsterisk ? 'asterisk-select' : ''}
          disabled={isFormLocked}
        >
          <option value="">Select Rating</option>
          <option value="1">1 - Strongly Disagree</option>
          <option value="2">2 - Disagree</option>
          <option value="3">3 - Somewhat Disagree</option>
          <option value="4">4 - Neutral</option>
          <option value="5">5 - Somewhat Agree</option>
          <option value="6">6 - Agree</option>
          <option value="7">7 - Strongly Agree</option>
          <option value="NA">NA - Not Applicable</option>
        </select>
      </div>
    );
  };



  return (
    <div className="mca-form-container">
      <h2>MCA Details</h2>
      {loading ? <div className="loader"></div> : (
        <div className="mca-form-card">
          <h2>Mentorship Assessment Form</h2>
          
          {/* Lock Status Display */}
          {lockStatus && (
            <div className={`lock-status ${isFormLocked ? 'locked' : 'unlocked'}`}>
              {isFormLocked ? (
                <div className="lock-message">
                  <h3>🔒 Form is Currently Locked</h3>
                  <p>{lockStatus.message}</p>
                  {lockStatus.days_remaining !== undefined && (
                    <p><strong>Time remaining:</strong> {lockStatus.days_remaining} days and {lockStatus.hours_remaining} hours</p>
                  )}
                  {lockStatus.last_submission && (
                    <p><strong>Last submission:</strong> {lockStatus.last_submission}</p>
                  )}
                  {lockStatus.lock_ends && (
                    <p><strong>Lock ends:</strong> {lockStatus.lock_ends}</p>
                  )}
                </div>
              ) : (
                <div className="unlock-message">
                  <h3>✅ Form is Available</h3>
                  <p>{lockStatus.message}</p>
                  {lockStatus.last_submission && (
                    <p><strong>Last submission:</strong> {lockStatus.last_submission}</p>
                  )}
                </div>
              )}
            </div>
          )}
          
          <p>Please rate the following statements based on your experiences and perspectives.</p>
          
          <form onSubmit={handleSubmit}>
            <div className="form-section-unique">
              {pageFields[currentPage].map((field) => renderQuestion(field))}
            </div>

            <div className="form-navigation-buttons">
              {currentPage > 1 && (
                <button 
                  type="button" 
                  onClick={handlePrev} 
                  className="nav-button-unique"
                  disabled={isFormLocked}
                >
                  Previous
                </button>
              )}
              {currentPage < 6 ? (
                <button 
                  type="button" 
                  onClick={handleNext} 
                  className="nav-button-unique"
                  disabled={isFormLocked}
                >
                  Next
                </button>
              ) : (
                <button 
                  type="submit" 
                  className="submit-button-unique"
                  disabled={isFormLocked}
                >
                  {isFormLocked ? 'Form Locked' : 'Submit'}
                </button>
              )}
            </div>
          </form>
          {status && <p className="status-message">{status}</p>}
        </div>
      )}

      {/* Modal for after submission */}
      <Modal
        isOpen={isModalOpen}
        onRequestClose={handleCloseModal}
        contentLabel="MCA Submission Success"
        className="mca-modal"
        overlayClassName="mca-modal-overlay"
      >
        <h2>MCA Assignment Submitted</h2>
        <p>Your MCA assignment has been submitted successfully!</p>
        {isCalculating ? (
          <div className="loader"></div>
        ) : (
          <button onClick={handleCalculateCompetencies} className="mca-modal-button">
            Calculate Competencies
          </button>
        )}
        {calculationStatus && <p className="mca-modal-status">{calculationStatus}</p>}
      </Modal>

      {/* Modal for generating observation */}
      <Modal
        isOpen={isObservationModalOpen}
        onRequestClose={handleCloseObservationModal}
        contentLabel="Generate Observation"
        className="mca-modal"
        overlayClassName="mca-modal-overlay"
      >
        <h2>Competencies Calculated</h2>
        <p>Your competencies have been calculated successfully.</p>
        {isGenerating ? (
          <div className="loader"></div>
        ) : (
          <button onClick={handleGenerateObservation} className="mca-modal-button">
            Generate Observation
          </button>
        )}
        {observationStatus && <p className="mca-modal-status">{observationStatus}</p>}
      </Modal>

      {/* Modal for downloading report */}
      <Modal
        isOpen={isDownloadModalOpen}
        onRequestClose={handleCloseDownloadModal}
        contentLabel="Download Report"
        className="mca-modal"
        overlayClassName="mca-modal-overlay"
      >
        <h2>Observations Generated</h2>
        <p>Your observation report is ready for download.</p>
        {isDownloading ? (
          <div className="loader"></div>
        ) : (
          <button onClick={handleDownloadReport} className="mca-modal-button">
            Download Report
          </button>
        )}
        {downloadStatus && <p className="mca-modal-status">{downloadStatus}</p>}
      </Modal>
    </div>
  );
};

export default McaForm;