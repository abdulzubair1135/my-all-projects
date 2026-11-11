import re
from typing import Dict, Any, Optional

class ErrorAnalyzer:
    @staticmethod
    def analyze_command_failure(command: str, exit_code: int, stdout: str, stderr: str) -> Dict[str, Any]:
        """
        Analyzes output and extracts clean, structured failure information.
        """
        raw_error = (stderr or stdout or "Unknown error").strip()
        
        # Detect common error categories
        category = "runtime_error"
        if "Cannot find module" in raw_error or "ModuleNotFoundError" in raw_error or "npm ERR! code ENOENT" in raw_error:
            category = "missing_dependency"
        elif "SyntaxError" in raw_error or "Unexpected token" in raw_error:
            category = "syntax_error"
        elif "EADDRINUSE" in raw_error or "address already in use" in raw_error:
            category = "port_conflict"
        elif "TypeError" in raw_error or "ReferenceError" in raw_error:
            category = "type_or_reference_error"
        elif "AssertionError" in raw_error or "failed" in raw_error.lower():
            category = "test_failure"

        # Extract last 15 lines of stack trace
        lines = raw_error.split("\n")
        concise_trace = "\n".join(lines[-15:])

        return {
            "type": "execution_error",
            "category": category,
            "command": command,
            "exit_code": exit_code,
            "error_snippet": concise_trace,
            "full_stderr": stderr[:4000],
            "full_stdout": stdout[:2000]
        }
