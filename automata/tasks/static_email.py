import pandas as pd
from typing import Any, Dict, List, Optional
from automata.core.task import Task
from automata.services.email import EmailService
import logging
import os

logger = logging.getLogger(__name__)

class StaticEmailTask(Task):
    """
    Sends a personalized template email to multiple recipients loaded from Excel or CSV.
    
    Template variables in subject/body are filled from each row's columns.
    Example: 'Dear {Name},' becomes 'Dear Lochan,' for a row with Name=Lochan.
    """
    
    def __init__(self, email_service: EmailService, subject: str, body: str, attachment_path: Optional[str] = None):
        self.email = email_service
        self.subject = subject
        self.body = body
        self.attachment_path = attachment_path

    @property
    def task_id(self) -> str:
        return "custom_static_email_v1"

    def _render(self, template: str, item: Dict[str, Any]) -> str:
        """Fills {ColumnName} placeholders in the template with values from the lead row."""
        try:
            return template.format_map({k: (v or "") for k, v in item.items()})
        except KeyError as e:
            logger.warning(f"Template placeholder {e} not found in lead data. Leaving as-is.")
            return template

    def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single lead:
        1. Validates required fields.
        2. Renders the subject and body with lead-specific values.
        3. Sends the personalized email.
        """
        email = item.get("Email")
        name = item.get("Name", "there")

        if not email:
            raise ValueError(f"Missing Email in lead row: {item}")

        # Render personalized subject and body
        personalized_subject = self._render(self.subject, item)
        personalized_body = self._render(self.body, item)

        logger.info(f"Sending email to {name} ({email})...")

        self.email.send_email(
            to_email=email,
            subject=personalized_subject,
            body=personalized_body,
            attachment_path=self.attachment_path
        )

        return {
            "sent_to": email,
            "subject": personalized_subject,
        }

    def load_leads(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Loads leads from an Excel (.xlsx / .xls) or CSV file.
        Auto-detects format from the file extension.
        """
        ext = os.path.splitext(filepath)[1].lower()
        if ext in (".xlsx", ".xls"):
            df = pd.read_excel(filepath)
            logger.info(f"Loaded leads from Excel file: {filepath}")
        elif ext == ".csv":
            df = pd.read_csv(filepath)
            logger.info(f"Loaded leads from CSV file: {filepath}")
        else:
            raise ValueError(f"Unsupported file format: {ext}. Use .xlsx, .xls, or .csv")

        df = df.where(pd.notnull(df), None)
        return df.to_dict("records")
