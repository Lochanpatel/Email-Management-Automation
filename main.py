import os
import argparse
import logging
from dotenv import load_dotenv

from automata.core.state import StateManager
from automata.core.engine import TaskEngine
from automata.services.email import EmailService
from automata.tasks.static_email import StaticEmailTask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Static Cold Emailing with Attachment")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending actual emails. Defaults to true.", default=True)
    parser.add_argument("--send-real", dest="dry_run", action="store_false", help="Send actual emails via SMTP")
    parser.add_argument("--leads-csv", type=str, default="data/leads.csv", help="Path to leads CSV file")
    parser.add_argument("--attachment", type=str, required=False, help="Path to attachment (e.g. resume.pdf)")
    args = parser.parse_args()

    load_dotenv()

    logger.info("Starting Automation Workflow (Static Email Model)...")
    if args.dry_run:
        logger.info("Running in DRY RUN mode. No real emails will be sent.")

    # 1. Initialize Core Framework
    state_manager = StateManager()  # Connects to SAMSUNG\sqlexpress SQL Server
    engine = TaskEngine(state_manager=state_manager)

    # 2. Initialize Services
    email_service = EmailService(dry_run=args.dry_run)

    body = """Hello,
I am writing to apply for the Software Engineer position.

I am a B.Tech student (2026) with a strong foundation in Data Structures and Algorithms, Object-Oriented Programming, and Web Development. I have hands-on experience building projects and enjoy working on real-world problems and scalable applications.

I’m currently holding two offers from service-based companies, but my goal is to start my career in a strong product-based engineering environment where I can properly learn system design, code quality, and real development practices. Because of that, I’ve decided to keep improving my skills rather than rushing into a role that won’t help me grow as a developer.

Please find my resume attached and my GitHub project link shared below for your reference:

GitHub: https://github.com/Lochanpatel
LeetCode: https://leetcode.com/u/lochanpatelmp/

Thank you for considering my application.

Lochan Patel
patellochan31@gmail.com
7566039795"""

    # 3. Initialize Specific Task
    static_email_task = StaticEmailTask(
        email_service=email_service,
        subject="Application for Software Engineer - Lochan Patel",
        body=body,
        attachment_path=args.attachment
    )

    # 4. Load Data
    try:
        leads = static_email_task.load_leads_from_csv(args.leads_csv)
    except Exception as e:
        logger.error(f"Failed to load leads: {e}")
        return

    logger.info(f"Loaded {len(leads)} leads from {args.leads_csv}")

    # 5. Execute Batch
    stats = engine.run_batch(
        task_id=static_email_task.task_id,
        items=leads,
        process_func=static_email_task.process_item,
        id_extractor=lambda item: item["Email"],
        max_retries=3,
        retry_delay=2.0
    )

    logger.info(f"Workflow Finished. Execution Stats: {stats}")

if __name__ == "__main__":
    main()
