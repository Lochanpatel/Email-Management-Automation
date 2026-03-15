import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    def send_email(self, to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
        """Sends an email via SMTP or logs if dry_run."""
        if self.dry_run:
            logger.info(f"\\n[DRY RUN] Would send email to: {to_email}")
            logger.info(f"[DRY RUN] Subject: {subject}")
            logger.info(f"[DRY RUN] Body: \\n{body}\\n")
            if attachment_path:
                logger.info(f"[DRY RUN] Attachment: {attachment_path}")
            return True
            
        if not all([self.smtp_user, self.smtp_password]):
            logger.error("SMTP credentials missing. Cannot send real email.")
            raise ValueError("SMTP credentials missing.")

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}",
                )
                msg.attach(part)
            elif attachment_path:
                logger.warning(f"Attachment not found at path: {attachment_path}")

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise e
