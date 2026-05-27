import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { API_BASE_URL } from '../../../api';
import '../../../assets/css/ExperienceLearning.css';
import { FaPlus, FaEdit, FaTrash, FaFile, FaTimes } from 'react-icons/fa';

const ExperienceLearning = () => {
  const { mentor_id } = useParams();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEntry, setCurrentEntry] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    detailed_explanation: '',
  });
  const [proofFile, setProofFile] = useState(null);
  const [uploadingProof, setUploadingProof] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchEntries();
  }, [mentor_id]);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/mentor/${mentor_id}/experience-learning`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch experiential learning entries');
      }

      const data = await response.json();
      setEntries(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      console.error('Error fetching entries:', err);
      setError(err.message);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e) => {
    setProofFile(e.target.files[0]);
  };

  const handleOpenModal = (entry = null) => {
    if (entry) {
      setIsEditing(true);
      setCurrentEntry(entry);
      setFormData({
        title: entry.title || '',
        detailed_explanation: entry.detailed_explanation || '',
      });
      setProofFile(null);
    } else {
      setIsEditing(false);
      setCurrentEntry(null);
      setFormData({
        title: '',
        detailed_explanation: '',
      });
      setProofFile(null);
    }
    setIsModalOpen(true);
    setMessage('');
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setIsEditing(false);
    setCurrentEntry(null);
    setFormData({
      title: '',
      detailed_explanation: '',
    });
    setProofFile(null);
    setMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.title.trim() || !formData.detailed_explanation.trim()) {
      setMessage('Please fill in all required fields.');
      return;
    }

    try {
      const token = sessionStorage.getItem('access_token');
      let entryId;

      if (isEditing && currentEntry) {
        // Update existing entry
        const response = await fetch(
          `${API_BASE_URL}/mentor/${mentor_id}/experience-learning/${currentEntry.id}`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
              title: formData.title.trim(),
              detailed_explanation: formData.detailed_explanation.trim(),
            }),
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to update entry');
        }

        entryId = currentEntry.id;
        setMessage('Entry updated successfully!');
      } else {
        // Create new entry
        const response = await fetch(
          `${API_BASE_URL}/mentor/${mentor_id}/experience-learning`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
              title: formData.title.trim(),
              detailed_explanation: formData.detailed_explanation.trim(),
            }),
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to create entry');
        }

        const data = await response.json();
        entryId = data.id;
        setMessage('Entry created successfully!');
      }

      // Upload proof file if provided
      if (proofFile) {
        await uploadProof(entryId);
      } else {
        // Refresh entries after a short delay
        setTimeout(() => {
          fetchEntries();
          handleCloseModal();
        }, 1000);
      }
    } catch (err) {
      console.error('Error saving entry:', err);
      setMessage(`Error: ${err.message}`);
    }
  };

  const uploadProof = async (entryId) => {
    if (!proofFile) return;

    try {
      setUploadingProof(true);
      const token = sessionStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', proofFile);

      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/experience-learning/${entryId}/upload-proof`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload proof file');
      }

      setMessage('Entry saved and proof uploaded successfully!');
      setTimeout(() => {
        fetchEntries();
        handleCloseModal();
      }, 1000);
    } catch (err) {
      console.error('Error uploading proof:', err);
      setMessage(`Error uploading proof: ${err.message}`);
    } finally {
      setUploadingProof(false);
    }
  };

  const handleDelete = async (entryId) => {
    if (!window.confirm('Are you sure you want to delete this entry?')) {
      return;
    }

    try {
      const token = sessionStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/mentor/${mentor_id}/experience-learning/${entryId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete entry');
      }

      fetchEntries();
    } catch (err) {
      console.error('Error deleting entry:', err);
      alert(`Error: ${err.message}`);
    }
  };

  const handleViewProof = (proofUrl) => {
    if (proofUrl) {
      window.open(proofUrl, '_blank');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="el-loading">
        <div className="el-loading-spinner"></div>
        <p>Loading experiential learning entries...</p>
      </div>
    );
  }

  return (
    <div className="el-container">
      <div className="el-header">
        <h2 className="el-title">Experiential Learning</h2>
        <button className="el-add-btn" onClick={() => handleOpenModal()}>
          <FaPlus /> Add New Entry
        </button>
      </div>

      {error && (
        <div className="el-error">
          <p>Error: {error}</p>
        </div>
      )}

      {entries.length === 0 ? (
        <div className="el-empty">
          <p>No experiential learning entries yet.</p>
          <p>Click "Add New Entry" to get started.</p>
        </div>
      ) : (
        <div className="el-entries-list">
          {entries.map((entry) => (
            <div key={entry.id} className="el-entry-card">
              <div className="el-entry-header">
                <h3 className="el-entry-title">{entry.title}</h3>
                <div className="el-entry-actions">
                  <button
                    className="el-edit-btn"
                    onClick={() => handleOpenModal(entry)}
                    title="Edit entry"
                  >
                    <FaEdit />
                  </button>
                  <button
                    className="el-delete-btn"
                    onClick={() => handleDelete(entry.id)}
                    title="Delete entry"
                  >
                    <FaTrash />
                  </button>
                </div>
              </div>
              <div className="el-entry-content">
                <p className="el-entry-explanation">{entry.detailed_explanation}</p>
                {entry.proof_url && (
                  <div className="el-entry-proof">
                    <button
                      className="el-proof-btn"
                      onClick={() => handleViewProof(entry.proof_url)}
                    >
                      <FaFile /> View Proof
                    </button>
                  </div>
                )}
                <div className="el-entry-meta">
                  <span className="el-entry-date">
                    Created: {formatDate(entry.created_at)}
                  </span>
                  {entry.updated_at !== entry.created_at && (
                    <span className="el-entry-date">
                      Updated: {formatDate(entry.updated_at)}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Add/Edit */}
      {isModalOpen && (
        <div className="el-modal-overlay" onClick={handleCloseModal}>
          <div className="el-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="el-modal-header">
              <h3>{isEditing ? 'Edit Entry' : 'Add New Entry'}</h3>
              <button className="el-modal-close" onClick={handleCloseModal}>
                <FaTimes />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="el-form">
              <div className="el-form-group">
                <label htmlFor="title">
                  Title <span className="el-required">*</span>
                </label>
                <input
                  id="title"
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Enter a title for your experience"
                  required
                  maxLength={255}
                />
              </div>

              <div className="el-form-group">
                <label htmlFor="detailed_explanation">
                  Detailed Explanation <span className="el-required">*</span>
                </label>
                <textarea
                  id="detailed_explanation"
                  name="detailed_explanation"
                  value={formData.detailed_explanation}
                  onChange={handleInputChange}
                  placeholder="Provide a detailed explanation of your learning experience..."
                  required
                  rows={6}
                />
              </div>

              <div className="el-form-group">
                <label htmlFor="proof_file">
                  Proof File (Optional)
                  {currentEntry?.proof_url && (
                    <span className="el-existing-proof">
                      {' '}
                      - Current proof available
                    </span>
                  )}
                </label>
                <input
                  id="proof_file"
                  type="file"
                  onChange={handleFileChange}
                  accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.zip"
                />
                <small className="el-file-hint">
                  Allowed types: Images, PDF, Word, Text, ZIP (Max 10MB)
                </small>
              </div>

              {message && (
                <div className={`el-message ${message.includes('Error') ? 'el-error-msg' : 'el-success-msg'}`}>
                  {message}
                </div>
              )}

              <div className="el-form-actions">
                <button
                  type="submit"
                  className="el-save-btn"
                  disabled={uploadingProof}
                >
                  {uploadingProof ? 'Uploading...' : isEditing ? 'Update Entry' : 'Create Entry'}
                </button>
                <button
                  type="button"
                  className="el-cancel-btn"
                  onClick={handleCloseModal}
                  disabled={uploadingProof}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExperienceLearning;
