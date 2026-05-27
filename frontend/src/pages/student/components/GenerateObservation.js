import React, { useState } from 'react';
import Modal from 'react-modal';
import { useParams, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/Loader.css';

Modal.setAppElement('#root');

const GenerateObservation = () => {
  const { student_usn } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState('');

  const handleGenerateObservation = async () => {
    setIsGenerating(true);
    setStatus('Generating observations... This may take a few minutes.');
    try {
      const token = sessionStorage.getItem('access_token');
      if (!token) {
        setStatus('Authentication token not found. Please log in again.');
        setIsGenerating(false);
        return;
      }

      // Create AbortController for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout

      const response = await fetch(`${API_BASE_URL}/generate_observation_recommendations?student_usn=${student_usn}`, {
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
      const successMessage = typeof data.message === 'string' ? data.message : 'Observations generated successfully!';
      setStatus(successMessage);
    } catch (error) {
      if (error.name === 'AbortError') {
        setStatus('Request timed out. The generation is taking longer than expected. Please try again.');
      } else {
        const errorMessage = error.message || 'Failed to generate observations.';
        setStatus(`Error: ${errorMessage}`);
      }
      console.error('Error generating observations:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    navigate(`/student/${student_usn}/profile`);
  };

  return (
    <Modal
      isOpen={isModalOpen}
      onRequestClose={handleCloseModal}
      contentLabel="Generate Observation"
      className="mca-modal"
      overlayClassName="mca-modal-overlay"
    >
      <h2>Generate Observation</h2>
      <p>Click the button below to generate your observation report.</p>
      {isGenerating ? (
        <div className="loader"></div>
      ) : (
        <button onClick={handleGenerateObservation} className="mca-modal-button">
          Generate Observation
        </button>
      )}
      {status && <p className="mca-modal-status">{status}</p>}
      <button onClick={handleCloseModal} className="mca-modal-button" style={{ marginTop: '1rem' }}>
        Close
      </button>
    </Modal>
  );
};

export default GenerateObservation; 