# utils/logger.py
import datetime

class AgentLog:
    _instance = None
    log_entries = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentLog, cls).__new__(cls)
            cls._instance.log_entries = []
        return cls._instance

    def log(self, agent_name: str, message: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{agent_name}]: {message}"
        self.log_entries.append(entry)
        print(entry) # Also print to console for debugging

    def get_logs(self):
        return self.log_entries

    def clear_logs(self): # For demo purposes, might want to persist logs differently in prod
        self.log_entries = []

# Global instance
agent_logger = AgentLog()