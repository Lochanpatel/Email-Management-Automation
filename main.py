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
    parser = argparse.ArgumentParser(description="Cold Emailing Automation - Personalized, Multi-Recipient")
    parser.add_argument("--dry-run",   action="store_true", default=True,
                        help="Log emails without actually sending (safe mode). Default: ON")
    parser.add_argument("--send-real", dest="dry_run", action="store_false",
                        help="Send real emails via SMTP")
    parser.add_argument("--leads",     type=str, default="data/leads.xlsx",
                        help="Path to leads file (.xlsx or .csv). Default: data/leads.xlsx")
    parser.add_argument("--attachment", type=str, required=False,
                        help="Optional path to a file attachment (e.g. resume.pdf)")
    args = parser.parse_args()

    load_dotenv()

    logger.info("Starting Automation Workflow...")
    if args.dry_run:
        logger.info("DRY RUN mode — no real emails will be sent.")

    # 1. Core Framework (SQL Server state — prevents double-sending)
    state_manager = StateManager()
    engine = TaskEngine(state_manager=state_manager)

    # 2. Services
    email_service = EmailService(dry_run=args.dry_run)

    # -------------------------------------------------------------------------
    # EMAIL TEMPLATE
    # Use {ColumnName} to personalise using columns from your Excel/CSV sheet.
    # Example columns: Name, Company, Role, HiringManagerName
    # -------------------------------------------------------------------------
    subject = "Application for Software Engineer - Lochan Patel"

    body = """Dear {Name},

I am writing to apply for the Software Engineer position at {Company}.

I am a B.Tech student (2026) with a strong foundation in Data Structures and Algorithms, Object-Oriented Programming, and Web Development. I have hands-on experience building projects and enjoy working on real-world problems and scalable applications.

I'm currently holding two offers from service-based companies, but my goal is to start my career in a strong product-based engineering environment — like {Company} — where I can properly learn system design, code quality, and real development practices.

Please find my resume attached and my GitHub project link shared below:

GitHub:   https://github.com/Lochanpatel
LeetCode: https://leetcode.com/u/lochanpatelmp/

Thank you for considering my application, {Name}.

Best regards,
Lochan Patel
patellochan31@gmail.com | 7566039795"""

    # 3. Task
    task = StaticEmailTask(
        email_service=email_service,
        subject=subject,
        body=body,
        attachment_path=args.attachment
    )

    # 4. Load leads from Excel or CSV
    try:
        leads = task.load_leads(args.leads)
    except Exception as e:
        logger.error(f"Failed to load leads from '{args.leads}': {e}")
        return

    logger.info(f"Loaded {len(leads)} leads from: {args.leads}")

    # 5. Run batch (auto-skips already-sent emails using SQL Server state)
    stats = engine.run_batch(
        task_id=task.task_id,
        items=leads,
        process_func=task.process_item,
        id_extractor=lambda item: item["Email"],
        max_retries=3,
        retry_delay=2.0
    )

    logger.info(f"Workflow Finished. Stats: {stats}")

if __name__ == "__main__":
    main()
