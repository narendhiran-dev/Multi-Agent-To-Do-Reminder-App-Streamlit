# agents/planner_agent.py
from .base_agent import BaseAgent
from typing import Dict, Any, Optional
import re
from datetime import datetime, timedelta

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("PlannerAgent")

    def process(self, raw_task_input: str, **kwargs) -> Optional[Dict[str, Any]]:
        self.log(f"Received raw input: '{raw_task_input}'")
        
        if not raw_task_input or not raw_task_input.strip():
            self.log("Input is empty. No task planned.")
            return None

        description = raw_task_input.strip()
        
        # Basic reasoning: Check for similar existing tasks (simple check)
        existing_tasks = self.db_manager.get_all_tasks()
        for task in existing_tasks:
            if task['status'] != 'completed' and description.lower() in task['description'].lower():
                self.log(f"Found a similar existing task: ID {task['id']} - '{task['description']}'. Consider reviewing.")
                # For now, we still proceed, but this is where more complex logic could go.

        # Basic NLP: Try to extract due date (very simple)
        # Examples: "buy milk tomorrow", "finish report by next friday", "call mom on 2023-12-25"
        due_date = None
        due_date_str = None

        # Check for "tomorrow"
        if "tomorrow" in description.lower():
            due_date = datetime.now() + timedelta(days=1)
            description = re.sub(r'\s*tomorrow\s*', '', description, flags=re.IGNORECASE).strip()
            due_date_str = due_date.strftime('%Y-%m-%d %H:%M:%S')
            self.log(f"Inferred due date: tomorrow ({due_date_str})")

        # Check for "next Xday" (e.g., next monday)
        match_next_day = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', description.lower())
        if match_next_day:
            day_name = match_next_day.group(1)
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            target_day_index = days.index(day_name)
            today_index = datetime.now().weekday()
            days_to_add = (target_day_index - today_index + 7) % 7
            if days_to_add == 0: # if "next monday" and today is monday, it means next week's monday
                days_to_add = 7
            due_date = datetime.now() + timedelta(days=days_to_add)
            description = re.sub(r'next\s+' + day_name, '', description, flags=re.IGNORECASE).strip()
            due_date_str = due_date.strftime('%Y-%m-%d %H:%M:%S') # Keep time for now, can be refined
            self.log(f"Inferred due date: next {day_name} ({due_date_str})")
        
        # Check for specific date "on YYYY-MM-DD" or "by YYYY-MM-DD"
        match_date = re.search(r'(by|on)\s+(\d{4}-\d{2}-\d{2})', description.lower())
        if match_date:
            try:
                date_str = match_date.group(2)
                due_date = datetime.strptime(date_str, '%Y-%m-%d')
                # Set time to end of day for "by" or a default time
                due_date = due_date.replace(hour=17, minute=0, second=0) 
                description = re.sub(r'(by|on)\s+' + date_str, '', description, flags=re.IGNORECASE).strip()
                due_date_str = due_date.strftime('%Y-%m-%d %H:%M:%S')
                self.log(f"Inferred due date: {date_str} ({due_date_str})")
            except ValueError:
                self.log(f"Could not parse date: {match_date.group(2)}")


        planned_task = {
            "description": description,
            "status": "pending_scheduling", # A temporary status
            "due_date": due_date_str,
            "priority": 2, # Default priority
            "agent_notes": f"Planned by PlannerAgent. Original input: '{raw_task_input}'"
        }
        self.log(f"Planned task: {planned_task['description']}" + (f", Due: {planned_task['due_date']}" if planned_task['due_date'] else ""))
        return planned_task