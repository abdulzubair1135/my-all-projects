import hashlib
import re
from typing import Dict

class LoopDetector:
    def __init__(self, max_same_error: int = 3, max_total_iterations: int = 30):
        self.max_same_error = max_same_error
        self.max_total_iterations = max_total_iterations
        self.total_iterations = 0
        self.error_fingerprints: Dict[str, int] = {}

    def compute_fingerprint(self, command: str, exit_code: int, error_text: str) -> str:
        # Normalize error text (remove timestamps, line numbers, temporary hashes)
        norm_text = re.sub(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}", "", error_text)
        norm_text = re.sub(r":\d+:\d+", "", norm_text)
        norm_text = re.sub(r"0x[0-9a-fA-F]+", "", norm_text)
        norm_text = norm_text.strip()[:500]

        raw = f"{command}:{exit_code}:{norm_text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record_iteration(self) -> bool:
        """
        Increments iteration count. Returns False if max iterations exceeded.
        """
        self.total_iterations += 1
        return self.total_iterations <= self.max_total_iterations

    def record_error(self, command: str, exit_code: int, error_text: str) -> bool:
        """
        Records an error fingerprint.
        Returns False if the same error has occurred >= max_same_error times (infinite loop detected).
        """
        fp = self.compute_fingerprint(command, exit_code, error_text)
        count = self.error_fingerprints.get(fp, 0) + 1
        self.error_fingerprints[fp] = count

        return count < self.max_same_error
