import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../../api';
import './FeedbackForm.css';

const MAX_PDF_SIZE_MB = 10;

const FeedbackForm = ({ counselingId, mentorId, onClose, onSuccess }) => {
  const [feedback, setFeedback] = useState('');
  const [rating, setRating] = useState(0);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [existingFeedback, setExistingFeedback] = useState(null);

  useEffect(() => {
    fetchExistingFeedback();
  }, [counselingId]);

  const fetchExistingFeedback = async () => {
    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/mentor/${mentorId}/counseling/sessions/${counselingId}/feedback`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setExistingFeedback(data);
        if (data.mentor_feedback) {
          setFeedback(data.mentor_feedback);
          setRating(data.mentor_rating || 0);
        }
      }
    } catch (error) {
      console.error('Error fetching existing feedback:', error);
    }
  };

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) {
      setFile(null);
      return;
    }
    if (selected.type !== 'application/pdf') {
      setMessage('Only PDF format is allowed for proof.');
      setFile(null);
      e.target.value = '';
      return;
    }
    if (selected.size > MAX_PDF_SIZE_MB * 1024 * 1024) {
      setMessage(`File must be under ${MAX_PDF_SIZE_MB} MB`);
      setFile(null);
      e.target.value = '';
      return;
    }
    setFile(selected);
    setMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!feedback.trim()) {
      setMessage('Please provide your feedback');
      return;
    }

    if (rating === 0) {
      setMessage('Please provide a rating');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const token = sessionStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('feedback', feedback.trim());
      formData.append('rating', String(rating));
      if (file) formData.append('file', file);
      const response = await fetch(`${API_BASE_URL}/mentor/${mentorId}/counseling/sessions/${counselingId}/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Feedback submitted successfully!');
        setTimeout(() => {
          onSuccess && onSuccess();
          onClose();
        }, 1500);
      } else {
        setMessage(data.detail || 'Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setMessage('Failed to submit feedback. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStars = () => {
    return (
      <div className="star-rating">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            className={`star ${star <= rating ? 'active' : ''}`}
            onClick={() => setRating(star)}
            disabled={existingFeedback?.mentor_feedback}
          >
            ⭐
          </button>
        ))}
        <span className="rating-text">
          {rating > 0 ? `${rating} star${rating > 1 ? 's' : ''}` : 'Select rating'}
        </span>
      </div>
    );
  };

  if (existingFeedback?.mentor_feedback) {
    return (
      <div className="feedback-form-overlay">
        <div className="feedback-form-container">
          <div className="feedback-form-header">
            <h2>Your Feedback</h2>
            <button className="close-btn" onClick={onClose}>✖</button>
          </div>
          
          <div className="existing-feedback">
            <div className="feedback-rating">
              <span className="rating-label">Your Rating:</span>
              <div className="star-display">
                {'⭐'.repeat(existingFeedback.mentor_rating || 0)}
                <span className="rating-number">({existingFeedback.mentor_rating}/5)</span>
              </div>
            </div>
            
            <div className="feedback-text">
              <span className="feedback-label">Your Feedback:</span>
              <p className="feedback-content">"{existingFeedback.mentor_feedback}"</p>
            </div>
            
            <div className="feedback-date">
              Submitted on: {new Date(existingFeedback.mentor_feedback_date).toLocaleDateString()}
            </div>
            {existingFeedback.mentor_feedback_file_url && (
              <div style={{ marginTop: '0.75rem' }}>
                <span className="feedback-label">Your proof (PDF): </span>
                <a href={existingFeedback.mentor_feedback_file_url} target="_blank" rel="noopener noreferrer">View / Download PDF</a>
              </div>
            )}
            {existingFeedback.student_feedback && (
              <div className="student-feedback-section">
                <h3>Student's Feedback</h3>
                <div className="student-rating">
                  <span className="rating-label">Student's Rating:</span>
                  <div className="star-display">
                    {'⭐'.repeat(existingFeedback.student_rating || 0)}
                    <span className="rating-number">({existingFeedback.student_rating}/5)</span>
                  </div>
                </div>
                <p className="student-feedback-content">"{existingFeedback.student_feedback}"</p>
                <div className="student-feedback-date">
                  Received on: {new Date(existingFeedback.student_feedback_date).toLocaleDateString()}
                </div>
                {existingFeedback.student_feedback_file_url && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <a href={existingFeedback.student_feedback_file_url} target="_blank" rel="noopener noreferrer">View / Download mentee's file</a>
                  </div>
                )}
              </div>
            )}
          </div>
          
          <div className="feedback-form-actions">
            <button className="close-button" onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-form-overlay">
      <div className="feedback-form-container">
        <div className="feedback-form-header">
          <h2>Submit Feedback</h2>
          <button className="close-btn" onClick={onClose}>✖</button>
        </div>
        
        <form onSubmit={handleSubmit} className="feedback-form">
          <div className="form-group">
            <label htmlFor="rating">Rate the student support session:</label>
            {renderStars()}
          </div>
          
          <div className="form-group">
            <label htmlFor="feedback">Your Feedback:</label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Please share your thoughts about the student support session..."
              rows="5"
              required
              className="feedback-textarea"
            />
          </div>
          <div className="form-group">
            <label htmlFor="feedback-proof">Attach proof (PDF, optional, max {MAX_PDF_SIZE_MB} MB):</label>
            <input
              id="feedback-proof"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              className="feedback-file-input"
            />
            {file && <span className="file-name">{file.name}</span>}
          </div>
          {message && (
            <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}
          
          <div className="feedback-form-actions">
            <button type="button" className="cancel-button" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackForm;
