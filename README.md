# Leasa - AI Real Estate Agent

Leasa is an AI-powered real estate agent application that connects landlords with tenants. It uses Gemini 2.0 to understand natural language queries and match properties with tenant requirements.

## Features

### For Landlords
- List properties with detailed descriptions
- Specify tenant preferences and requirements
- AI-powered matching with suitable tenants

### For Tenants
- Chat with an AI agent to find suitable properties
- Ask questions about properties, locations, and neighborhoods
- Get personalized property recommendations

## Project Structure

The project consists of two main parts:

1. **Backend**: FastAPI server with Gemini 2.0 integration
2. **Frontend**: React application with a user-friendly interface

## Prerequisites

- Python 3.8+ (for backend)
- Node.js 14+ (for frontend)
- Gemini API key

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install the required dependencies:
   ```
   pip install fastapi uvicorn google-generativeai pydantic
   ```

3. Set up your Gemini API key:
   ```
   # On Windows
   set GEMINI_API_KEY=your_api_key_here
   
   # On macOS/Linux
   export GEMINI_API_KEY=your_api_key_here
   ```

4. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd leasa-frontend
   ```

2. Install the required dependencies:
   ```
   npm install
   ```

3. Start the frontend development server:
   ```
   npm start
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

## Usage

### Landlord Interface
1. Navigate to the "For Landlords" section
2. Fill out the property listing form with:
   - Property address
   - Property description
   - Tenant specifications and preferences
3. Submit the form to list your property

### Tenant Interface
1. Navigate to the "For Tenants" section
2. Chat with the AI agent about your housing needs
3. Ask questions about properties and locations
4. View recommended properties that match your requirements

## Technologies Used

- **Backend**:
  - FastAPI (Python web framework)
  - Gemini 2.0 (Google's generative AI)
  - JSON files for data storage

- **Frontend**:
  - React (JavaScript library)
  - React Router (for navigation)
  - Axios (for API requests)
  - CSS (for styling)

## Limitations

This is a demo application with the following limitations:

- Uses simple JSON files for data storage instead of a database
- Limited error handling and validation
- No authentication or user management
- Placeholder images for properties

## Future Enhancements

- Add user authentication and accounts
- Implement a proper database
- Add property images and file uploads
- Integrate with maps and location services
- Add voice interaction capabilities
