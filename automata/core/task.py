from abc import ABC, abstractmethod
from typing import Any, Dict

class Task(ABC):
    """Base class for any automation task."""
    
    @property
    @abstractmethod
    def task_id(self) -> str:
        """Unique identifier for the task."""
        pass

    @abstractmethod
    def process_item(self, item: Any) -> Any:
        """Process a single item. Should raise exceptions on failure."""
        pass
