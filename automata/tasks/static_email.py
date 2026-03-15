import pandas as pd
from typing import Any, Dict, List
from automata.core.task import Task
from automata.services.email import EmailService
import logging

logger = logging.getLogger(__name__)

class StaticEmailTask(Task):
    """Specific task implementation for sending a predefined static email with an attachment."""
    
    def __init__(self, email_service: EmailService, subject: str, body: str, attachment_path: str = None):
        self.email = email_service
        self.subject = subject
        self.body = body
        self.attachment_path = attachment_path

    @property
    def task_id(self) -> str:
        return "custom_static_email_v1"

    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single lead:
        1. Validates data.
        2. Sends the static email.
        """
        email = item.get("Email")
        name = item.get("Name")
        
        if not email:
            raise ValueError(f"Missing required email address in lead data: {item}")
            
        logger.info(f"Sending static email to {name} ({email})...")
        
        # Send email (raises exception on failure)
        self.email.send_email(to_email=email, subject=self.subject, body=self.body, attachment_path=self.attachment_path)
        
        return {
            "sent_to": email,
            "subject": self.subject,
        }

    def load_leads_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Utility to load leads from a CSV."""
        df = pd.read_csv(filepath)
        df = df.where(pd.notnull(df), None)
        return df.to_dict('records')
