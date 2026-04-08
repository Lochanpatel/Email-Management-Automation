# 📧 Email Automation Framework

> A scalable, resilient, and fully automated email outreach engine — built with Python, Google Gemini AI, and SQLite state management.

---

## 🚀 Features

- **Smart state management** — SQLite-backed deduplication prevents double-sending
- **Batch processing** — Send to hundreds of leads from Excel or CSV files
- **Personalized content** — Use `{ColumnName}` placeholders mapped directly to your spreadsheet columns
- **LLM-powered generation** — Integrated Google Gemini AI for dynamic email body creation
- **File attachments** — Securely attach resumes or documents to every outgoing email
- **Dry-run / Safe mode** — Test your entire pipeline without sending a single real email
- **Auto-retry logic** — Configurable retries with delay for resilient dispatch
- **Force re-send** — Override existing state and re-process all leads when needed

---

## 🏗️ Architecture

The system is cleanly decoupled into three layers:

```
cold-emailing-automation/
├── automata/
│   ├── core/
│   │   ├── engine.py       # Task orchestration, batching & retry logic
│   │   ├── state.py        # SQLite-backed state manager (deduplication)
│   │   └── task.py         # Abstract base task interface
│   ├── services/
│   │   ├── email.py        # SMTP email dispatch service
│   │   └── llm.py          # Google Gemini AI wrapper
│   └── tasks/
│       ├── cold_email.py   # LLM-generated personalized email task
│       └── static_email.py # Template-based static email task
├── data/
│   └── leads.xlsx          # Your leads file (Excel or CSV)
├── main.py                 # CLI entrypoint
├── requirements.txt
└── .env                    # API keys & SMTP config (not committed)
```

| Layer | Files | Responsibility |
|-------|-------|----------------|
| **Core** | `engine.py`, `state.py`, `task.py` | Retry logic, state caching, abstract task interface |
| **Services** | `llm.py`, `email.py` | Google Gemini API, SMTP dispatch |
| **Tasks** | `cold_email.py`, `static_email.py` | Business logic — reading leads, personalizing, sending |

---

## ⚙️ Setup

### 1. Prerequisites

- Python 3.9+
- An SMTP-enabled Gmail account (or any SMTP server)
- [Google Gemini API key](https://aistudio.google.com/) *(for LLM-based emails)*

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Google Gemini AI (for LLM-based email task)
GEMINI_API_KEY=your_gemini_api_key
```

> **Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your account password.

### 4. Prepare Your Leads File

Create `data/leads.xlsx` (or `.csv`) with columns like:

| Name | Email | Company | Role |
|------|-------|---------|------|
| Lochan | Lochan@acme.com | Acme Corp | Engineering Manager |
| Yash  | Yash@startup.io | StartupIO | CTO |

---

## 🖥️ Usage

### Safe Test (Dry Run — Default)

Runs the entire pipeline locally and logs what would be sent — **no real emails**:

```bash
python main.py
```

### Send Real Emails

```bash
python main.py --send-real
```

### Custom Leads File

```bash
python main.py --send-real --leads data/my_leads.csv
```

### With Resume Attachment

```bash
python main.py --send-real --attachment path/to/resume.pdf
```

### Force Re-send to All Leads (Ignore State)

```bash
python main.py --send-real --force
```

### All Options

```
usage: main.py [-h] [--dry-run] [--send-real] [--leads LEADS] [--attachment ATTACHMENT] [--force]

optional arguments:
  --dry-run             Log emails without sending (default: ON)
  --send-real           Send real emails via SMTP
  --leads LEADS         Path to leads file (.xlsx or .csv) [default: data/leads.xlsx]
  --attachment FILE     Optional file attachment (e.g. resume.pdf)
  --force               Ignore existing state and re-send to all leads
```

---

## 🔧 Email Personalization

In `main.py`, customize your subject and body using `{ColumnName}` placeholders that map to your spreadsheet columns:

```python
subject = "Application for Software Engineer - Your Name"

body = """Hello {Name},

I am writing to apply for the Software Engineer position at {Company}...

Warm regards,
Your Name"""
```

Any column from your Excel/CSV file can be used as a placeholder.

---

## 🛡️ How Deduplication Works

The `StateManager` records every successfully sent email in a local SQLite database (`state.db`). On subsequent runs, the `TaskEngine` automatically skips leads that have already been processed — ensuring no recipient ever gets duplicate emails.

```
Lead loaded → Check state.db → Already sent? Skip : Send → Record in state.db
```

Use `--force` to bypass this and re-process all leads.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `pandas` | Reading Excel/CSV lead files |
| `python-dotenv` | Loading `.env` configuration |
| `google-genai` | Google Gemini AI for LLM email generation |
| `pydantic` | Data validation |
| `pyodbc` | Optional SQL Server state backend |

---

## 🔒 Security

- Use Gmail **App Passwords** instead of your main password
- The `state.db` file contains sent-email records — keep it local

---

## 👤 Author

**Lochan Patel**
- GitHub: [@Lochanpatel](https://github.com/Lochanpatel)
- LeetCode: [lochanpatelmp](https://leetcode.com/u/lochanpatelmp/)
- Email: patellochan31@gmail.com

---

## 📄 License

This project is open-source and available for personal and educational use.
