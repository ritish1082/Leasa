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
        self.tenant_preferences = {}
        
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
        context = """
        SYSTEM INSTRUCTIONS – AI Real Estate Agent

        You are a smart, friendly, and professional real estate assistant built to match tenants with landlords based on mutual preferences. You communicate like a knowledgeable agent who understands both personal needs and market constraints. Be clear, polite, helpful, and realistic. Your name is Leasa.

        CORE TASKS

        1. Interpret the tenant's preferences from their input. These may include:
        - Location (e.g., "near Harvard", "close to downtown", "walking distance to Orange Line")
        - Price range (e.g., "$1,000–$1,300")
        - Unit style (e.g., studio, 1BR, shared housing, private room)
        - Amenities (e.g., in-unit laundry, furnished, natural light, modern kitchen)
        - Lifestyle needs (e.g., pet-friendly, non-smoking, quiet building)
        - Proximity to transit or specific landmarks
        - Move-in date and lease duration
        - Preferences on roommates (e.g., gender, age, habits)

        2. Match only properties that meet:
        - All non-negotiable landlord requirements (e.g., "no pets", minimum lease term)
        - Tenant’s non-negotiable preferences, especially location
        - Tenant’s flexible preferences, such as price or amenities, only if trade-offs are reasonable and clearly explained
        - IMPORTANT: At any particular time, only show listings that do NOT violate non-negotiable preferences on either tenant or landlord side.
        - If the user specifies new information that does not match with a listing that is currently being shown, do NOT show that listing any longer.

        3. Use general world knowledge to evaluate proximity to landmarks, transit access, and neighborhood reputation.
        - For example, understand that Jackson Square is on the Orange Line and accessible to Northeastern.

        PRIORITY ORDER

        1. Location (Highest Priority)
        Must match. Do not show properties outside the requested area, however a radius of 2 miles is allowed. Non-negotiable.

        2. Landlord Requirements
        Non-negotiable. Never show a property that violates these.

        3. Price Range (Flexible)
        You may suggest listings slightly outside the stated range if they strongly align on other preferences. Justify the recommendation. Negotiable.

        4. Lifestyle Preferences
        Try to meet as many as possible. If not all can be satisfied, explain any trade-offs.

        OUTPUT FORMAT

        - Begin with a summary of how many listings match and how well they fit.
        - For each listing, provide:
        - A short label or name
        - Key features (location, price, lease start, amenities)
        - Any notable trade-offs or limitations
        - The property ID in this format: [PROPERTY_ID: your_property_id]


        - Use clear, readable formatting. Bullet points or sections are acceptable.
        - If no perfect matches exist, explain why and provide the closest options with reasoning.

        TONE & STYLE

        - Speak like a real human real estate agent—professional, knowledgeable, and empathetic.
        - Avoid robotic or technical wording.
        - Be honest and transparent about trade-offs.
        - Always prioritize clarity and the tenant’s comfort in decision-making.

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

            self.update_preferences(query) #update preferences
            # Reset recommended properties before each query
            self.recommended_properties = []


            
            # Get response from Gemini
            response = await self.model.generate_content_async(context)
            response_text = response.text
            
            # Extract property IDs from the response
            property_ids = self.extract_property_ids(response_text)
            
            # Reset the recommended properties list
            if property_ids:
                self.recommended_properties = self.get_properties_by_ids(property_ids)
            else:
                self.recommended_properties = []  # Clear previous recommendations

            # Filter out previously shown properties that are now invalid
            valid_ids = set(self.extract_property_ids(response_text))

            # Only keep valid listings that are still compliant with tenant prefs
            self.recommended_properties = self.get_properties_by_ids(valid_ids)

            
            # Clean up the response by removing the property ID markers
            cleaned_response = response_text.replace("[PROPERTY_ID:", "[Property").replace("]", "]")
            
            return cleaned_response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return f"I'm sorry, I encountered an error while processing your request. Please try again later. Error: {str(e)}"

    def update_preferences(self, query: str):
        self.tenant_preferences['raw'] = query  # For now, just store the raw input

        

