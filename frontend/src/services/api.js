const API_BASE_URL = 'http://localhost:8000';

/**
 * API Service for communicating with the UniRAG backend
 */
class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Health Check
  async getHealth() {
    return this.request('/health');
  }

  // Documents
  async uploadDocument(file, category = 'other') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const response = await fetch(`${this.baseUrl}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Upload failed');
    }

    return response.json();
  }

  async getDocuments(category = null) {
    const params = category ? `?category=${category}` : '';
    return this.request(`/api/documents/${params}`);
  }

  async deleteDocument(documentId) {
    return this.request(`/api/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  async getCategories() {
    return this.request('/api/documents/categories');
  }

  // Chat
  async sendMessage(message, conversationId = null, categoryFilter = null) {
    const body = {
      message,
      conversation_id: conversationId,
      category_filter: categoryFilter,
    };

    return this.request('/api/chat/', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getConversationHistory(conversationId) {
    return this.request(`/api/chat/history/${conversationId}`);
  }

  async getConversations() {
    return this.request('/api/chat/conversations');
  }

  async deleteConversation(conversationId) {
    return this.request(`/api/chat/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }

  async submitFeedback(conversationId, messageIndex, isHelpful, feedbackText = null) {
    return this.request('/api/chat/feedback', {
      method: 'POST',
      body: JSON.stringify({
        conversation_id: conversationId,
        message_index: messageIndex,
        is_helpful: isHelpful,
        feedback_text: feedbackText,
      }),
    });
  }

  async getSuggestions() {
    return this.request('/api/chat/suggestions');
  }
}

export const api = new ApiService();
export default api;
