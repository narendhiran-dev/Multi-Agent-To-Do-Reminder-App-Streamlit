# main.py
import subprocess
import os

if __name__ == "__main__":
    # Ensure tasks.db exists (db_manager will create table if not exists)
    # from database.db_manager import DatabaseManager # This line would initialize it
    # db = DatabaseManager() # Call to ensure table creation on first run
    
    print("Starting Streamlit To-Do App...")
    # Construct the path to app.py relative to main.py
    app_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")
    subprocess.run(["streamlit", "run", app_path])