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
```

## Interview Questions Addressed

### 1. What failure cases have you run into and how did you handle them?
- **Restarts & Duplicate Execution:** If the script crashes halfway through a list of 1,000 leads, we do not want to re-email the first 500 when we restart. *Solution:* Implemented `StateManager` using SQLite. Before processing any item, the engine checks if its status is `COMPLETED`.
- **API Flakes / Rate Limits:** LLMs and SMTP servers often timeout or reject requests. *Solution:* The `TaskEngine` has a built-in retry mechanism with a backoff delay, separating transient failures from permanent ones.
- **Missing API Keys:** If the Google Gemini key is missing, the LLM service catches the lack of a client and elegantly falls back to a mock template rather than crashing the whole pipeline.

### 2. How did you organize your code and how would it scale if you have to automate 10 more tasks?
The code is deliberately structured out of monolithic scripts into a **Core Framework**. 
- To add 10 more tasks (e.g., `LinkedInScraperTask`, `CRMUpdaterTask`), you simply create 10 new classes inheriting from the abstract base `Task` class. 
- The `TaskEngine` works agnostically—you simply pass it any task ID, a list of items, and a processing function—it then handles the retries and state management automatically for any new workflow.

### 3. What alternative approaches did you consider?
- **No-Code Tools (Make/Zapier):** Great for simple triggers, but debugging complex nested loops or custom state/retry logic becomes visually cumbersome. Version control and code-reviewing is also difficult.
- **Off-the-shelf Platforms (Instantly/Apollo):** Excellent for pure cold email, but not extensible. If we wanted to add a step that texts a user or updates an internal proprietary database before emailing, we'd hit platform limitations.
- **Monolithic Script:** A single `script.py` with 500 lines of code. Quick to write, but impossible to test properly or reuse components (like the LLM generator) for other tasks.

### 4. How easy is it to adapt your automation for a team rather than you as an individual?
This framework is built to adapt to team use naturally:
- **State Management:** By changing `sqlite3` to `psycopg2` and connecting to a shared PostgreSQL database, multiple team members can run workers simultaneously without stepping on each other's toes.
- **Configuration:** Secrets are pulled from `.env` instead of hardcoded strings, making it trivial to migrate to AWS Secrets Manager or HashiCorp Vault when deploying to a team server.
- **Observability:** Centralized logging via the `logging` module can easily be piped to Datadog or an ELK stack so non-engineers can view success/failure rates on a shared dashboard.
