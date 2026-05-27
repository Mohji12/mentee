import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/IBPForm.css';
import Modal from 'react-modal';
import '../../../assets/css/Loader.css';

Modal.setAppElement('#root');

const QUESTIONS_PER_PAGE = 10;
const TOTAL_QUESTIONS = 36;
const OPTION_LABELS = { 1: 'Rarely', 2: 'Occasionally', 3: 'Sometimes', 4: 'Often', 5: 'Always' };

const IBPForm = () => {
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

        const response = await fetch(`${API_BASE_URL}/student/${student_usn}/ibp-form`, {
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
            console.log('IBP: Loading locked form with responses:', data.responses);
            data.questions.forEach((q) => {
              // JSON keys are strings, so convert question_number to string for lookup
              const qNum = q.question_number;
              const qNumStr = String(qNum);
              const responseValue = data.responses[qNumStr] || '';
              initialAnswers[qNum] = responseValue;
              if (qNum <= 10) {
                console.log(`IBP Q${qNum}: responseValue =`, responseValue, 'from responses[qNumStr]:', data.responses[qNumStr]);
              }
            });
          } else {
            // Otherwise initialize as empty
            console.log('IBP: Form not locked or no responses available. is_locked:', data.is_locked, 'responses:', data.responses);
            data.questions.forEach((q) => {
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
    const numVal = parseInt(value, 10);
    setAnswers((prev) => ({
      ...prev,
      [questionNumber]: numVal,
    }));
  };

  const isValidAnswer = (answer) =>
    answer === 1 || answer === 2 || answer === 3 || answer === 4 || answer === 5;

  const validateCurrentPage = () => {
    const startIdx = (currentPage - 1) * QUESTIONS_PER_PAGE;
    const endIdx = Math.min(startIdx + QUESTIONS_PER_PAGE, questions.length);
    const pageQuestions = questions.slice(startIdx, endIdx);

    return pageQuestions.every((q) => isValidAnswer(answers[q.question_number]));
  };

  const handleNext = () => {
    if (validateCurrentPage()) {
      if (currentPage < totalPages) {
        setCurrentPage((prev) => prev + 1);
        setStatus('');
      }
    } else {
      setStatus('Please answer all questions on this page before proceeding.');
    }
  };

  const handlePrevious = () => {
    if (currentPage > 1) {
      setCurrentPage((prev) => prev - 1);
      setStatus('');
    }
  };

  const handleSubmit = async () => {
    if (isLocked) {
      setStatus('Form is already submitted and locked.');
      return;
    }

    const unanswered = questions.filter((q) => !isValidAnswer(answers[q.question_number]));

    if (unanswered.length > 0) {
      setStatus(`Please answer all ${TOTAL_QUESTIONS} questions before submitting.`);
      return;
    }

    setIsSubmitting(true);
    setStatus('');

    try {
      const token = sessionStorage.getItem('access_token');
      const payload = {};
      questions.forEach((q) => {
        payload[q.question_number] = answers[q.question_number];
      });

      const response = await fetch(`${API_BASE_URL}/student/${student_usn}/ibp-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ responses: payload }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsModalOpen(true);
        setIsLocked(true);
        setSubmittedAt(new Date(data.submitted_at));
        setStatus('IBP form submitted successfully!');
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
      <div className="ibp-page">
        <div className="loader"></div>
        <p>Loading IBP form...</p>
      </div>
    );
  }

  const startIdx = (currentPage - 1) * QUESTIONS_PER_PAGE;
  const endIdx = Math.min(startIdx + QUESTIONS_PER_PAGE, questions.length);
  const pageQuestions = questions.slice(startIdx, endIdx);

  return (
    <div className="ibp-page">
      <h1 className="ibp-title">IBP – Institutional Behaviour Profile</h1>

      {isLocked && submittedAt && (
        <div className="ibp-locked-message">
          <p>
            ✓ Form submitted on {submittedAt.toLocaleDateString()} at{' '}
            {submittedAt.toLocaleTimeString()}
          </p>
          <p>This form is locked and cannot be edited.</p>
        </div>
      )}

      {status && (
        <div
          className={`ibp-status ${status.includes('success') ? 'ibp-success' : 'ibp-error'}`}
        >
          {status}
        </div>
      )}

      {!isLocked && (
        <>
          <div className="ibp-progress">
            <p>Page {currentPage} of {totalPages}</p>
            <p>
              Questions {startIdx + 1} - {endIdx} of {TOTAL_QUESTIONS}
            </p>
          </div>

          <div className="ibp-instructions">
            <p>
              <strong>Instructions:</strong>
            </p>
            <ul>
              <li>Please answer all statements honestly</li>
              <li>For each statement choose one: Rarely (1), Occasionally (2), Sometimes (3), Often (4), Always (5)</li>
              <li>You must answer all {TOTAL_QUESTIONS} statements before submitting</li>
              <li>Once submitted, the form will be locked and cannot be edited</li>
            </ul>
          </div>

          <div className="ibp-questions-container">
            {pageQuestions.map((question) => (
              <div key={question.question_number} className="ibp-question-block">
                <div className="ibp-question-header">
                  <span className="ibp-question-number">Statement {question.question_number}</span>
                </div>
                <p className="ibp-question-text">{question.text}</p>
                <div className="ibp-options">
                  {[1, 2, 3, 4, 5].map((option) => (
                    <label key={option} className="ibp-option-label">
                      <input
                        type="radio"
                        name={`q${question.question_number}`}
                        value={option}
                        checked={answers[question.question_number] === option}
                        onChange={(e) =>
                          handleAnswerChange(question.question_number, e.target.value)
                        }
                        className="ibp-radio"
                      />
                      <span className="ibp-option-number">{option}</span>
                      <span className="ibp-option-text">
                        {question.options[String(option)] || OPTION_LABELS[option]}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="ibp-navigation">
            <button
              onClick={handlePrevious}
              disabled={currentPage === 1}
              className="ibp-nav-btn ibp-prev-btn"
            >
              Previous
            </button>
            <span className="ibp-page-indicator">
              Page {currentPage} of {totalPages}
            </span>
            {currentPage < totalPages ? (
              <button onClick={handleNext} className="ibp-nav-btn ibp-next-btn">
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isSubmitting || !validateCurrentPage()}
                className="ibp-submit-btn"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Form'}
              </button>
            )}
          </div>
        </>
      )}

      {isLocked && (
        <div className="ibp-readonly-view">
          <h2>Your Responses</h2>
          <p>Form is locked. View your submitted responses below:</p>
          <div className="ibp-responses-summary">
            {questions.slice(0, 10).map((q) => (
              <div key={q.question_number} className="ibp-response-item">
                <strong>Q{q.question_number}:</strong> {q.text}
                <br />
                <span className="ibp-answer">
                  Answer: <strong>{OPTION_LABELS[answers[q.question_number]] || 'Not answered'}</strong>
                </span>
              </div>
            ))}
            {questions.length > 10 && (
              <p className="ibp-more-info">
                ... and {questions.length - 10} more statements.
              </p>
            )}
          </div>
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onRequestClose={() => setIsModalOpen(false)}
        contentLabel="Submission Success"
        className="ibp-modal"
        overlayClassName="ibp-modal-overlay"
      >
        <h2>✓ Form Submitted Successfully!</h2>
        <p>Your IBP form has been submitted and locked.</p>
        <div className="ibp-modal-buttons">
          <button onClick={() => setIsModalOpen(false)} className="ibp-modal-close-btn">
            Close
          </button>
        </div>
      </Modal>
    </div>
  );
};

export default IBPForm;
