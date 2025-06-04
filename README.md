# Multi-Agent To-Do & Reminder App

This project is a smart to-do list application built with Python, Streamlit, and SQLite, featuring a multi-agent system for task handling.

## Features

* **Task Management:** Add, view, edit, complete, and delete tasks.
* **Multi-Agent System:**
  * **Planner Agent:** Takes raw user input and attempts to structure it into a task, including inferring due dates from natural language (e.g., "tomorrow", "next Friday").
  * **Scheduler Agent:** Finalizes task details (due date, priority) and saves the task to the database.
  * **Reminder Agent:** Periodically checks for upcoming or overdue tasks and displays reminders.
* **Memory & Reasoning:**
  * Agents use the SQLite database as shared memory.
  * Planner Agent has basic NLP to parse due dates.
  * Scheduler Agent can validate due dates (e.g., not in the past for new tasks).
  * Reminder Agent reasons about when to send reminders (upcoming, overdue, avoid spamming).
* **Persistent Storage:** Tasks are stored in an SQLite database (`tasks.db`).
* **User Interface (Streamlit):**
  * Clean UI for managing tasks.
  * Input form for new tasks.
  * Filtering tasks by status.
  * Agent Log view to see agent activities.
  * Reminder notifications.

## Technology Stack

* **Backend Logic & Agents:** Python
* **Frontend UI:** Streamlit
* **Database:** SQLite
* **Key Python Libraries:** `streamlit`, `sqlite3`, `datetime`

## Project Structure


    **multi_agent_todo/**
├── agents/ # Agent implementations
│ ├── **init**.py
│ ├── base_agent.py
│ ├── planner_agent.py
│ ├── scheduler_agent.py
│ └── reminder_agent.py
├── database/ # Database management
│ ├── **init**.py
│ └── db_manager.py
├── ui/ # Streamlit UI application
│ ├── **init**.py
│ └── app.py
├── utils/ # Utility modules like logger
│ ├── **init**.py
│ └── logger.py
├── tasks.db # SQLite database file (created on run)
└── README.md

<pre _ngcontent-ng-c3155711068=""><br class="Apple-interchange-newline"/>

</pre>


## Setup and Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd multi_agent_todo
   ```
2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**

   ```bash
   pip install streamlit
   # No other external dependencies for this basic version
   ```

## How to Run

Navigate to the project's root directory (`multi_agent_todo/`) in your terminal and run:

```bash
streamlit run ui/app.py
```


---
This comprehensive setup provides a solid foundation for your Multi-Agent To-Do & Reminder App. You can now proceed to create the files, copy the code, and test it out! Remember to create empty `__init__.py` files in the `agents`, `database`, `ui`, and `utils` directories.
---
