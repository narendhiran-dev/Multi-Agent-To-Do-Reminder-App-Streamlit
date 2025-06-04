# agents/reminder_agent.py
from .base_agent import BaseAgent
from typing import List, Dict, Any
from datetime import datetime

class ReminderAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReminderAgent")
        self.reminders_sent_this_session = [] # Simple way to show reminders in UI

    def process(self, **kwargs) -> List[str]:
        self.log("Checking for tasks needing reminders...")
        self.reminders_sent_this_session.clear() # Clear for this run

        tasks_to_remind = self.db_manager.get_tasks_for_reminder()
        
        if not tasks_to_remind:
            self.log("No tasks currently need reminders.")
            return []

        now = datetime.now()
        for task in tasks_to_remind:
            task_id = task['id']
            description = task['description']
            due_date_str = task['due_date']
            
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S') if due_date_str else None

            reminder_message = ""
            if due_date:
                if due_date < now:
                    time_diff = now - due_date
                    reminder_message = f"REMINDER: Task '{description}' (ID: {task_id}) is OVERDUE by {time_diff.days} days, {time_diff.seconds//3600} hours."
                else:
                    time_diff = due_date - now
                    if time_diff.days < 1 and time_diff.seconds//3600 < 24: # Due within 24 hours
                         reminder_message = f"REMINDER: Task '{description}' (ID: {task_id}) is due in {time_diff.seconds//3600} hours, {(time_diff.seconds//60)%60} minutes (at {due_date.strftime('%H:%M')})."
                    else: # Due further out but within reminder window (e.g. next day)
                         reminder_message = f"REMINDER: Task '{description}' (ID: {task_id}) is due on {due_date.strftime('%Y-%m-%d at %H:%M')}."
            else: # Should not happen with current DB query but as a fallback
                reminder_message = f"REMINDER: Task '{description}' (ID: {task_id}) is pending and has no due date."

            if reminder_message:
                self.log(reminder_message)
                self.reminders_sent_this_session.append(reminder_message)
                # Update task to mark reminder as sent
                self.db_manager.update_task(task_id, {"reminder_sent_at": now.strftime('%Y-%m-%d %H:%M:%S')})
        
        return self.reminders_sent_this_session