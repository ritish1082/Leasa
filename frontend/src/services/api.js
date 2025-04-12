import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getProperties = async () => {
  try {
    const response = await api.get('/properties');
    return response.data;
  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
};

export const createProperty = async (propertyData) => {
  try {
    const response = await api.post('/properties', propertyData);
    return response.data;
  } catch (error) {
    console.error('Error creating property:', error);
    throw error;
  }
};

export const sendChatMessage = async (message, sessionId = null) => {
  try {
    const response = await api.post('/chat', { message, session_id: sessionId });
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};
