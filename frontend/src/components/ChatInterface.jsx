import { useState, useEffect, useRef, useCallback } from 'react';
import { sendChatMessage } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [properties, setProperties] = useState([]);
  const [errorMessage, setError] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Speech recognition
  const recognition = useRef(null);

  // Voice selection
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  // Initialize speech recognition
  useEffect(() => {
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = 'en-US';

      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        // Automatically submit after a short delay
        setTimeout(() => {
          // Create a synthetic form submission event
          const syntheticEvent = { preventDefault: () => { } };
          handleSendMessage(syntheticEvent, transcript);
        }, 500);
      };

      recognition.current.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Initialize and load available voices
  useEffect(() => {
    // Check if browser supports speech synthesis
    if ('speechSynthesis' in window) {
      // Function to get and set available voices
      const loadVoices = () => {
        // Get all available voices
        const voices = window.speechSynthesis.getVoices();

        // Filter for only female voices
        const femaleVoices = voices.filter(voice =>
          voice.name.toLowerCase().includes('female') ||
          voice.name.toLowerCase().includes('woman') ||
          voice.name.toLowerCase().includes('girl') ||
          // Some voice names don't specify gender but end with female-sounding names
          /\b(alice|anna|karen|lisa|mary|susan|victoria|zara)\b/i.test(voice.name)
        );

        setAvailableVoices(femaleVoices);

        // Set default voice - prefer English female voice if available
        if (femaleVoices.length > 0) {
          const englishFemaleVoice = femaleVoices.find(voice =>
            voice.lang.startsWith('en-')
          );

          setSelectedVoice(englishFemaleVoice || femaleVoices[0]);
        }
      };

      // Chrome loads voices asynchronously
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }

      // Initial load of voices
      loadVoices();

      // If Chrome hasn't loaded voices yet, try again after a short delay
      if (availableVoices.length === 0) {
        setTimeout(loadVoices, 200);
      }
    }
  }, []);

  // Check if browser supports speech synthesis
  const speechSynthesisSupported = 'speechSynthesis' in window;

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

  // Function to speak text
  const speakText = (text) => {
    if (speechSynthesisSupported && voiceEnabled) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      // Use the selected female voice if available
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      window.speechSynthesis.speak(utterance);
    }
  };

  // Toggle speech recognition
  const toggleListening = () => {
    if (!recognition.current) return;

    if (isListening) {
      recognition.current.stop();
      setIsListening(false);
    } else {
      recognition.current.start();
      setIsListening(true);
    }
  };

  // Toggle voice output
  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);

    // Cancel any ongoing speech when turning off
    if (voiceEnabled) {
      window.speechSynthesis.cancel();
    }
  };

  const handleSendMessage = async (e, transcribedText = null) => {
    e.preventDefault();

    // Use either transcribed text or input field value
    const messageText = transcribedText || input;

    if (!messageText.trim()) return;

    // Add user message to chat
    const userMessage = {
      content: messageText,
      role: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Send message to backend
      const response = await sendChatMessage(messageText, sessionId);

      // Save session ID for future messages
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
      }

      // Add agent response to chat
      const agentMessage = {
        content: response.message,
        role: 'agent',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, agentMessage]);

      // Speak the agent's response
      speakText(response.message);

      // Update recommended properties if any
      console.log("Properties received:", response.properties);
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
      speakText(errorMessage);
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

      // Cancel any ongoing speech
      if (speechSynthesisSupported) {
        window.speechSynthesis.cancel();
      }
    }
  };

  // Handle voice selection change
  const handleVoiceChange = (e) => {
    const voiceIndex = e.target.value;
    setSelectedVoice(availableVoices[voiceIndex]);

    // Speak a test message with the new voice
    if (voiceEnabled) {
      const testMessage = "Hello, I'm Leasa, your AI real estate agent.";
      setTimeout(() => speakText(testMessage), 100);
    }
  };

  // Format and display property details
  const PropertyCard = ({ property }) => (
    <div className="property-card">
      <h4>{property.address}</h4>
      <p className="property-price">Price: {property.price}</p>
      <p>{property.description}</p>
      {property.specifications && (
        <p className="property-specifications">
          <strong>Requirements:</strong> {property.specifications}
        </p>
      )}
    </div>
  );

  return (
    <div className="chat-container">
      <div className="chat-main">
        <div className="chat-header">
          <div className="header-title">
            <h2>Chat with Leasa</h2>
            <p>Your AI Real Estate Agent</p>
          </div>
          <div className="header-controls">
            <button
              className={`voice-toggle ${voiceEnabled ? 'enabled' : 'disabled'}`}
              onClick={toggleVoice}
              aria-label={voiceEnabled ? "Disable voice" : "Enable voice"}
              title={voiceEnabled ? "Disable voice" : "Enable voice"}
            >
              {voiceEnabled ? "🔊" : "🔇"}
            </button>

            {voiceEnabled && availableVoices.length > 1 && (
              <select
                value={availableVoices.indexOf(selectedVoice)}
                onChange={handleVoiceChange}
                className="voice-selector"
                title="Select a female voice"
              >
                {availableVoices.map((voice, index) => (
                  <option key={index} value={index}>
                    {voice.name}
                  </option>
                ))}
              </select>
            )}

            <button
              className="clear-chat-button"
              onClick={clearChat}
              aria-label="Clear chat"
            >
              Clear Chat
            </button>
          </div>
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
            disabled={loading || isListening}
            ref={inputRef}
          />
          <button
            type="button"
            className={`voice-button ${isListening ? 'listening' : ''}`}
            onClick={toggleListening}
            disabled={loading}
          >
            {isListening ? '🔴' : '🎤'}
          </button>
          <button type="submit" disabled={loading || (!input.trim() && !isListening)}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>

      <div className="chat-sidebar">
        {console.log("Properties in sidebar:", properties)}
        {properties.length > 0 ? (
          <div className="recommended-properties">
            <h3>Recommended Properties</h3>
            <div className="properties-list">
              {properties.map((property) => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
          </div>
        ) : (
          <div className="no-properties-sidebar">
            <h3>Property Recommendations</h3>
            <p>As you chat, property recommendations will appear here based on your preferences.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
