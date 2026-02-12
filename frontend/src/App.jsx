import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import DocumentUpload from './components/DocumentUpload';
import api from './services/api';
import './App.css';

const MenuIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="3" y1="12" x2="21" y2="12"/>
    <line x1="3" y1="6" x2="21" y2="6"/>
    <line x1="3" y1="18" x2="21" y2="18"/>
  </svg>
);

const UploadIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const CloseIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

function App() {
  const [activeTab, setActiveTab] = useState('chats');
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await api.getHealth();
      setHealthStatus(health);
    } catch (error) {
      console.error('Backend not available:', error);
      setHealthStatus({ status: 'error', message: 'Backend not connected' });
    }
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setActiveTab('chats');
  };

  const handleConversationSelect = (convId) => {
    setCurrentConversationId(convId);
    setActiveTab('chats');
  };

  const handleConversationStart = (convId) => {
    setCurrentConversationId(convId);
  };

  const handleUploadComplete = (result) => {
    if (result.status === 'success') {
      // Could refresh documents list or show notification
      setTimeout(() => {
        setShowUploadModal(false);
      }, 2000);
    }
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        currentConversationId={currentConversationId}
        onConversationSelect={handleConversationSelect}
        onNewChat={handleNewChat}
      />

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="main-header">
          <div className="header-left">
            <button 
              className="menu-btn btn-icon btn-ghost"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <MenuIcon />
            </button>
            <h1 className="header-title">University Assistant</h1>
          </div>
          
          <div className="header-right">
            {healthStatus && (
              <div className={`health-badge ${healthStatus.status === 'healthy' ? 'success' : 'error'}`}>
                <span className="health-dot"></span>
                {healthStatus.document_count !== undefined 
                  ? `${healthStatus.document_count} chunks` 
                  : healthStatus.message || 'Disconnected'}
              </div>
            )}
            <button 
              className="upload-btn btn btn-primary"
              onClick={() => setShowUploadModal(true)}
            >
              <UploadIcon />
              <span className="upload-btn-text">Upload</span>
            </button>
          </div>
        </header>

        {/* Chat Interface */}
        <div className="chat-container">
          <ChatInterface
            conversationId={currentConversationId}
            onConversationStart={handleConversationStart}
          />
        </div>
      </main>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="modal-overlay" onClick={() => setShowUploadModal(false)}>
          <div className="modal animate-slideUp" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Upload Document</h2>
              <button 
                className="btn-icon btn-ghost"
                onClick={() => setShowUploadModal(false)}
              >
                <CloseIcon />
              </button>
            </div>
            <DocumentUpload onUploadComplete={handleUploadComplete} />
          </div>
        </div>
      )}

      {/* Backend Error Banner */}
      {healthStatus?.status === 'error' && (
        <div className="error-banner animate-slideUp">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>
            Backend server is not running. Start it with: 
            <code>cd backend && uvicorn main:app --reload</code>
          </span>
        </div>
      )}
    </div>
  );
}

export default App;
