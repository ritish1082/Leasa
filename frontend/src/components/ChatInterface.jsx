import { useState, useEffect, useRef, useCallback } from 'react';
import { sendChatMessage } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [properties, setProperties] = useState([]);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Focus input field when component loads
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      content: input,
      role: 'user',
      timestamp: new Date().toISOString(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);
    
    // Reset properties before making a new request
    setProperties([]);
    
    try {
      // Send message to backend
      const response = await sendChatMessage(input, sessionId);
      
      // Save session ID for future messages
      if (!sessionId) {
        setSessionId(response.session_id);
      }
      
      // Add agent response to chat
      const agentMessage = {
        content: response.message,
        role: 'agent',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, agentMessage]);
      
      // Update recommended properties if any
      if (response.properties && response.properties.length > 0) {
        setProperties(response.properties);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      let errorMessage = 'Sorry, there was an error processing your request. Please try again.';
      
      // Customize error message based on error type
      if (error.message === 'Network Error') {
        errorMessage = 'Unable to connect to the server. Please check your internet connection.';
      } else if (error.response && error.response.status === 429) {
        errorMessage = 'You\'ve sent too many messages. Please wait a moment and try again.';
      }
      
      setError(errorMessage);
      
      // Add error message to chat
      const errorMsg = {
        content: errorMessage,
        role: 'system',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      // Focus back on input after sending
      inputRef.current?.focus();
    }
  };
  
  const clearChat = () => {
    if (window.confirm('Are you sure you want to clear this conversation?')) {
      setMessages([]);
      setProperties([]);
      // Session ID is kept to maintain context with the backend
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-title">
          <h2>Chat with Leasa</h2>
          <p>Your AI Real Estate Agent</p>
        </div>
        {messages.length > 0 && (
          <button 
            className="clear-chat-btn" 
            onClick={clearChat}
            aria-label="Clear conversation"
          >
            Clear Chat
          </button>
        )}
      </div>
      
      <div className="chat-messages" aria-live="polite">
        {messages.length === 0 ? (
          <div className="welcome-message" role="status">
            <h3>Welcome to Leasa!</h3>
            <p>
              I'm your AI real estate agent. How can I help you find your perfect property today?
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role === 'user' ? 'user-message' : 
                          msg.role === 'system' ? 'system-message' : 'agent-message'}`}
              role={msg.role === 'system' ? 'alert' : 'log'}
            >
              <div className="message-content">{msg.content}</div>
              <div className="message-timestamp" aria-label={`Sent at ${new Date(msg.timestamp).toLocaleTimeString()}`}>
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message agent-message typing-indicator" role="status" aria-label="Leasa is typing">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message here..."
          disabled={loading}
          aria-label="Message input"
        />
        <button 
          type="submit" 
          disabled={loading || !input.trim()}
          aria-label="Send message"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
      
      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
      
      {properties.length > 0 && (
        <div className="recommended-properties" aria-label="Recommended properties">
          <h3>Recommended Properties</h3>
          <div className="properties-list">
            {properties.map((property) => (
              <div key={property.id} className="property-item" tabIndex="0">
                <h4>{property.address}</h4>
                <p>{property.description}</p>
                {property.price && <p className="property-price">${property.price.toLocaleString()}</p>}
                <button className="property-details-btn" aria-label={`View details for ${property.address}`}>
                  View Details
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;