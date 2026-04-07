# AIntropy - Cold Email Automation Framework

This project implements a scalable, resilient task execution framework to automate cold email outreach. It is built to answer the AIntropy interview request for an automation script that replaces a daily routine.

## Architecture

The system is decoupled into three layers:
1. **Core:** `engine.py`, `state.py`, `task.py` abstract away retry logic, caching, and state management (using SQLite).
2. **Services:** `llm.py` and `email.py` wrap external APIs (Google Gemini and SMTP).
3. **Tasks:** `cold_email.py` implements the specific business logic for reading leads, generating personalized content, and sending emails.

## Execution

Ensure you have Python 3 installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

To run a safe test without sending real emails (this runs entirely locally and logs what would be sent):
```bash
python main.py --dry-run
