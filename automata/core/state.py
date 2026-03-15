import sqlite3
import json
from datetime import datetime
import os
from typing import Any, Dict, Optional

class StateManager:
    """Manages the execution state of tasks to allow retries and prevent duplicates."""
    
    def __init__(self, db_path: str = "state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_state (
                    task_id TEXT,
                    item_id TEXT,
                    status TEXT,
                    result TEXT,
                    error TEXT,
                    updated_at TEXT,
                    PRIMARY KEY (task_id, item_id)
                )
            ''')
            conn.commit()

    def update_state(self, task_id: str, item_id: str, status: str, result: Any = None, error: Any = None) -> None:
        """Updates the state of a specific item in a task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # SQLite UPSERT syntax
            cursor.execute('''
                INSERT INTO task_state (task_id, item_id, status, result, error, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id, item_id) 
                DO UPDATE SET 
                    status=excluded.status, 
                    result=excluded.result, 
                    error=excluded.error, 
                    updated_at=excluded.updated_at
            ''', (
                task_id,
                item_id,
                status,
                json.dumps(result) if result else None,
                str(error) if error else None,
                datetime.utcnow().isoformat()
            ))
            conn.commit()

    def get_state(self, task_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the current state of a task item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT status, result, error, updated_at
                FROM task_state
                WHERE task_id = ? AND item_id = ?
            ''', (task_id, item_id))
            row = cursor.fetchone()
            
            if row:
                return {
                    "status": row[0],
                    "result": json.loads(row[1]) if row[1] else None,
                    "error": row[2],
                    "updated_at": row[3]
                }
            return None
