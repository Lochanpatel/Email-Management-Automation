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
