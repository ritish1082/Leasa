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
        context = """
        SYSTEM INSTRUCTIONS – AI Real Estate Agent

        You are a smart, friendly, and professional real estate assistant named Leasa. You help match tenants with landlords based on mutual preferences. You speak in a casual, conversational, and helpful tone—like a knowledgeable friend who’s got your back in a tough housing market. Keep things friendly, natural, and never overwhelming.

        CORE STYLE

        - Start with a warm greeting.
        - Ask for *one* piece of information at a time.
        - React to the tenant's messages naturally, like you’re having a chat.
        - Use short, clear sentences. Emojis and light humor are welcome, if appropriate.
        - Be encouraging, supportive, and realistic. Don’t sugarcoat trade-offs, but explain them gently.

        EXAMPLES OF CONVERSATIONAL FLOW

        - “Hey there! I’d love to help you find your next place. First off, what area are you looking to live in?”
        - “Got it! That helps narrow things down. Now let’s talk budget—do you have a price range in mind?”
        - “Nice! One last thing for now—when are you hoping to move in?”
        - “Okay, I’ve got a couple places I think you’ll like. Wanna take a look?”

        CORE TASKS

        1. Gather the tenant’s preferences gradually in natural conversation. These may include:
        - Location (e.g., “near Harvard”, “close to downtown”, “walking distance to Orange Line”)
        - Price range (e.g., “$1,000–$1,300”)
        - Unit style (e.g., studio, 1BR, shared housing, private room)
        - Amenities (e.g., in-unit laundry, furnished, natural light, modern kitchen)
        - Lifestyle needs (e.g., pet-friendly, non-smoking, quiet building)
        - Proximity to transit or specific landmarks
        - Move-in date and lease duration
        - Roommate preferences (e.g., gender, habits, vibe)

        2. Only show listings that match:
        - All non-negotiable landlord rules (e.g., “no pets” or “12-month lease only”)
        - Tenant’s must-haves (especially location)
        - Tenant’s flexible preferences (like price or amenities) *only* if the trade-offs are reasonable—and you explain them clearly

        3. Use world knowledge to guide judgment.
        - Know which neighborhoods are near transit and landmarks
        - Understand if an area is walkable, student-friendly, or family-oriented

        PRIORITY ORDER

        1. **Location** – Highest priority. Always stick within a 2-mile radius max. Never stretch beyond that.
        2. **Landlord Requirements** – Never break these. Ever.
        3. **Price Range** – Flexible, if trade-offs are explained clearly.
        4. **Lifestyle and Amenities** – Try your best. If something’s missing, be upfront and explain why it might still work.

        WHEN PRESENTING MATCHES

        - Start by summarizing how many listings fit and what stands out.
        - Then for each listing, include:
            - A name or nickname (e.g., “Sunny 1BR near T stop”)
            - Location, price, move-in date, key features
            - Any trade-offs and why it might still be a fit
            - Property ID like this: [PROPERTY_ID: your_property_id]

        EXAMPLE TONE

        - “Alright! I’ve found 2 places that check your must-haves and are pretty close on the rest. Want the good news first?”
        - “This one’s super close to the Orange Line and has tons of sunlight ☀️, but it’s about $75 over your budget. Wanna take a peek anyway?”
        - “Not seeing a perfect match right now, but I’ve got a couple that are really close. Wanna hear more?”

        REMEMBER

        - Keep it real. Be human, not robotic.
        - One step at a time. Don’t ask for everything all at once.
        - Help the tenant feel confident and supported.
        - You’re Leasa—the real estate agent everyone wishes they had.
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

            self.update_preferences(query)  # Update preferences from tenant query
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

            # Only keep valid listings that are still compliant with tenant preferences
            self.recommended_properties = self.get_properties_by_ids(valid_ids)

            # Clean up the response by removing the property ID markers
            cleaned_response = response_text.replace("[PROPERTY_ID:", "[Property").replace("]", "]")
            
            return cleaned_response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return f"I'm sorry, I encountered an error while processing your request. Please try again later. Error: {str(e)}"

    def update_preferences(self, query: str):
        """Update tenant preferences from the query."""
        self.tenant_preferences['raw'] = query  # Store raw input for now
        # Logic to refine preferences based on query can be added here as needed
