# ui/app.py
import sys
import os


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# Now your project-specific imports should work
from database.db_manager import db_manager
from agents.planner_agent import PlannerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.reminder_agent import ReminderAgent
from utils.logger import agent_logger

import streamlit as st # Keep other imports after the sys.path modification
from datetime import datetime, time

# Initialize agents
planner = PlannerAgent()
scheduler = SchedulerAgent()
reminder = ReminderAgent()

# --- Helper Functions ---
def format_datetime_for_display(dt_str):
    if not dt_str:
        return "N/A"
    try:
        dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return dt_obj.strftime('%Y-%m-%d %I:%M %p')
    except (ValueError, TypeError):
        return "Invalid Date"

def priority_to_text(p_int):
    return {1: "High", 2: "Medium", 3: "Low"}.get(p_int, "Unknown")

def text_to_priority(p_text):
    return {"High": 1, "Medium": 2, "Low": 3}.get(p_text, 2)


# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🧠 Multi-Agent To-Do & Reminder App")

# --- Session State Initialization ---
if 'editing_task_id' not in st.session_state:
    st.session_state.editing_task_id = None
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'status_filter' not in st.session_state:
    st.session_state.status_filter = "pending" # Default filter

# --- Sidebar for Agent Log and Controls ---
with st.sidebar:
    st.header("Agent Controls & Log")
    if st.button("🔄 Check for Reminders"):
        with st.spinner("Reminder Agent processing..."):
            reminders_fired = reminder.process()
            st.session_state.reminders.extend(reminders_fired) # Append new reminders
            if reminders_fired:
                st.success(f"{len(reminders_fired)} reminder(s) processed.")
            else:
                st.info("No new reminders.")
        st.rerun() # Rerun to update reminder display

    st.subheader("Agent Log")
    log_container = st.container(height=300)
    for entry in reversed(agent_logger.get_logs()): # Show newest first
        log_container.text(entry)
    
    if st.button("Clear Agent Log (Session Only)"):
        agent_logger.clear_logs()
        st.rerun()

# --- Display Reminders ---
if st.session_state.reminders:
    st.subheader("🔔 Active Reminders")
    for rem_msg in st.session_state.reminders:
        st.warning(rem_msg)
    if st.button("Dismiss All Reminders"):
        st.session_state.reminders = []
        st.rerun()
    st.markdown("---")


# --- Task Input Form ---
st.header("➕ Add New Task")
with st.form("new_task_form", clear_on_submit=True):
    raw_task_input = st.text_input("Describe your task (e.g., 'Buy groceries tomorrow', 'Prepare presentation by next Friday 5pm'):")
    
    # These fields will be populated/confirmed after PlannerAgent
    # but we can allow user to provide them upfront if SchedulerAgent needs them
    col1, col2 = st.columns(2)
    with col1:
        user_due_date = st.date_input("Due Date (Optional, Planner might infer)", value=None)
    with col2:
        user_due_time = st.time_input("Due Time (Optional)", value=time(17,0)) # Default 5 PM

    user_priority_text = st.selectbox("Priority (Optional)", ["Medium", "High", "Low"], index=0)
    
    submit_button = st.form_submit_button("Process & Add Task")

if submit_button and raw_task_input:
    with st.spinner("Agents at work..."):
        # 1. Planner Agent
        planned_task = planner.process(raw_task_input)

        if planned_task:
            # Allow user to override/confirm Planner's inferences or provide missing info
            # If Planner inferred a due date, use it, otherwise use user's input
            if planned_task.get("due_date"):
                try:
                    inferred_dt = datetime.strptime(planned_task["due_date"], '%Y-%m-%d %H:%M:%S')
                    final_due_date = inferred_dt.date()
                    final_due_time = inferred_dt.time()
                except (ValueError, TypeError): # If parsing fails, fall back to user input
                    final_due_date = user_due_date
                    final_due_time = user_due_time
            else: # Planner didn't infer, use user input
                final_due_date = user_due_date
                final_due_time = user_due_time
            
            # Combine date and time if both are provided
            if final_due_date and final_due_time:
                combined_datetime = datetime.combine(final_due_date, final_due_time)
                planned_task["due_date"] = combined_datetime.strftime('%Y-%m-%d %H:%M:%S')
            elif final_due_date: # Only date provided
                combined_datetime = datetime.combine(final_due_date, time(0,0)) # Midnight
                planned_task["due_date"] = combined_datetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                planned_task["due_date"] = None # No due date

            planned_task["priority"] = text_to_priority(user_priority_text)
            
            # 2. Scheduler Agent
            task_id = scheduler.process(planned_task)
            if task_id:
                st.success(f"Task '{planned_task['description']}' added with ID: {task_id}!")
            else:
                st.error("Scheduler Agent failed to add the task.")
        else:
            st.warning("Planner Agent could not create a task from the input.")
    st.rerun() # Refresh the task list

# --- Task Display and Management ---
st.header("📋 My Tasks")

status_options = ["all", "pending", "in progress", "completed"]
# Use the session state for the selected filter
current_filter_index = status_options.index(st.session_state.status_filter) if st.session_state.status_filter in status_options else 0
selected_status = st.selectbox("Filter by status:", status_options, index=current_filter_index)

# Update session state if filter changes
if selected_status != st.session_state.status_filter:
    st.session_state.status_filter = selected_status
    st.rerun()


tasks = db_manager.get_all_tasks(status_filter=st.session_state.status_filter)

if not tasks:
    st.info(f"No tasks found with status '{st.session_state.status_filter}'. Try a different filter or add new tasks!")
else:
    for task in tasks:
        task_id = task['id']
        with st.expander(f"**{task['description']}** (Due: {format_datetime_for_display(task['due_date'])}) - P: {priority_to_text(task['priority'])} - S: {task['status'].capitalize()}"):
            st.caption(f"Task ID: {task_id} | Created: {format_datetime_for_display(task['created_at'])}")
            if task['agent_notes']:
                st.markdown("**Agent Notes:**")
                st.text(task['agent_notes'])
            
            if task.get('reminder_sent_at'):
                st.caption(f"Last Reminder Sent: {format_datetime_for_display(task['reminder_sent_at'])}")


            # Edit form within the expander
            if st.session_state.editing_task_id == task_id:
                with st.form(key=f"edit_form_{task_id}"):
                    st.subheader(f"Edit Task: {task['description'][:30]}...")
                    new_description = st.text_input("Description", value=task['description'])
                    
                    current_due_dt = None
                    if task['due_date']:
                        current_due_dt = datetime.strptime(task['due_date'], '%Y-%m-%d %H:%M:%S')
                    
                    edit_col1, edit_col2 = st.columns(2)
                    with edit_col1:
                        new_due_date = st.date_input("New Due Date", value=current_due_dt.date() if current_due_dt else None, key=f"date_{task_id}")
                    with edit_col2:
                        new_due_time = st.time_input("New Due Time", value=current_due_dt.time() if current_due_dt else time(17,0), key=f"time_{task_id}")

                    new_priority_text = st.selectbox("New Priority", ["High", "Medium", "Low"], 
                                                     index=["High", "Medium", "Low"].index(priority_to_text(task['priority'])),
                                                     key=f"prio_{task_id}")
                    new_status = st.selectbox("New Status", ["pending", "in progress", "completed"], 
                                              index=["pending", "in progress", "completed"].index(task['status']),
                                              key=f"stat_{task_id}")

                    save_changes = st.form_submit_button("💾 Save Changes")
                    cancel_edit = st.form_submit_button("❌ Cancel")

                    if save_changes:
                        updates = {
                            "description": new_description,
                            "priority": text_to_priority(new_priority_text),
                            "status": new_status
                        }
                        if new_due_date and new_due_time:
                            updates["due_date"] = datetime.combine(new_due_date, new_due_time).strftime('%Y-%m-%d %H:%M:%S')
                        elif new_due_date: # Only date
                             updates["due_date"] = datetime.combine(new_due_date, time(0,0)).strftime('%Y-%m-%d %H:%M:%S')
                        else: # No due date
                            updates["due_date"] = None
                        
                        db_manager.update_task(task_id, updates)
                        agent_logger.log("UserInterface", f"Task ID {task_id} updated by user.")
                        st.session_state.editing_task_id = None
                        st.success("Task updated!")
                        st.rerun()
                    if cancel_edit:
                        st.session_state.editing_task_id = None
                        st.rerun()
            else: # Display mode for task
                cols = st.columns(4)
                if cols[0].button("✏️ Edit", key=f"edit_{task_id}"):
                    st.session_state.editing_task_id = task_id
                    st.rerun()
                
                if task['status'] != 'completed':
                    if cols[1].button("✅ Mark Complete", key=f"complete_{task_id}"):
                        db_manager.update_task(task_id, {"status": "completed"})
                        agent_logger.log("UserInterface", f"Task ID {task_id} marked as 'completed' by user.")
                        st.rerun()
                else:
                    if cols[1].button("↩️ Mark Pending", key=f"uncomplete_{task_id}"): # Option to un-complete
                        db_manager.update_task(task_id, {"status": "pending"})
                        agent_logger.log("UserInterface", f"Task ID {task_id} marked as 'pending' by user.")
                        st.rerun()

                if cols[2].button("🗑️ Delete", key=f"delete_{task_id}"):
                    db_manager.delete_task(task_id)
                    agent_logger.log("UserInterface", f"Task ID {task_id} deleted by user.")
                    st.rerun()

# --- Final Touches ---
st.markdown("---")
st.caption("Built with Streamlit and Multiple Agents.")