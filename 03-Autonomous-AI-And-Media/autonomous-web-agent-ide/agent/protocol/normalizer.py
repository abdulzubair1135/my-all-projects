import os
import re
from typing import Dict, Any

class ActionNormalizer:
    @staticmethod
    def normalize_action(action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes action dictionary before validation and execution:
        - Normalizes slashes in paths
        - Strips leading drive letters or slashes
        - Strips whitespace in commands
        """
        norm = action.copy()
        
        if "path" in norm and isinstance(norm["path"], str):
            # Normalize path slashes to forward slashes for cross-platform consistency
            cleaned_path = norm["path"].strip().replace("\\", "/")
            # Remove leading slashes to ensure it's treated as relative
            cleaned_path = re.sub(r"^/+", "", cleaned_path)
            norm["path"] = cleaned_path

        if "command" in norm and isinstance(norm["command"], str):
            norm["command"] = norm["command"].strip()

        return norm
