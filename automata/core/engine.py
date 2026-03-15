import logging
import time
from typing import List, Callable, Any, Dict
from automata.core.state import StateManager

logger = logging.getLogger(__name__)

class TaskEngine:
    """Engine responsible for running items through tasks with automatic retries and state management."""
    
    def __init__(self, state_manager: StateManager):
        self.state = state_manager

    def run_item(self, task_id: str, item_id: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Runs a single item, checking its state first to avoid redundant work."""
        current_state = self.state.get_state(task_id, item_id)
        
        # If successfully processed earlier, skip to avoid duplicates (e.g. sending emails twice)
        if current_state and current_state["status"] == "COMPLETED":
            logger.info(f"[{task_id}] Item {item_id} already completed. Skipping.")
            return {"status": "SKIPPED", "result": current_state.get("result")}

        max_retries = kwargs.pop("max_retries", 3)
        retry_delay = kwargs.pop("retry_delay", 2.0)

        for attempt in range(max_retries):
            try:
                self.state.update_state(task_id, item_id, "PROCESSING")
                result = func(*args, **kwargs)
                self.state.update_state(task_id, item_id, "COMPLETED", result=result)
                logger.info(f"[{task_id}] Item {item_id} successfully COMPLETED.")
                return {"status": "COMPLETED", "result": result}
            except Exception as e:
                logger.warning(f"[{task_id}] Item {item_id} attempt {attempt + 1} failed: {e}")
                self.state.update_state(task_id, item_id, "FAILED", error=str(e))
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"[{task_id}] Item {item_id} permanently FAILED after {max_retries} attempts.")
                    return {"status": "FAILED", "error": str(e)}
        
        return {"status": "FAILED", "error": "Exceeded max retries"}

    def run_batch(self, task_id: str, items: List[Any], process_func: Callable, id_extractor: Callable, **kwargs) -> Dict[str, int]:
        """Runs a batch of items and returns execution statistics."""
        stats = {"COMPLETED": 0, "SKIPPED": 0, "FAILED": 0}
        for item in items:
            item_id = id_extractor(item)
            res = self.run_item(task_id, item_id, process_func, item, **kwargs)
            # Make sure we safely get the status to increment the counter
            status = res.get("status", "FAILED")
            stats[status] = stats.get(status, 0) + 1
        return stats
