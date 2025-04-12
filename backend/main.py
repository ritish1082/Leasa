from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from typing import List, Optional
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the AI agent
from agent import RealEstateAgent

app = FastAPI(title="Leasa - AI Real Estate Agent")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class PropertyBase(BaseModel):
    address: str
    description: str
    specifications: str

class PropertyCreate(PropertyBase):
    pass

class Property(PropertyBase):
    id: str
    created_at: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    properties: Optional[List[Property]] = None

# File paths
PROPERTIES_FILE = "backend/data/properties.json"
CHATS_FILE = "backend/data/chats.json"

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists("backend/data"):
        os.makedirs("backend/data")
    
    if not os.path.exists(PROPERTIES_FILE):
        with open(PROPERTIES_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, "w") as f:
            json.dump({}, f)

initialize_data_files()

# Load properties
def load_properties():
    try:
        with open(PROPERTIES_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Save properties
def save_properties(properties):
    with open(PROPERTIES_FILE, "w") as f:
        json.dump(properties, f, indent=2)

# Load chats
def load_chats():
    try:
        with open(CHATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Save chats
def save_chats(chats):
    with open(CHATS_FILE, "w") as f:
        json.dump(chats, f, indent=2)

# Initialize the AI agent
agent = RealEstateAgent(load_properties())

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to Leasa - AI Real Estate Agent API"}

@app.get("/properties", response_model=List[Property])
def get_properties():
    return load_properties()

@app.post("/properties", response_model=Property)
def create_property(property_data: PropertyCreate):
    properties = load_properties()
    
    new_property = {
        "id": str(uuid.uuid4()),
        "address": property_data.address,
        "description": property_data.description,
        "specifications": property_data.specifications,
        "created_at": datetime.now().isoformat()
    }
    
    properties.append(new_property)
    save_properties(properties)
    
    # Update the agent with the new properties
    agent.properties = properties
    
    return new_property

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    # Load existing chats
    chats = load_chats()
    
    # Create a new session if none provided
    session_id = chat_message.session_id or str(uuid.uuid4())
    
    # Initialize session if it doesn't exist
    if session_id not in chats:
        chats[session_id] = []
    
    # Add user message to history
    chats[session_id].append({
        "role": "user",
        "content": chat_message.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Process the message with the AI agent
    agent.conversation_history = chats[session_id]
    response = await agent.process_query(chat_message.message)
    
    # Add agent response to history
    chats[session_id].append({
        "role": "agent",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })
    
    # Save updated chats
    save_chats(chats)
    
    # Return the response
    return {
        "message": response,
        "session_id": session_id,
        "properties": agent.recommended_properties
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
