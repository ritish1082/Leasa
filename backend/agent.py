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
        - “Okay, I’ve got a couple places I think you’ll like."
        - If you find an available listing, SHOW THE LISTING CARD

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

        4. If a listing matches at any given time, SHOW THE LISTING CARD

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