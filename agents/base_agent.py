# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Any # <--- ADD THIS LINE
from utils.logger import agent_logger
from database.db_manager import db_manager

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = agent_logger
        self.db_manager = db_manager

    @abstractmethod
    def process(self, data: Any, **kwargs) -> Any: # Now 'Any' is defined
        pass

    def log(self, message: str):
        self.logger.log(self.name, message)