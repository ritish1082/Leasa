import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")
genai.configure(api_key=API_KEY)

class RealEstateAgent:
    def __init__(self, properties_data: List[Dict[str, Any]]):
        self.properties = properties_data
        self.conversation_history = []
        self.recommended_properties = []
        
        # Initialize the Gemini model
        try:
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest",
                generation_config=GenerationConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            # Fallback to a different model if gemini-flash-2.0 is not available
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest",
                generation_config=GenerationConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
    
    def build_context(self, query: str) -> str:
        """Build a rich context for the Gemini model."""
#         context = """You are Leasa, an AI real estate agent. Your goal is to help tenants find suitable properties based on their requirements and landlord preferences.

# SYSTEM INSTRUCTIONS:
# 1. Be helpful, professional, and knowledgeable about real estate.
# 2. Use your knowledge about locations, neighborhoods, and real estate to answer questions.
# 3. If asked about distances, nearby places, or neighborhood features, provide helpful information based on the property locations.
# 4. Only recommend properties that match both the tenant's requirements AND the landlord's specifications.
# 5. If no properties match the requirements, explain why and suggest alternatives.
# 6. When recommending properties, include their IDs in your response in the format [PROPERTY_ID: prop_id].
# 7. Be conversational but professional, like a real estate agent would be.

# """
        context = """You are Leasa, an advanced AI real estate agent. You are helping a tenant find suitable properties based on their preferences and landlord specifications.

        You have access to:
        - A list of available properties, including their full addresses.
        - Your own extensive knowledge of geography, neighborhoods, cities, distances between locations, commute times, and local amenities.

        SYSTEM INSTRUCTIONS:
        1. Use your own world knowledge to evaluate how far properties are from popular landmarks or requested areas (e.g., 'near Harvard', 'close to downtown', 'walking distance to subway').
        2. Recommend only properties that meet both the tenant's criteria AND the landlord's requirements.
        3. If no properties fully match, explain why and offer alternatives that are close matches.
        4. For each recommended property, include the ID in this format: [PROPERTY_ID: property_id]
        5. Use a natural, conversational, and helpful tone—like a professional real estate agent.

        NOTE:
        - Use the full addresses in the property list to infer locations, distances, and neighborhood features.
        - Do NOT ask the user for geolocation or external data—you already know about all public places, institutions, and city layouts.
        """



        # Add properties information
        if self.properties:
            context += "AVAILABLE PROPERTIES:\n"
            for prop in self.properties:
                context += f"Property ID: {prop['id']}\n"
                context += f"Address: {prop['address']}\n"
                context += f"Description: {prop['description']}\n"
                context += f"Landlord specifications: {prop['specifications']}\n\n"
        else:
            context += "AVAILABLE PROPERTIES: No properties are currently available.\n\n"
        
        # Add conversation history
        if self.conversation_history:
            context += "CONVERSATION HISTORY:\n"
            for message in self.conversation_history:
                if message.get("role") and message.get("content"):
                    context += f"{message['role'].capitalize()}: {message['content']}\n"
        
        # Add current query
        context += f"\nCURRENT QUERY:\nUser: {query}\n\n"
        
        return context
    
    def extract_property_ids(self, response: str) -> List[str]:
        """Extract property IDs from the response."""
        import re
        
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
    
    async def process_query(self, query: str) -> str:
        """Process a query from a tenant and return a response."""
        try:
            # Build the context for the model
            context = self.build_context(query)
            
            # Get response from Gemini
            response = await self.model.generate_content_async(context)
            response_text = response.text
            
            # Extract property IDs from the response
            property_ids = self.extract_property_ids(response_text)
            
            # Get the recommended properties
            self.recommended_properties = self.get_properties_by_ids(property_ids)
            
            # Clean up the response by removing the property ID markers
            cleaned_response = response_text.replace("[PROPERTY_ID:", "[Property").replace("]", "]")
            
            return cleaned_response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return f"I'm sorry, I encountered an error while processing your request. Please try again later. Error: {str(e)}"
