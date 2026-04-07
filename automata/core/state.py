import pyodbc
import json
from datetime import datetime
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """Manages execution state using SQL Server to allow retries and prevent duplicates."""

    def __init__(self, server: str = r"SAMSUNG\sqlexpress", database: str = "AutomataState"):
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
        self._init_db()

    def _get_conn(self):
        return pyodbc.connect(self.connection_string)

    def _init_db(self) -> None:
        """Creates the database and task_state table if they do not exist."""
        # Connect to master first to create the database if needed
        master_conn_str = self.connection_string.replace(
            "DATABASE=AutomataState", "DATABASE=master"
        )
        try:
            with pyodbc.connect(master_conn_str, autocommit=True) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'AutomataState')
                    CREATE DATABASE AutomataState
                """)
            logger.info("AutomataState database is ready.")
        except Exception as e:
            logger.warning(f"Could not ensure database exists (may already exist): {e}")

        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    IF NOT EXISTS (
                        SELECT * FROM sysobjects WHERE name='task_state' AND xtype='U'
                    )
                    CREATE TABLE task_state (
                        task_id     NVARCHAR(255)  NOT NULL,
                        item_id     NVARCHAR(500)  NOT NULL,
                        status      NVARCHAR(50)   NOT NULL,
                        result      NVARCHAR(MAX)  NULL,
                        error       NVARCHAR(MAX)  NULL,
                        updated_at  NVARCHAR(50)   NOT NULL,
                        PRIMARY KEY (task_id, item_id)
                    )
                """)
                conn.commit()
            logger.info("task_state table is ready.")
        except Exception as e:
            logger.error(f"Failed to initialize task_state table: {e}")
            raise

    def update_state(self, task_id: str, item_id: str, status: str, result: Any = None, error: Any = None) -> None:
        """Upserts the state of a specific item in a task."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                MERGE task_state AS target
                USING (SELECT ? AS task_id, ? AS item_id) AS source
                ON target.task_id = source.task_id AND target.item_id = source.item_id
                WHEN MATCHED THEN
                    UPDATE SET status=?, result=?, error=?, updated_at=?
                WHEN NOT MATCHED THEN
                    INSERT (task_id, item_id, status, result, error, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?);
            """,
                task_id, item_id,
                status, json.dumps(result) if result else None, str(error) if error else None,
                datetime.utcnow().isoformat(),
                task_id, item_id, status,
                json.dumps(result) if result else None, str(error) if error else None,
                datetime.utcnow().isoformat()
            )
            conn.commit()

    def get_state(self, task_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the current state of a task item."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, result, error, updated_at
                FROM task_state
                WHERE task_id = ? AND item_id = ?
            """, task_id, item_id)
            row = cursor.fetchone()

            if row:
                return {
                    "status": row[0],
                    "result": json.loads(row[1]) if row[1] else None,
                    "error": row[2],
                    "updated_at": row[3]
                }
            return None
