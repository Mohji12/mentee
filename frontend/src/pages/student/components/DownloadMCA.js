import React, { useState } from 'react';
import Modal from 'react-modal';
import { useParams, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/Loader.css';
import { triggerPdfDownload } from '../../../utils/triggerPdfDownload';

Modal.setAppElement('#root');

const DownloadMCA = () => {
  const { student_usn } = useParams();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [status, setStatus] = useState('');

  const handleDownloadReport = async () => {
    setIsDownloading(true);
    setStatus('Generating report... This may take a moment.');
    try {
      console.log('Starting download for USN:', student_usn);
      const response = await fetch(`${API_BASE_URL}/student/${student_usn}/reportdownload`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${sessionStorage.getItem('access_token')}`
        }
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
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
        setStatus(errorMessage);
        setIsDownloading(false);
        return;
      }

      // Check if response is actually a PDF
      const contentType = response.headers.get('content-type');
      console.log('Content-Type:', contentType);
      
      // If not PDF, try to get error message
      if (!contentType || !contentType.includes('application/pdf')) {
        let errorText = '';
        try {
          errorText = await response.text();
          console.log('Error response:', errorText);
          // Try to parse as JSON
          try {
            const errorData = JSON.parse(errorText);
            setStatus(errorData.detail || errorData.message || 'Error: Server did not return a PDF file.');
          } catch {
            setStatus(errorText || 'Error: Server did not return a PDF file.');
          }
        } catch (e) {
          setStatus('Error: Server did not return a PDF file. Please ensure you have completed the MCA assessment.');
        }
        setIsDownloading(false);
        return;
      }

      // Create blob from response
      const blob = await response.blob();
      console.log('Blob created, size:', blob.size, 'type:', blob.type);
      
      // Check if blob is valid
      if (!blob || blob.size === 0) {
        setStatus('Error: Received empty file.');
        setIsDownloading(false);
        return;
      }

      try {
        triggerPdfDownload(blob, `student_profile_${student_usn}.pdf`);
        setStatus('Report downloaded successfully! Check your downloads folder.');
      } catch (downloadError) {
        console.error('Download error:', downloadError);
        try {
          const objectUrl = URL.createObjectURL(blob);
          window.open(objectUrl, '_blank');
          setStatus('Report opened in a new tab. Use Ctrl+S to save the PDF.');
          setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
        } catch (fallbackError) {
          console.error('Fallback error:', fallbackError);
          setStatus('Error: Could not download file. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error downloading report:', error);
      setStatus(`Failed to download report: ${error.message || 'Unknown error'}`);
    } finally {
      setIsDownloading(false);
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
      contentLabel="Download MCA Report"
      className="mca-modal"
      overlayClassName="mca-modal-overlay"
    >
      <h2>Download MCA Report</h2>
      <p>Click the button below to download your MCA report.</p>
      {isDownloading ? (
        <div className="loader"></div>
      ) : (
        <button onClick={handleDownloadReport} className="mca-modal-button">
          Download MCA
        </button>
      )}
      {status && <p className="mca-modal-status">{status}</p>}
      <button onClick={handleCloseModal} className="mca-modal-button" style={{ marginTop: '1rem' }}>
        Close
      </button>
    </Modal>
  );
};

export default DownloadMCA; 