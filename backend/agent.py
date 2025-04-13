import os
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")

# Initialize the Gemini client
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash"  # Using the latest stable model

class RealEstateAgent:
    def __init__(self, properties_data: List[Dict[str, Any]]):
        self.properties = properties_data
        # Simple in-memory array for conversation - resets when agent is recreated
        self.conversation = []
        self.recommended_properties = []
        
        # Set up Google Search tool
        self.google_search_tool = Tool(
            google_search=GoogleSearch()
        )
    
    def build_context(self, query: str) -> str:
        """Build a concise, sales-driven context for the Gemini model."""
        context = """
You are Leasa, a real estate voice agent. Keep responses under 40 words. Be warm and conversational.

For first-time users, only introduce yourself as Leasa and ask how you can help with their property search. Don't show listings in the first conversation.

Be logical and relevant - only suggest properties in locations the user specifically asks for. Never suggest properties in different cities or areas than requested.

For follow-up messages, respond directly to queries with matching properties.
Highlight one key benefit per property. Use natural speech patterns suitable for voice.
        """
        # Add available property details
        if self.properties:
            context += "\n\nAVAILABLE PROPERTIES:\n"
            for prop in self.properties:
                context += f"- {prop.get('address')} | ${prop.get('price')} | {prop.get('description')} | [PROPERTY_ID: {prop.get('id')}]\n"
        else:
            context += "\n\nNo available properties at the moment.\n"
        
        # Add conversation context if there is any history
        if self.conversation:
            context += "\n\nCONVERSATION HISTORY:\n"
            for entry in self.conversation:
                context += f"User: {entry['user']}\n"
                if entry.get('agent'):
                    context += f"Agent: {entry['agent']}\n"
        
        # Add current user query
        context += f"\n\nCURRENT QUERY:\n{query.strip()}\n"

        return context
    
    def extract_property_ids(self, response: str) -> List[str]:
        """Extract property IDs from the response."""
        # Look for property IDs in the format [PROPERTY_ID: prop_id]
        pattern = r'\[PROPERTY_ID:\s*([^\]]+)\]'
        matches = re.findall(pattern, response)
        
        # Return unique property IDs
        return list(set(matches))
    
    def get_properties_by_ids(self, property_ids: List[str]) -> List[Dict[str, Any]]:
        """Get property details by IDs."""
        recommended = []
        for prop_id in property_ids:
            for prop in self.properties:
                if prop.get("id") == prop_id:
                    recommended.append(prop)
        return recommended
    
    # This is a synchronous method that will be used by the async process_query
    def _process_query_sync(self, query: str) -> str:
        """Internal synchronous implementation of query processing."""
        try:
            # Store user query in conversation history
            self.conversation.append({"user": query})
            
            # Build the context for the model
            context = self.build_context(query)
            
            # Reset recommended properties before each query
            self.recommended_properties = []
            
            # Use the synchronous interface for model generation
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=context,
                config=GenerateContentConfig(
                    tools=[self.google_search_tool],
                    response_modalities=["TEXT"],
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            # Extract the response text
            response_text = response.text
            
            # Store agent response in conversation history
            self.conversation[-1]["agent"] = response_text
            
            # Extract property IDs from the response
            property_ids = self.extract_property_ids(response_text)
            
            # Update recommended properties
            if property_ids:
                self.recommended_properties = self.get_properties_by_ids(property_ids)
            
            # Clean up the response by removing the property ID markers
            cleaned_response = response_text.replace("[PROPERTY_ID:", "[Property").replace("]", "]")
            
            return cleaned_response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return f"I'm sorry, I encountered an error while processing your request. Please try again later. Error: {str(e)}"
    
    # Keep the async method signature for FastAPI compatibility
    async def process_query(self, query: str) -> str:
        """Process a query from a tenant and return a response.
        This is an async wrapper around the synchronous implementation.
        """
        # Call the synchronous implementation directly, no await needed
        return self._process_query_sync(query)
        
    def clear_conversation(self):
        """Clear the conversation history to start fresh."""
        self.conversation = []
        self.recommended_properties = []