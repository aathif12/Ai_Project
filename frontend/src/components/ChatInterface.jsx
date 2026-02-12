import { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import './ChatInterface.css';

// Icons as simple SVG components
const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
  </svg>
);

const LoadingDots = () => (
  <div className="loading-dots">
    <span></span>
    <span></span>
    <span></span>
  </div>
);

const ThumbsUp = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
  </svg>
);

const ThumbsDown = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/>
  </svg>
);

const DocumentIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
);

const ChatInterface = ({ conversationId, onConversationStart }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(conversationId);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Load suggestions on mount
  useEffect(() => {
    loadSuggestions();
  }, []);

  // Load conversation if ID provided
  useEffect(() => {
    if (conversationId && conversationId !== currentConversationId) {
      setCurrentConversationId(conversationId);
      loadConversation(conversationId);
    }
  }, [conversationId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSuggestions = async () => {
    try {
      const data = await api.getSuggestions();
      setSuggestions(data);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const loadConversation = async (convId) => {
    try {
      const history = await api.getConversationHistory(convId);
      setMessages(history);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.sendMessage(
        userMessage.content,
        currentConversationId
      );

      // Update conversation ID if this is a new conversation
      if (!currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        onConversationStart?.(response.conversation_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        citations: response.citations,
        confidence: response.confidence,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        isError: true,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  const handleFeedback = async (messageIndex, isHelpful) => {
    if (!currentConversationId) return;

    try {
      await api.submitFeedback(currentConversationId, messageIndex, isHelpful);
      // Update message to show feedback was submitted
      setMessages(prev => prev.map((msg, idx) => 
        idx === messageIndex ? { ...msg, feedbackGiven: isHelpful ? 'positive' : 'negative' } : msg
      ));
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-interface">
      {/* Messages Area */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome animate-fadeIn">
            <div className="welcome-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="url(#gradient)" strokeWidth="1.5">
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#667eea" />
                    <stop offset="100%" stopColor="#764ba2" />
                  </linearGradient>
                </defs>
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </div>
            <h2>Welcome to UniRAG</h2>
            <p>Ask me anything about your university documents!</p>
            
            {suggestions.length > 0 && (
              <div className="suggestions">
                <p className="suggestions-label">Try asking:</p>
                <div className="suggestion-chips">
                  {suggestions.map((suggestion, idx) => (
                    <button
                      key={idx}
                      className="suggestion-chip"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`message ${message.role} ${message.isError ? 'error' : ''} animate-slideUp`}
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                <div className="message-avatar">
                  {message.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  
                  {/* Citations */}
                  {message.citations && message.citations.length > 0 && (
                    <div className="message-citations">
                      <div className="citations-header">
                        <DocumentIcon /> Sources:
                      </div>
                      <div className="citations-list">
                        {message.citations.map((citation, cidx) => (
                          <div key={cidx} className="citation">
                            <div className="citation-source">
                              {citation.document_name}
                              {citation.page_number && ` (Page ${citation.page_number})`}
                            </div>
                            <div className="citation-score">
                              Relevance: {Math.round(citation.relevance_score * 100)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Feedback Buttons */}
                  {message.role === 'assistant' && !message.isError && (
                    <div className="message-feedback">
                      {message.feedbackGiven ? (
                        <span className="feedback-thanks">
                          Thanks for your feedback! 
                          {message.feedbackGiven === 'positive' ? ' 👍' : ' 👎'}
                        </span>
                      ) : (
                        <>
                          <button
                            className="feedback-btn"
                            onClick={() => handleFeedback(idx, true)}
                            title="Helpful"
                          >
                            <ThumbsUp />
                          </button>
                          <button
                            className="feedback-btn"
                            onClick={() => handleFeedback(idx, false)}
                            title="Not helpful"
                          >
                            <ThumbsDown />
                          </button>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="message assistant loading animate-slideUp">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <LoadingDots />
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form className="chat-input-container" onSubmit={handleSubmit}>
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? <div className="spinner small" /> : <SendIcon />}
          </button>
        </div>
        <p className="input-hint">
          Press Enter to send • Shift+Enter for new line
        </p>
      </form>
    </div>
  );
};

export default ChatInterface;
