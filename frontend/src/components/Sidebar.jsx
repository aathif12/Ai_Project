import { useState, useEffect } from 'react';
import api from '../services/api';
import './Sidebar.css';

const ChatIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
);

const PlusIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="12" y1="5" x2="12" y2="19"/>
    <line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
);

const DocumentIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
);

const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  </svg>
);

const Sidebar = ({ 
  activeTab, 
  onTabChange, 
  currentConversationId,
  onConversationSelect,
  onNewChat 
}) => {
  const [conversations, setConversations] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [convs, docs] = await Promise.all([
        api.getConversations(),
        api.getDocuments()
      ]);
      setConversations(convs);
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading sidebar data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async (e, convId) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(convId);
      setConversations(prev => prev.filter(c => c.id !== convId));
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleDeleteDocument = async (e, docId) => {
    e.stopPropagation();
    try {
      await api.deleteDocument(docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <div className="logo">
          <div className="logo-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="url(#logoGradient)" strokeWidth="2">
              <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#667eea" />
                  <stop offset="100%" stopColor="#764ba2" />
                </linearGradient>
              </defs>
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <span className="logo-text">UniRAG</span>
        </div>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat}>
        <PlusIcon />
        New Chat
      </button>

      {/* Tabs */}
      <div className="sidebar-tabs">
        <button 
          className={`sidebar-tab ${activeTab === 'chats' ? 'active' : ''}`}
          onClick={() => onTabChange('chats')}
        >
          <ChatIcon />
          Chats
        </button>
        <button 
          className={`sidebar-tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => onTabChange('documents')}
        >
          <DocumentIcon />
          Documents
        </button>
      </div>

      {/* Content */}
      <div className="sidebar-content">
        {isLoading ? (
          <div className="sidebar-loading">
            <div className="spinner"></div>
          </div>
        ) : activeTab === 'chats' ? (
          <div className="conversation-list">
            {conversations.length === 0 ? (
              <div className="sidebar-empty">
                <p>No conversations yet</p>
                <span>Start a new chat!</span>
              </div>
            ) : (
              conversations.map(conv => (
                <div
                  key={conv.id}
                  className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
                  onClick={() => onConversationSelect(conv.id)}
                >
                  <div className="conversation-info">
                    <p className="conversation-preview">{conv.preview}</p>
                    <span className="conversation-date">{formatDate(conv.updated_at)}</span>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={(e) => handleDeleteConversation(e, conv.id)}
                    title="Delete conversation"
                  >
                    <TrashIcon />
                  </button>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="document-list">
            {documents.length === 0 ? (
              <div className="sidebar-empty">
                <p>No documents uploaded</p>
                <span>Upload documents to get started!</span>
              </div>
            ) : (
              documents.map(doc => (
                <div key={doc.id} className="document-item">
                  <div className="document-info">
                    <p className="document-name">{doc.filename}</p>
                    <div className="document-meta">
                      <span className="document-category">{doc.category}</span>
                      <span className="document-date">{formatDate(doc.uploaded_at)}</span>
                    </div>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={(e) => handleDeleteDocument(e, doc.id)}
                    title="Delete document"
                  >
                    <TrashIcon />
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span>Ready</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
