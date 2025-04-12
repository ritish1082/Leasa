import { useState, useEffect, useRef } from 'react';
import { sendChatMessage } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [properties, setProperties] = useState([]);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      
      // Add error message
      const errorMessage = {
        content: 'Sorry, there was an error processing your request. Please try again.',
        role: 'system',
        timestamp: new Date().toISOString(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Chat with Leasa</h2>
        <p>Your AI Real Estate Agent</p>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>Welcome to Leasa!</h3>
            <p>
              I'm your AI real estate agent. How can I help you find your perfect property today?
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.role === 'user' ? 'user-message' : 'agent-message'}`}
            >
              <div className="message-content">{msg.content}</div>
              <div className="message-timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message here..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
      
      {properties.length > 0 && (
        <div className="recommended-properties">
          <h3>Recommended Properties</h3>
          <div className="properties-list">
            {properties.map((property) => (
              <div key={property.id} className="property-item">
                <h4>{property.address}</h4>
                <p>{property.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
