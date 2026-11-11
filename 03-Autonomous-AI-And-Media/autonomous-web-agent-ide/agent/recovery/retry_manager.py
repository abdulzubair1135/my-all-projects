from typing import Optional

class RetryManager:
    def __init__(self, max_retries_per_task: int = 4):
        self.max_retries_per_task = max_retries_per_task

    def should_retry(self, current_retry_count: int) -> bool:
        return current_retry_count < self.max_retries_per_task

    def get_strategy_for_attempt(self, attempt: int) -> str:
        if attempt == 1:
            return "direct_fix"
        elif attempt == 2:
            return "clean_reinstall_dependencies"
        elif attempt == 3:
            return "architectural_refactor"
        else:
            return "pause_and_ask_user"
