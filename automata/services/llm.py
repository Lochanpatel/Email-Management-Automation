import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # We assume the environment variable GEMINI_API_KEY is set.
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. LLM generation may run in mock mode if it fails.")
        try:
            # The client picks up GEMINI_API_KEY automatically
            self.client = genai.Client()
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini Client: {e}")
            self.client = None

    def generate_email(self, lead_data: dict, company_context: str) -> str:
        """Generates a hyper-personalized email given lead info and company context."""
        
        prompt = f"""
        You are an expert sales development representative.
        Write a hyper-personalized, short, and engaging cold email for the following lead.
        
        Lead Details:
        Name: {lead_data.get('Name')}
        Company: {lead_data.get('Company')}
        Role: {lead_data.get('Role')}
        Recent News/Context: {lead_data.get('Context')}
        
        Our Company/Product Context:
        {company_context}
        
        Guidelines:
        - Keep it under 150 words.
        - Start with a personalized hook based on their Recent News or Role.
        - Focus on value, not features.
        - End with a soft call to action.
        - Do not include placeholders like [Your Name]. Just give me the body of the email.
        """
        
        if not self.client:
            logger.info("Mock LLM generation due to missing client.")
            return f"Hi {lead_data.get('Name')},\\n\\nI noticed your work at {lead_data.get('Company')} and think our product could help. Let's chat!\\n\\nBest,\\nSales"
            
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating email from LLM: {e}")
            raise e
