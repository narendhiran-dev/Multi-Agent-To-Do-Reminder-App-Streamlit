# agents/scheduler_agent.py
from .base_agent import BaseAgent
from typing import Dict, Any, Optional
from datetime import datetime

class SchedulerAgent(BaseAgent):
    def __init__(self):
        super().__init__("SchedulerAgent")

    def process(self, planned_task: Dict[str, Any], **kwargs) -> Optional[int]:
        self.log(f"Received planned task: {planned_task['description']}")

        if not planned_task:
            self.log("No planned task received. Cannot schedule.")
            return None

        # Reasoning: Validate or set due_date
        due_date_str = planned_task.get("due_date")
        final_due_date = None
        if due_date_str:
            try:
                # Ensure it's a valid datetime object if passed as string
                if isinstance(due_date_str, str):
                    final_due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S')
                elif isinstance(due_date_str, datetime): # Should not happen from Planner currently
                    final_due_date = due_date_str
                
                # Basic reasoning: if due_date is in the past for a new task, flag it or adjust
                if final_due_date and final_due_date < datetime.now():
                    self.log(f"Warning: Suggested due date '{final_due_date.strftime('%Y-%m-%d %H:%M:%S')}' is in the past. Setting to None for now.")
                    # In a real app, might ask user or set to today + 1 day
                    final_due_date = None 
            except ValueError:
                self.log(f"Invalid due date format: {due_date_str}. Scheduling without a due date.")
                final_due_date = None
        
        # If no due_date, UI will prompt or it remains None.
        # For this agent, we'll proceed if user provides it via UI later or explicitly wants no due date.

        task_to_schedule = {
            "description": planned_task["description"],
            "status": "pending", # Official status for new tasks
            "due_date": final_due_date.strftime('%Y-%m-%d %H:%M:%S') if final_due_date else None,
            "priority": planned_task.get("priority", 2),
            "assigned_agent": self.name,
            "agent_notes": planned_task.get("agent_notes", "") + f"\nScheduled by SchedulerAgent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        }

        try:
            task_id = self.db_manager.add_task(task_to_schedule)
            self.log(f"Task '{task_to_schedule['description']}' (ID: {task_id}) successfully scheduled and stored.")
            return task_id
        except Exception as e:
            self.log(f"Error scheduling task: {e}")
            return None