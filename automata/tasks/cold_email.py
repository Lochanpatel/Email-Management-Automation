import pandas as pd
from typing import Any, Dict, List
from automata.core.task import Task
from automata.services.llm import LLMService
from automata.services.email import EmailService
import logging

logger = logging.getLogger(__name__)

class ColdEmailTask(Task):
    """Specific task implementation for sending hyper-personalized cold emails."""
    
    def __init__(self, llm_service: LLMService, email_service: EmailService, company_context: str):
        self.llm = llm_service
        self.email = email_service
        self.company_context = company_context

    @property
    def task_id(self) -> str:
        return "cold_email_campaign_v1"

    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single lead:
        1. Validates data.
        2. Generates email using LLM.
        3. Sends email.
        """
        email = item.get("Email")
        name = item.get("Name")
        
        if not email or not name:
            raise ValueError(f"Missing required lead data: {item}")
            
        logger.info(f"Generating personalized email for {name} ({email})...")
        
        # This will raise exceptions if the LLM fails, which is caught by the Engine for retries
        body = self.llm.generate_email(item, self.company_context)
        
        subject = f"{name}, quick question about {item.get('Company')}"
        
        # Send email (raises exception on failure)
        self.email.send_email(to_email=email, subject=subject, body=body)
        
        return {
            "sent_to": email,
            "subject": subject,
            "body_snippet": body[:50] + "..." if body else ""
        }

    def load_leads_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Utility to load leads from a CSV."""
        df = pd.read_csv(filepath)
        # Convert pandas NaN/NaT to None for JSON serialization compatibility
        df = df.where(pd.notnull(df), None)
        return df.to_dict('records')
