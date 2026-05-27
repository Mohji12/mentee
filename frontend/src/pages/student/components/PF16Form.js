import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/PF16Form.css';
import Modal from 'react-modal';
import '../../../assets/css/Loader.css';

Modal.setAppElement('#root');

const QUESTIONS_PER_PAGE = 10;
const TOTAL_QUESTIONS = 185;

const PF16Form = () => {
  const { student_usn } = useParams();
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [status, setStatus] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLocked, setIsLocked] = useState(false);
  const [submittedAt, setSubmittedAt] = useState(null);

  const totalPages = Math.ceil(TOTAL_QUESTIONS / QUESTIONS_PER_PAGE);

  useEffect(() => {
    const fetchFormData = async () => {
      try {
        setLoading(true);
        const token = sessionStorage.getItem('access_token');
        if (!token) {
          setStatus('Please log in again.');
          setLoading(false);
          return;
        }

        const response = await fetch(`${API_BASE_URL}/student/${student_usn}/pf16-form`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setQuestions(data.questions || []);
        setIsLocked(data.is_locked || false);
        setSubmittedAt(data.submitted_at ? new Date(data.submitted_at) : null);

        if (data.questions && Array.isArray(data.questions)) {
          const initialAnswers = {};
          // If form is locked and responses are available, use them
          if (data.is_locked && data.responses) {
            console.log('PF16: Loading locked form with responses:', data.responses);
            data.questions.forEach(q => {
              // JSON keys are strings, so convert question_number to string for lookup
              const qNum = q.question_number;
              const qNumStr = String(qNum);
              const responseValue = data.responses[qNumStr] || '';
              initialAnswers[qNum] = responseValue;
              if (qNum <= 10) {
                console.log(`PF16 Q${qNum}: responseValue =`, responseValue, 'from responses[qNumStr]:', data.responses[qNumStr]);
              }
            });
          } else {
            // Otherwise initialize as empty
            console.log('PF16: Form not locked or no responses available. is_locked:', data.is_locked, 'responses:', data.responses);
            data.questions.forEach(q => {
              initialAnswers[q.question_number] = '';
            });
          }
          setAnswers(initialAnswers);
        }
      } catch (error) {
        console.error('Error fetching form data:', error);
        setStatus('Error loading form. Please refresh the page.');
      } finally {
        setLoading(false);
      }
    };

    fetchFormData();
  }, [student_usn]);

  const handleAnswerChange = (questionNumber, value) => {
    if (isLocked) return;
    setAnswers(prev => ({
      ...prev,
      [questionNumber]: value
    }));
  };

  const validateCurrentPage = () => {
    const startIdx = (currentPage - 1) * QUESTIONS_PER_PAGE;
    const endIdx = Math.min(startIdx + QUESTIONS_PER_PAGE, questions.length);
    const pageQuestions = questions.slice(startIdx, endIdx);
    
    return pageQuestions.every(q => {
      const answer = answers[q.question_number];
      return answer === 'a' || answer === 'b' || answer === 'c';
    });
  };

  const handleNext = () => {
    if (validateCurrentPage()) {
      if (currentPage < totalPages) {
        setCurrentPage(prev => prev + 1);
        setStatus('');
      }
    } else {
      setStatus('Please answer all questions on this page before proceeding.');
    }
  };

  const handlePrevious = () => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
      setStatus('');
    }
  };

  const handleSubmit = async () => {
    if (isLocked) {
      setStatus('Form is already submitted and locked.');
      return;
    }

    const unanswered = questions.filter(q => {
      const answer = answers[q.question_number];
      return !answer || (answer !== 'a' && answer !== 'b' && answer !== 'c');
    });

    if (unanswered.length > 0) {
      setStatus(`Please answer all ${TOTAL_QUESTIONS} questions before submitting.`);
      return;
    }

    setIsSubmitting(true);
    setStatus('');

    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/student/${student_usn}/pf16-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ responses: answers }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsModalOpen(true);
        setIsLocked(true);
        setSubmittedAt(new Date(data.submitted_at));
        setStatus('16PF form submitted successfully!');
      } else {
        setStatus(data.detail || 'Form submission failed.');
      }
    } catch (error) {
      console.error('Submission error:', error);
      setStatus('Network error. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="pf16-page">
        <div className="loader"></div>
        <p>Loading 16PF form...</p>
      </div>
    );
  }

  const startIdx = (currentPage - 1) * QUESTIONS_PER_PAGE;
  const endIdx = Math.min(startIdx + QUESTIONS_PER_PAGE, questions.length);
  const pageQuestions = questions.slice(startIdx, endIdx);

  return (
    <div className="pf16-page">
      <h1 className="pf16-title">16PF Personality Assessment</h1>
      
      {isLocked && submittedAt && (
        <div className="pf16-locked-message">
          <p>✓ Form submitted on {submittedAt.toLocaleDateString()} at {submittedAt.toLocaleTimeString()}</p>
          <p>This form is locked and cannot be edited.</p>
        </div>
      )}

      {status && (
        <div className={`pf16-status ${status.includes('success') ? 'pf16-success' : 'pf16-error'}`}>
          {status}
        </div>
      )}

      {!isLocked && (
        <>
          <div className="pf16-progress">
            <p>Page {currentPage} of {totalPages}</p>
            <p>Questions {startIdx + 1} - {endIdx} of {TOTAL_QUESTIONS}</p>
          </div>

          <div className="pf16-instructions">
            <p><strong>Instructions:</strong></p>
            <ul>
              <li>Please answer all questions honestly</li>
              <li>Each question has 3 options: <strong>a</strong>, <strong>b</strong>, or <strong>c</strong></li>
              <li>Select the option that best describes you</li>
              <li>You must answer all {TOTAL_QUESTIONS} questions before submitting</li>
              <li>Once submitted, the form will be locked and cannot be edited</li>
            </ul>
          </div>

          <div className="pf16-questions-container">
            {pageQuestions.map((question) => (
              <div key={question.question_number} className="pf16-question-block">
                <div className="pf16-question-header">
                  <span className="pf16-question-number">Question {question.question_number}</span>
                </div>
                <p className="pf16-question-text">{question.text}</p>
                <div className="pf16-options">
                  {['a', 'b', 'c'].map((option) => (
                    <label key={option} className="pf16-option-label">
                      <input
                        type="radio"
                        name={`q${question.question_number}`}
                        value={option}
                        checked={answers[question.question_number] === option}
                        onChange={(e) => handleAnswerChange(question.question_number, e.target.value)}
                        className="pf16-radio"
                      />
                      <span className="pf16-option-letter">{option.toUpperCase()}</span>
                      <span className="pf16-option-text">{question.options[option]}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="pf16-navigation">
            <button
              onClick={handlePrevious}
              disabled={currentPage === 1}
              className="pf16-nav-btn pf16-prev-btn"
            >
              Previous
            </button>
            <span className="pf16-page-indicator">
              Page {currentPage} of {totalPages}
            </span>
            {currentPage < totalPages ? (
              <button
                onClick={handleNext}
                className="pf16-nav-btn pf16-next-btn"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting || !validateCurrentPage()}
                className="pf16-submit-btn"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Form'}
              </button>
            )}
          </div>
        </>
      )}

      {isLocked && (
        <div className="pf16-readonly-view">
          <h2>Your Responses</h2>
          <p>Form is locked. View your submitted responses below:</p>
          <div className="pf16-responses-summary">
            {questions.slice(0, 10).map((q) => (
              <div key={q.question_number} className="pf16-response-item">
                <strong>Q{q.question_number}:</strong> {q.text}
                <br />
                <span className="pf16-answer">
                  Answer: <strong>{answers[q.question_number]?.toUpperCase() || 'Not answered'}</strong>
                </span>
              </div>
            ))}
            {questions.length > 10 && (
              <p className="pf16-more-info">
                ... and {questions.length - 10} more questions.
              </p>
            )}
          </div>
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onRequestClose={() => setIsModalOpen(false)}
        contentLabel="Submission Success"
        className="pf16-modal"
        overlayClassName="pf16-modal-overlay"
      >
        <h2>✓ Form Submitted Successfully!</h2>
        <p>Your 16PF form has been submitted and locked.</p>
        <div className="pf16-modal-buttons">
          <button onClick={() => setIsModalOpen(false)} className="pf16-modal-close-btn">
            Close
          </button>
        </div>
      </Modal>
    </div>
  );
};

export default PF16Form;
