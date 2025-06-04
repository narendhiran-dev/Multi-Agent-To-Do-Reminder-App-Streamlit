# database/db_manager.py
import sqlite3
import datetime
from typing import List, Dict, Any, Optional

DATABASE_NAME = 'tasks.db'

class DatabaseManager:
    def __init__(self, db_name=DATABASE_NAME):
        self.db_name = db_name
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                priority INTEGER DEFAULT 2, -- 1:High, 2:Medium, 3:Low
                assigned_agent TEXT,
                agent_notes TEXT,
                reminder_sent_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def add_task(self, task_data: Dict[str, Any]) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (description, status, due_date, priority, assigned_agent, agent_notes)
            VALUES (:description, :status, :due_date, :priority, :assigned_agent, :agent_notes)
        ''', task_data)
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        conn.close()
        return dict(task) if task else None

    def get_all_tasks(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM tasks"
        params = []
        if status_filter and status_filter != "all":
            query += " WHERE status = ?"
            params.append(status_filter)
        query += " ORDER BY due_date ASC, priority ASC, created_at ASC"
        
        cursor.execute(query, params)
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def update_task(self, task_id: int, updates: Dict[str, Any]):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        set_clauses = []
        values = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        if not set_clauses:
            return # No updates to make

        query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
        values.append(task_id)
        
        cursor.execute(query, tuple(values))
        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def get_tasks_for_reminder(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Remind for tasks due in the next 24 hours or overdue, not completed,
        # and not reminded in the last 6 hours (to avoid spam)
        # For simplicity, we'll just check if reminder_sent_at is NULL or more than 6 hours ago
        now = datetime.datetime.now()
        reminder_threshold_time = now - datetime.timedelta(hours=6)
        
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE status != 'completed' 
            AND due_date IS NOT NULL
            AND (
                (due_date <= ?) OR -- Overdue or due within next day
                (JULIANDAY(due_date) - JULIANDAY('now', 'localtime')) <= 1 
            )
            AND (reminder_sent_at IS NULL OR reminder_sent_at < ?)
            ORDER BY due_date ASC
        """, (now.strftime('%Y-%m-%d %H:%M:%S'), reminder_threshold_time.strftime('%Y-%m-%d %H:%M:%S')))
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

# Global instance
db_manager = DatabaseManager()