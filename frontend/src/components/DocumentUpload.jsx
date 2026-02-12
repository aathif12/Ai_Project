import { useState, useRef } from 'react';
import api from '../services/api';
import './DocumentUpload.css';

const UploadIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const DocumentUpload = ({ onUploadComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const [category, setCategory] = useState('other');
  
  const fileInputRef = useRef(null);

  const categories = [
    { value: 'rules', label: 'Rules & Policies' },
    { value: 'exams', label: 'Exams' },
    { value: 'courses', label: 'Courses' },
    { value: 'hostel', label: 'Hostel' },
    { value: 'timetable', label: 'Timetable' },
    { value: 'notices', label: 'Notices' },
    { value: 'handbook', label: 'Handbook' },
    { value: 'other', label: 'Other' },
  ];

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    // Validate file type
    const validTypes = ['.pdf', '.docx'];
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validTypes.includes(fileExt)) {
      setError(`Invalid file type. Please upload PDF or DOCX files.`);
      return;
    }

    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File is too large. Maximum size is 50MB.');
      return;
    }

    setError(null);
    setUploadResult(null);
    setIsUploading(true);
    setUploadProgress(0);

    // Simulate progress (actual progress would need XHR or fetch with ReadableStream)
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 200);

    try {
      const result = await api.uploadDocument(file, category);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      setUploadResult(result);
      onUploadComplete?.(result);
      
      // Reset after delay
      setTimeout(() => {
        setUploadProgress(0);
        setIsUploading(false);
      }, 2000);
      
    } catch (err) {
      clearInterval(progressInterval);
      setError(err.message || 'Upload failed. Please try again.');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="document-upload">
      <div className="upload-header">
        <h3>Upload Documents</h3>
        <p>Upload PDF or DOCX files to make them searchable</p>
      </div>

      {/* Category Selection */}
      <div className="category-select">
        <label htmlFor="category">Document Category</label>
        <select 
          id="category"
          className="input select"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {categories.map(cat => (
            <option key={cat.value} value={cat.value}>{cat.label}</option>
          ))}
        </select>
      </div>

      {/* Drop Zone */}
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        {isUploading ? (
          <div className="upload-progress">
            <div className="progress-ring">
              <svg viewBox="0 0 36 36">
                <path
                  className="progress-ring-bg"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="progress-ring-fill"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                  style={{ strokeDasharray: `${uploadProgress}, 100` }}
                />
              </svg>
              <span className="progress-text">
                {uploadProgress === 100 ? <CheckIcon /> : `${uploadProgress}%`}
              </span>
            </div>
            <p>{uploadProgress === 100 ? 'Processing complete!' : 'Uploading & processing...'}</p>
          </div>
        ) : (
          <>
            <UploadIcon />
            <p className="drop-zone-text">
              <strong>Drop your file here</strong>
              <span>or click to browse</span>
            </p>
            <p className="drop-zone-hint">PDF or DOCX, max 50MB</p>
          </>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="upload-error animate-slideUp">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {error}
        </div>
      )}

      {/* Success Message */}
      {uploadResult && uploadResult.status === 'success' && (
        <div className="upload-success animate-slideUp">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <div>
            <strong>{uploadResult.filename}</strong>
            <span>{uploadResult.chunk_count} searchable chunks created</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
